import os
import json

import sys
import time
import timeout_decorator

import requests
import redis

from collections import defaultdict
from flask import Blueprint, jsonify, request, url_for, make_response, abort

from flask_cors import cross_origin
from sqlalchemy.exc import DatabaseError

from py_zipkin.zipkin import zipkin_span, ZipkinAttrs
deals = Blueprint('deals', __name__)

from main import db
from main import mqpool

from main import dealsmodel
from main import searchqueue

PORT = int(os.getenv('PORT', '9013'))
ZIPKINURI = os.getenv('ZIPKINURI', 'http://zipkin:9411')
ZIPKINSAMPLERATE = float(os.getenv('ZIPKINSAMPLERATE', 100.0))
DEBUG = int(os.getenv('DEBUG', '0'))

@deals.errorhandler(400)
def not_found(error):
  return make_response(jsonify( { 'error': 'Bad request' }), 400)

@deals.errorhandler(404)
def not_found(error):
  return make_response(jsonify( { 'error': 'Not found' }), 404)

def http_transport(encoded_span):
  # The collector expects a thrift-encoded list of spans.
  requests.post(ZIPKINURI + '/api/v1/spans', data=encoded_span, headers={'Content-Type': 'application/x-thrift'})

def debugmessage(position, message):
  if DEBUG == 1:
    print position
    print message 

    sys.stdout.flush() 

@zipkin_span(service_name='hotels.com:dealsquery', span_name='dealquery:getdeals')  
def getdeals(sessionid):
  query = dealsmodel.query.join(searchqueue, dealsmodel.hotelid == searchqueue.hotelid).add_columns(dealsmodel.id, dealsmodel.agency, 
   dealsmodel.hotelid, dealsmodel.roomtype, dealsmodel.fromdt, dealsmodel.todt, dealsmodel.price, dealsmodel.active)
  if (sessionid == ''): dealresults = query.all()
  else: dealresults = query.filter(searchqueue.sessionid == sessionid).all()

  deals = []
  for result in dealresults:
    deal = {}

    deal['id'] = int(result.id)
    deal['agency'] = result.agency.encode("utf-8")
    deal['hotelid'] = int(result.hotelid)
    deal['roomtype'] = result.roomtype.encode("utf-8")
    deal['fromdt'] = str(result.fromdt)
    deal['todt'] = str(result.todt)
    deal['price'] = int(result.price)
    deal['active'] = int(result.active)

    deals.append(deal)

  db.session.close()
  return deals

@deals.route('/api/v1.0/deals/alldeals', methods=['GET'])
@cross_origin()
def alldeals():
  with zipkin_span(service_name='hotels.com:dealsquery', span_name='dealquery:alldeals', transport_handler=http_transport,
    port=PORT, sample_rate=ZIPKINSAMPLERATE):   
    deals = getdeals('')
    return jsonify({ 'deals': deals })

@zipkin_span(service_name='hotels.com:dealsquery', span_name='dealquery:dealsdatabaseindexsetup')
def dealsdatabaseindexsetup(sessionid, searchidsdata):
  searchqueues = []
  for searchid in searchidsdata:
    searchqueues.append(searchqueue(sessionid, searchid))
            
  db.session.add_all(searchqueues);
  db.session.commit()
  db.session.close() 

@zipkin_span(service_name='hotels.com:dealsquery', span_name='dealquery:loghotelsearchevents')
def loghotelsearchevents(mq, sessionid, eventjson):
  mq.publish(sessionid, eventjson)
  mq.rpush('HOTELSEARCHSESSION-' + sessionid, eventjson)

@zipkin_span(service_name='hotels.com:dealsquery', span_name='dealquery:setupsearchindex') 
@timeout_decorator.timeout(4, use_signals=False) 
def setupsearchindex(sessionid):
  mq = redis.StrictRedis(connection_pool=mqpool)
  sub = mq.pubsub()

  sub.subscribe(sessionid)
  while True:
    for message in sub.listen():
      if message['type'] == 'message':
        data = message['data']       
        data = json.loads(data)

        if data['event'] == 'hotelsearchcompleted':
          searchidsdata = data['searchids']
          
          if (len(searchidsdata) <= 0):
            loghotelsearchevents(mq, sessionid, json.dumps({ 'sessionid': sessionid, 'event': 'dealemptyresultsetfound' }))
            return False
          else:
            dealsdatabaseindexsetup(sessionid, searchidsdata)
            loghotelsearchevents(mq, sessionid, json.dumps({ 'sessionid': sessionid, 'event': 'dealsearchindexcreated' }))

            return True

@deals.route('/api/v1.0/deals/dealsbyhotel', methods=['GET'])
@cross_origin()
def dealsbyhotel():
  with zipkin_span(service_name='hotels.com:dealsquery', zipkin_attrs=ZipkinAttrs(trace_id=request.headers['X-B3-TraceID'],
    span_id=request.headers['X-B3-SpanID'], parent_span_id=request.headers['X-B3-ParentSpanID'], flags='1', is_sampled=
    request.headers['X-B3-Sampled']),span_name='dealquery:dealsbyhotel', transport_handler=http_transport, port=PORT, 
    sample_rate=ZIPKINSAMPLERATE):  
    sessionid = request.args.get('sessionid')
    debugmessage('BEGIN DEALS SEARCH: SESSIONID', sessionid)

    status = setupsearchindex(sessionid)
    if (status == False):
      return jsonify({})

    deals = getdeals(sessionid)
    hoteldict = defaultdict(defaultdict)

    for deal in deals: 
      hoteldict[deal['hotelid']] = []

    for deal in deals: 
      hoteldict[deal['hotelid']].append(deal)

    debugmessage('END DEALS SEARCH: SESSIONID', sessionid)
    return jsonify(hoteldict)

@deals.route('/api/v1.0/deals', methods=['POST'])
@cross_origin()
def createdeal():
  with zipkin_span(service_name='hotels.com:dealsquery', span_name='dealquery:createdeal', transport_handler=http_transport,
    port=PORT, sample_rate=ZIPKINSAMPLERATE):  
    if not request.json or not 'price' in request.json or not 'id' in request.json:
      abort(400)
  
    deal = {
      'id': request.json['id'],
      'agency': request.json['agency'],
      'hotelid': request.json['hotelid'],    
      'roomtype': request.json['roomtype'],
      'fromdt': request.json['fromdt'].encode("utf-8"),
      'todt': request.json['todt'].encode("utf-8"),
      'price': request.json['price'],
      'active': request.json['active'],    
    }
    
    newdeal = dealsmodel(deal['id'], deal['agency'], deal['hotelid'], deal['roomtype'], deal['fromdt'], deal['todt'], deal['price'], deal['active'])
    db.session.add(newdeal)

    try:
      db.session.commit()
    except DatabaseError:
      db.session.rollback()
    
    db.session.close()    
    return jsonify({ 'deal': deal }), 201  
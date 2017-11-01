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
amenities = Blueprint('amenities', __name__)

from main import db
from main import generalamenitiesmodel
from main import amenitiesmodel
from main import searchqueue
from main import mqpool

PORT = int(os.getenv('PORT', '9014'))
ZIPKINURI = os.getenv('ZIPKINURI', 'http://zipkin:9411')
ZIPKINSAMPLERATE = float(os.getenv('ZIPKINSAMPLERATE', 100.0))
DEBUG = int(os.getenv('DEBUG', '0'))

@amenities.errorhandler(400)
def not_found(error):
  return make_response(jsonify( { 'error': 'Bad request' }), 400)

@amenities.errorhandler(404)
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

@zipkin_span(service_name='hotels.com:amenitiesquery', span_name='amenitiesquery:topamenities')  
def getamenities(sessionid, limit):
  query = amenitiesmodel.query.join(searchqueue, amenitiesmodel.hotelid == searchqueue.hotelid)
  query = query.join(generalamenitiesmodel, amenitiesmodel.amenityid == generalamenitiesmodel.id)

  query = query.add_columns(amenitiesmodel.id, amenitiesmodel.hotelid, amenitiesmodel.amenityid, amenitiesmodel.isfree, amenitiesmodel.description, 
  generalamenitiesmodel.icon, generalamenitiesmodel.category, generalamenitiesmodel.amenity, amenitiesmodel.label)

  if (sessionid == ''): query = query.filter(amenitiesmodel.displayorder <= limit)
  else: query = query.filter(searchqueue.sessionid == sessionid and amenitiesmodel.displayorder <= limit)

  topamenitiesresults = query.all()
  
  topamenities = []
  for result in topamenitiesresults:
    amenity = {}

    amenity['id'] = int(result.id)
    amenity['hotelid'] = int(result.hotelid)
    amenity['amenityid'] = int(result.amenityid)    
    amenity['isfree'] = int(result.isfree)
    amenity['description'] = result.description.encode("utf-8")
    amenity['icon'] = result.icon.encode("utf-8")
    amenity['category'] = result.category.encode("utf-8")
    amenity['amenity'] = result.amenity.encode("utf-8")
    amenity['label'] = result.label.encode("utf-8")

    topamenities.append(amenity)  

  db.session.close()
  return topamenities

@amenities.route('/api/v1.0/amenities/allamenities', methods=['GET'])
@cross_origin()
def allamenities():
  with zipkin_span(service_name='hotels.com:amenitiesquery', span_name='amenitiesquery:allamenities', transport_handler=http_transport,
    port=PORT, sample_rate=ZIPKINSAMPLERATE):   
    amenities = getamenities('', 1000)
    return jsonify({ 'amenities': amenities })  

@zipkin_span(service_name='hotels.com:amenitiesquery', span_name='amenitiesquery:amenitiesdatabaseindexsetup')
def amenitiesdatabaseindexsetup(sessionid, searchidsdata):
  searchqueues = []
  for searchid in searchidsdata:
    searchqueues.append(searchqueue(sessionid, searchid))
            
  db.session.add_all(searchqueues);
  db.session.commit()
  db.session.close()

@zipkin_span(service_name='hotels.com:amenitiesquery', span_name='amenitiesquery:loghotelsearchevents')
def loghotelsearchevents(mq, sessionid, eventjson):
  mq.publish(sessionid, eventjson)
  mq.rpush('HOTELSEARCHSESSION-' + sessionid, eventjson)

@zipkin_span(service_name='hotels.com:amenitiesquery', span_name='amenitiesquery:setupsearchindex')
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
            loghotelsearchevents(mq, sessionid, json.dumps({ 'sessionid': sessionid, 'event': 'amenitiesemptyresultsetfound' }))
            return False
          else:
            amenitiesdatabaseindexsetup(sessionid, searchidsdata)
            loghotelsearchevents(mq, sessionid, json.dumps({ 'sessionid': sessionid, 'event': 'amenitiessearchindexcreated' }))

            return True           

@amenities.route('/api/v1.0/amenities/topamenitiesbyhotel', methods=['GET'])
@cross_origin()
def topamenitiesbyhotel():
  with zipkin_span(service_name='hotels.com:amenitiesquery', zipkin_attrs=ZipkinAttrs(trace_id=request.headers['X-B3-TraceID'],
    span_id=request.headers['X-B3-SpanID'], parent_span_id=request.headers['X-B3-ParentSpanID'], flags='1', is_sampled=
    request.headers['X-B3-Sampled']),span_name='amenitiesquery:amenitiesbyhotel', transport_handler=http_transport, port=PORT, 
    sample_rate=ZIPKINSAMPLERATE):
    sessionid = request.args.get('sessionid')
    debugmessage('BEGIN AMENITIES SEARCH: SESSIONID', sessionid)
    
    status = setupsearchindex(sessionid)
    if (status == False):
      return jsonify({})

    amenities = getamenities(sessionid, 6)
    amenitiesdict = defaultdict(defaultdict)

    for amenity in amenities: 
      amenitiesdict[amenity['hotelid']] = []

    for amenity in amenities: 
      amenitiesdict[amenity['hotelid']].append(amenity)

    debugmessage('END AMENITIES SEARCH: SESSIONID', sessionid)    
    return jsonify(amenitiesdict)

@amenities.route('/api/v1.0/amenities', methods=['POST'])
@cross_origin()
def createamenities():
  with zipkin_span(service_name='hotels.com:amenitiesquery', span_name='amenitiesquery:createamenity', transport_handler=http_transport,
    port=PORT, sample_rate=ZIPKINSAMPLERATE):  
    if not request.json or not 'hotelid' in request.json or not 'id' in request.json:
      abort(400)
  
    amenity = {
      'id': request.json['id'],
      'hotelid': request.json['hotelid'],    
      'amenityid': request.json['amenityid'],
      'isfree': request.json['isfree'],
      'description': request.json['description'].encode("utf-8"),
      'displayorder': request.json['displayorder'],
      'label': request.json['label'].encode("utf-8"),    
    }
    
    newamenity = amenitiesmodel(amenity['id'], amenity['hotelid'], amenity['amenityid'], amenity['isfree'], amenity['description'], 
    amenity['displayorder'], amenity['label'])
    db.session.add(newamenity)

    try:
      db.session.commit()
    except DatabaseError:
      db.session.rollback()
    
    db.session.close()    
    return jsonify({ 'amenity': amenity }), 201  
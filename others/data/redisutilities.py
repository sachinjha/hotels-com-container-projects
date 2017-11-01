import os

import xlrd
import csv

import json
import requests

import redis

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

if 'VCAP_SERVICES' in os.environ: 
  vcap_services = json.loads(os.environ['VCAP_SERVICES'])

  uri = ''
  for key, value in vcap_services.iteritems():   # iter on both keys and values
    if key.find('redis') > 0:
      redis_info = vcap_services[key][0]
		
      cred = redis_info['credentials']
      uri = cred['uri'].encode('utf8')
      
  redis = redis.StrictRedis.from_url(uri + '/0')
else:
  redis = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', 9001), db=0)
  #redis = redis.StrictRedis(host=os.getenv('REDIS_HOST', '192.168.99.100'), port=os.getenv('REDIS_PORT', 31471), db=0)

APIENDPOINTURL = os.getenv('DATALOADURL', 'http://localhost')
def fiximages():
  keys = redis.keys('H*')
  for key in keys:
    list = redis.lrange(key, 0, -1)
    print list

def readexcelsheet(sheetobject, sheetdata, processstatusmessage):
  rowcount = 0
  if(sheetobject.nrows < 1):
    processstatusmessage.append('No data in sheet')
    return 0

  sheetheaders = []
  for col in range(sheetobject.ncols):
    sheetheaders.append(sheetobject.cell_value(0, col))

  for row in range(1, sheetobject.nrows):
    elm = {}
    
    for col in range(sheetobject.ncols):
      value = sheetobject.cell_value(row, col)
      ctype = sheetobject.cell_type(row, col)
      
      if isinstance(value, float) and value == int(value):
        elm[sheetheaders[col].encode("ascii")] = int(sheetobject.cell_value(row,col))
      elif isinstance(value, float):
        elm[sheetheaders[col].encode("ascii")] = sheetobject.cell_value(row,col)      
      elif isinstance(value, int):
        elm[sheetheaders[col].encode("ascii")] = int(sheetobject.cell_value(row,col))    
      else:
        elm[sheetheaders[col].encode("ascii")] = sheetobject.cell_value(row, col).encode("ascii")
      
    sheetdata.append(elm)
    
  return sheetobject.nrows

def createlocationdata(dataxls):
  locationsheet = dataxls.sheet_by_name("locations")

  locationdata = []
  processstatusmessage = []

  numrows = readexcelsheet(locationsheet, locationdata, processstatusmessage)

  #url = 'http://localhost:9011/hotels.com/api/v1.0/locations'
  #url = 'https://hotels-com-20170807164728186-locationquery.mybluemix.net/hotels.com/api/v1.0/locations'
  #url = 'http://192.168.99.100:31011/hotels.com/api/v1.0/locations'
  #url = 'http://184.173.5.169:31011/hotels.com/api/v1.0/locations'
  #url = 'http://192.168.122.10:31011/hotels.com/api/v1.0/locations'
  #url = 'https://locationquery.mybluemix.net/hotels.com/api/v1.0/locations'
  #url = 'http://9.113.140.160:31011/hotels.com/api/v1.0/locations'
  url = 'http://169.51.13.228:31011/hotels.com/api/v1.0/locations'
  headers = {'Content-type': 'application/json'}

  if numrows > 0:
    for location in locationdata:
      print url, json.dumps(location), headers
      response = requests.post(url, data=json.dumps(location), headers=headers)
      print response

def createhoteldata(dataxls):
  hotelsheet = dataxls.sheet_by_name("hotels")

  hoteldata = []
  processstatusmessage = []

  numrows = readexcelsheet(hotelsheet, hoteldata, processstatusmessage)

  #url = 'http://localhost:9012/hotels.com/api/v1.0/hotels'
  #url = 'https://hotels-com-20170807164728186-hotelquery.mybluemix.net/hotels.com/api/v1.0/hotels'
  #url = 'http://192.168.99.100:31012/hotels.com/api/v1.0/hotels'
  #url = 'http://192.168.122.10:31012/hotels.com/api/v1.0/hotels'
  #url = 'http://9.113.140.160:31012/hotels.com/api/v1.0/hotels'
  url = 'http://169.51.13.228:31012/hotels.com/api/v1.0/hotels'
  headers = {'Content-type': 'application/json'}

  if numrows > 0:
    for hotel in hoteldata:
      print url, json.dumps(hotel), headers
      response = requests.post(url, data=json.dumps(hotel), headers=headers)
      print response

def geocodehoteldata(dataxls):
  hotelsheet = dataxls.sheet_by_name("hotels")

  hoteldata = []
  processstatusmessage = []

  numrows = readexcelsheet(hotelsheet, hoteldata, processstatusmessage)
  if numrows > 0:
    for hotel in hoteldata:
      url = 'https://maps.googleapis.com/maps/api/geocode/json?address=<address>&key=AIzaSyBNDq5fFF096N2JA4TwCA2xhzcI2zlX4qs'
      headers = {'Content-type': 'application/json'}
      
      hoteladdress = hotel['displayname'] + ', Chennai, India'
      newurl = url.replace('<address>', hoteladdress)
      
      response = requests.get(newurl, headers=headers)
      jsonresponse = json.loads(response.text)

      results = jsonresponse['results']
      if (len(results) > 0):
        lat = results[0]['geometry']['location']['lat']
        lng = results[0]['geometry']['location']['lng']

        print '"%s",' % hotel['displayname'], '"%s",' % results[0]['formatted_address'].replace(',', ';'), '%s,' % lat, '%s' % lng
      else:
        lat = 0
        lng = 0

        print '"%s",' % hotel['displayname'], ',', '%s,' % lat, '%s' % lng

def createdealdata(dataxls):
  dealsheet = dataxls.sheet_by_name("deals")
  
  dealdata = []
  processstatusmessage = []

  #url = 'http://localhost:9013/hotels.com/api/v1.0/deals'
  #url = 'https://hotels-com-20170807164728186-dealsquery.mybluemix.net/hotels.com/api/v1.0/deals'
  #url = 'http://192.168.99.100:31013/hotels.com/api/v1.0/deals'
  #url = 'http://192.168.122.10:31013/hotels.com/api/v1.0/deals'  
  #url = 'http://9.113.140.160:31013/hotels.com/api/v1.0/deals'
  url = 'http://169.51.13.228:31013/hotels.com/api/v1.0/deals'  
  headers = {'Content-type': 'application/json'}

  numrows = readexcelsheet(dealsheet, dealdata, processstatusmessage)
  if numrows > 0:
    for deal in dealdata:
      if deal['id'] > 0:
        print url, json.dumps(deal), headers
        response = requests.post(url, data=json.dumps(deal), headers=headers)
        print response

def createamenitydata(dataxls):
  amenitiessheet = dataxls.sheet_by_name("amenities")
  
  amenitiesdata = []
  processstatusmessage = []

  #url = 'http://localhost:9014/hotels.com/api/v1.0/amenities'
  #url = 'http://192.168.99.100:31014/hotels.com/api/v1.0/amenities'  
  #url = 'https://amenitiesquery.mybluemix.net/hotels.com/api/v1.0/amenities'
  #url = 'http://192.168.122.10:31014/hotels.com/api/v1.0/amenities'  
  #url = 'http://9.113.140.160:31014/hotels.com/api/v1.0/amenities'
  url = 'http://169.51.13.228:31014/hotels.com/api/v1.0/amenities'  
  headers = {'Content-type': 'application/json'}

  numrows = readexcelsheet(amenitiessheet, amenitiesdata, processstatusmessage)
  if numrows > 0:
    for amenity in amenitiesdata:
      if amenity['id'] >= 1:
        print url, json.dumps(amenity), headers
        response = requests.post(url, data=json.dumps(amenity), headers=headers)
        print response

def deletehotelsearchkeys():
  keys = redis.keys('HOTELSEARCHSESSION*')
  for key in keys:
    print key
    redis.delete(key)

def createtestdata(datafile):
  dataxls = xlrd.open_workbook(datafile)
  #createlocationdata(dataxls)
  #createhoteldata(dataxls)
  createdealdata(dataxls)
  createamenitydata(dataxls)
  #geocodehoteldata(dataxls)
  #fiximages()
  #deletehotelsearchkeys()

if __name__ == "__main__":
  createtestdata('data.xlsx')
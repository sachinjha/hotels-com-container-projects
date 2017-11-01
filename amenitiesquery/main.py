import os
import json

from flask import Flask
from flask_cors import CORS

import redis
from flask_sqlalchemy import SQLAlchemy

from gevent.wsgi import WSGIServer
app = Flask(__name__)

from amenities import amenities
app.register_blueprint(amenities, url_prefix='/hotels.com')

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

mqpool = None
if 'VCAP_SERVICES' in os.environ: 
  vcap_services = json.loads(os.environ['VCAP_SERVICES'])

  uri = ''
  urimq = ''

  for key, value in vcap_services.iteritems():   # iter on both keys and values
	  if key.find('mysql') > 0 or key.find('cleardb') >= 0:
	    mysql_info = vcap_services[key][0]
		
	    cred = mysql_info['credentials']
	    uri = cred['uri'].encode('utf8').replace('?reconnect=true', '')
	  elif key.find('redis') > 0:
	    redis_info = vcap_services[key][0]
		
	    cred = redis_info['credentials']
	    urimq = cred['uri'].encode('utf8')
  
  app.config['SQLALCHEMY_DATABASE_URI'] = uri 
  mqpool  = redis.ConnectionPool.from_url(urimq + '/0') 
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQLURI', 'mysql://root:password@mysql:3306/sys')
  mqpool = redis.ConnectionPool.from_url(os.getenv('MQURI', 'redis://localhost:6379/0'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class generalamenitiesmodel(db.Model):
  __tablename__ = "generalamenities"
  __table_args__ = { "schema": "hotelamenities" }

  id = db.Column(db.Integer, primary_key = True)
  category = db.Column(db.String(128))
  amenity = db.Column(db.String(128))
  icon = db.Column(db.String(512))

  def __init__(self, id, category, amenity, icon):
    self.id = id
    self.category = category
    self.amenity = amenity
    self.icon = icon

class amenitiesmodel(db.Model):
  __tablename__ = "amenities"
  __table_args__ = { "schema": "hotelamenities" }  

  id = db.Column(db.Integer, primary_key = True)
  hotelid = db.Column(db.Integer)
  amenityid = db.Column(db.Integer)
  isfree = db.Column(db.Integer)
  description = db.Column(db.String(128))
  displayorder = db.Column(db.Integer)
  label = db.Column(db.String(32))

  def __init__(self, id, hotelid, amenityid, isfree, description, displayorder, label):
    self.id = id
    self.hotelid = hotelid
    self.amenityid = amenityid
    self.isfree = isfree
    self.description = description
    self.displayorder = displayorder
    self.label = label

class searchqueue(db.Model):
  __tablename__ = "searchqueueamenities"
  __table_args__ = { "schema": "hotelamenities" }  

  id = db.Column(db.Integer, primary_key = True)
  sessionid = db.Column(db.String(512))
  hotelid = db.Column(db.Integer)

  def __init__(self, sessionid, hotelid):
    self.sessionid = sessionid
    self.hotelid = hotelid

  def __repr__(self):
    return '<Row %r %r>' % self.sessionid, self.hotelid                

port = os.getenv('PORT', '9014')
if __name__ == "__main__":
  http_server = WSGIServer(('0.0.0.0', int(port)), app)
  http_server.serve_forever()
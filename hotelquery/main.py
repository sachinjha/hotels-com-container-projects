import os

from flask import Flask
from flask_cors import CORS

from hotel import hotel

from gevent.wsgi import WSGIServer
app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.register_blueprint(hotel, url_prefix='/hotels.com')

port = os.getenv('PORT', '9012')
if __name__ == "__main__":
  http_server = WSGIServer(('0.0.0.0', int(port)), app)
  http_server.serve_forever()
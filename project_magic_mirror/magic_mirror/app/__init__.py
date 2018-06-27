import gevent.monkey
gevent.monkey.patch_all()

from flask_uwsgi_websocket import GeventWebSocket
from flask import Flask

app = Flask(__name__)
websocket = GeventWebSocket(app)


from database.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Bootstrap(app)


from app import route
from facenet_face_recognition import whoisit
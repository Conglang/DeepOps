from flask import Flask
from flask_uwsgi_websocket import GeventWebSocket
from utils import *
from flask import render_template
import numpy as np
from gameplay import run
from gameplay import get_audio
# from flask_bootstrap import Bootstrap

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Bootstrap(app)
websocket = GeventWebSocket(app)



@app.route('/')
def home():
    title = "Magic Mirror"
    debugmsg = "test msg"
    return render_template('index.html', debugmsg=debugmsg, title=title, isdebug = False)


@websocket.route('/websocket')
def user_messages(ws):
    pre_msg_count = 0
    photos = []
    sample_rate = 0
    photo_num = 0
    photo_width = 0
    photo_height = 0

    while True:
        msg = ws.receive()
        if msg is None:
            break
        if msg == b"":
            continue

        if pre_msg_count < 4:
            print(msg)
            if pre_msg_count == 0:
                # the first message should be the sample rate
                sample_rate = getIntMsg(msg)
            elif pre_msg_count == 1:
                # photo count
                photo_num = getIntMsg(msg)
            elif pre_msg_count == 2:
                # photo width
                photo_width = getIntMsg(msg)
            elif pre_msg_count == 3:
                # photo height
                photo_height = getIntMsg(msg)
            pre_msg_count = pre_msg_count + 1
        elif pre_msg_count < photo_num + 4:
            # photo_num message are user photos
            photo_as_int_array = np.frombuffer(msg, 'i2')
            photos.append(photo_as_int_array)
            pre_msg_count = pre_msg_count + 1
        else:
            audio_as_int_array = np.frombuffer(msg, 'i2')
            run(photos, sample_rate, audio_as_int_array)


@app.route('/getFileName')
def getFileName():
    return get_audio()

if __name__ == '__main__':
    app.run(debug=True, gevent=3000)

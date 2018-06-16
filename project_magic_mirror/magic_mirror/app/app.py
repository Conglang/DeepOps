from flask import Flask
from flask_uwsgi_websocket import GeventWebSocket
from utils import *
from flask import render_template
import numpy as np
from gameplay import run


app = Flask(__name__)
websocket = GeventWebSocket(app)



@app.route('/')
@app.route('/index')
def home():
    print(app)
    print(websocket)
    title = "Magic Mirror"
    debugmsg = "test msg"
    return render_template('index.html', debugmsg=debugmsg, title=title, isdebug = False)


@websocket.route('/websocket')
def audio(ws):
    first_message = True
    total_msg = ""
    sample_rate = 0

    while True:
        msg = ws.receive()

        if first_message and msg is not None: # the first message should be the sample rate
            sample_rate = getSampleRate(msg)
            print(sample_rate)
            first_message = False
            continue
        elif msg is not None:
            audio_as_int_array = np.frombuffer(msg, 'i2')
            # doSomething(audio_as_int_array)
            #print("yahaha")
            run(sample_rate, audio_as_int_array)
        else:
            break

if __name__ == '__main__':
    app.run(debug=True, gevent=3000)

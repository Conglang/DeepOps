from flask import render_template
import numpy as np
from game import gameplay, utils


from app import app
from app import db
from app import migrate
from app import websocket

@app.route('/')
@app.route('/index')
def index():
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
    photo_buffer = b""
    chunk_num = 127
    photo_index = 0

    while True:
        msg = ws.receive()
        if msg is None:
            break
        if msg == b"":
            continue

        if pre_msg_count < 4:
            print(msg)
            if pre_msg_count == 0:
                gameplay.clear_player_id()
                # the first message should be the sample rate
                sample_rate = utils.getIntMsg(msg)
            elif pre_msg_count == 1:
                # photo count
                photo_num = utils.getIntMsg(msg)
            elif pre_msg_count == 2:
                # photo width
                photo_width = utils.getIntMsg(msg)
            elif pre_msg_count == 3:
                # photo height
                photo_height = utils.getIntMsg(msg)
            pre_msg_count = pre_msg_count + 1
        elif photo_index < photo_num:
            photo_buffer = photo_buffer + msg
            if len(photo_buffer) == photo_width * photo_height * 3:
                photo_index = photo_index + 1
                photo_as_int_array = np.frombuffer(photo_buffer, 'uint8')
                print(photo_as_int_array)
                photo_buffer = b""
                gameplay.face_recognition(photo_width, photo_height, photo_as_int_array, photo_index == photo_num)
        else:
            # print("audio", msg)
            try:
                audio_as_int_array = np.frombuffer(msg, 'i2')
                gameplay.run(sample_rate, audio_as_int_array)
            except:
                pass

@app.route('/getFileName')
def getFileName():
    return gameplay.get_audio()

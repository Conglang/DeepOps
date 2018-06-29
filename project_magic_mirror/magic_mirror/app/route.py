from flask import render_template
import numpy as np
import threading
from game import utils, gameplay
import uwsgidecorators


from app import app
from app import db
from app import migrate
from app import websocket

game_client = None

@uwsgidecorators.postfork
@uwsgidecorators.thread
def daemon():
    global game_client
    if game_client is None:
        game_client = gameplay.GamePlay()

# from flask import g



# #from threading.Queue import Queue

# #data_queue = Queue()

# # with app.app_context():
# #     g.game_client = None
# #     if g.game_client is None:
# #         g.game_client = gameplay.GamePlay()
# #         #data_queue.put(game_client)

# game_client = None
# if game_client is None:
#     game_client = gameplay.GamePlay()
#     game_client.start()

# def get_game_client():
#     game_client = gameplay.GamePlay()
#     return game_client

# #threading.Thread(target=print_work_a, name='Thread-a', daemon=True)



@app.route('/')
@app.route('/index')
def index():
    title = "Magic Mirror"
    debugmsg = "test msg"
    return render_template('index.html', debugmsg=debugmsg, title=title, isdebug = False)


@websocket.route('/websocket')
def user_messages(ws):
    while True:
        msg = ws.receive()
        game_client.process_msg(msg)
    # gc = data_queue.get()
    # game_client.set_ws(ws)
    # if not game_client.is_alive():
    #     game_client.start()
    # game_client.process_msg(ws)
    # game_client.set_ws(ws)
    # if not game_client.is_alive():
    #     game_client.start()
    # game_client.process_msg(ws)


@app.route('/getFileName')
def getFileName():
    # with app.app_context():
    #     if g.game_client is None:
    #         return ""
    #     return g.game_client.get_audio()
    return game_client.get_audio()

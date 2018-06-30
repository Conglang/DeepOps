import os
import numpy as np
from constants import *
from game.audio_logic import AudioLogic
from game.photo_logic import PhotoLogic

from game.utils import *
import random
from database import dbop

from threading import Thread
import functools
import threading

lock = threading.Lock()


def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)
        return inner_wrapper
    return wrapper

class Singleton(type):
    _instances = {}

    @synchronized(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# control game state
class GamePlay(metaclass=Singleton):
    def __init__(self):
        super(GamePlay, self).__init__()
        self.daemon = True
        self.cancelled = False

        # self.ws = None

        print("a game play instance. -----------------------")
        # global variables
        self.game_state_list = [STATE_SHUTDOWN]
        self.player_id_list = [INVALID_USER]
        self.audio_file_list = [""]


        # process msg
        self.reset_states()

        # instances
        self.photo_logic = PhotoLogic(self.game_state_list, self.player_id_list)
        self.audio_logic = AudioLogic(self.game_state_list, self.player_id_list, self.audio_file_list) # todo
    
    def reset_states(self):
        self.pre_msg_count = 0
        self.photos = []
        self.sample_rate = 0
        self.photo_num = 0
        self.photo_width = 0
        self.photo_height = 0
        self.photo_buffer = b""
        self.photo_index = 0

        self.audio_buffer = np.zeros(FEED_SAMPLES, dtype='int16')

    def clear_player_id(self):
        if self.player_id_list[0] != INVALID_USER:
            self.player_id_list[0] = INVALID_USER
    
    def get_audio(self):
        return self.audio_file_list[0]

    # main loop
    def main_loop(self, sample_rate, audio_as_int_array):
        print(self.game_state_list[0])
        if self.game_state_list[0] in [STATE_LISTEN, STATE_PLAY, STATE_RECORD]:
            self.trigger_listening(audio_as_int_array)
        if self.game_state_list[0] == STATE_RECORD:
            self.audio_logic.save_to_file(sample_rate, audio_as_int_array)
        if self.game_state_list[0] == STATE_PLAY:
            self.audio_logic.start_play_audio()

    # face recognition
    def face_recognition_logic(self, width, height, photo, isfinish):
        self.photo_logic.face_recognition(width, height, photo, isfinish)

    # trigger word detection
    def trigger_listening(self, audio_as_int_array):
        self.audio_buffer = np.append(self.audio_buffer, audio_as_int_array)
        if len(self.audio_buffer) > FEED_SAMPLES:
            self.audio_buffer = self.audio_buffer[-FEED_SAMPLES:]
            self.audio_logic.audio_queue.put(self.audio_buffer)
        
    def process_msg(self, msg):
        if msg is None:
            print("empty msg------", msg)
            return

        if self.pre_msg_count < 4:
            if self.pre_msg_count == 0:
                self.clear_player_id()
                # the first message should be the sample rate
                self.sample_rate = getIntMsg(msg)
            elif self.pre_msg_count == 1:
                # photo count
                self.photo_num = getIntMsg(msg)
            elif self.pre_msg_count == 2:
                # photo width
                self.photo_width = getIntMsg(msg)
            elif self.pre_msg_count == 3:
                # photo height
                self.photo_height = getIntMsg(msg)
            self.pre_msg_count = self.pre_msg_count + 1
        elif self.photo_index < self.photo_num:
            # 5 photos
            self.photo_buffer = self.photo_buffer + msg
            if len(self.photo_buffer) == self.photo_width * self.photo_height * 3:
                print("get photos")
                self.photo_index = self.photo_index + 1
                photo_as_int_array = np.frombuffer(self.photo_buffer, 'uint8')
                self.photo_buffer = b""
                self.face_recognition_logic(self.photo_width, self.photo_height, photo_as_int_array, self.photo_index == self.photo_num)
        else:
            # audio
            audio_as_int_array = np.frombuffer(msg, 'i2')
            # print(audio_as_int_array)
            self.main_loop(self.sample_rate, audio_as_int_array)

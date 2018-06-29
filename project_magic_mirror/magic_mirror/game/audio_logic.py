import os
from game.utils import *
from threading import Timer
import time
from scipy.io.wavfile import write
import numpy as np

class AudioLogic():
    def __init__(self, game_state_list, player_id_list, audio_file_list):
        self.game_state_list = game_state_list
        self.player_id_list = player_id_list
        self.audio_file_list = audio_file_list
        self.audio_file_list[0] = ""
        
        self.sound_buffer = np.array([], np.dtype('i2'))
        self.sound_flush = False

        # global utilities - timer
        self.to_listen = Timer(10, self.timer_listen)
        self.to_play = Timer(5, self.timer_play)
        self.to_shutdown = Timer(5, self.timer_shutdown)

    def set_game_state(self, state):
        if self.game_state_list[0] != state:
            self.game_state_list[0] = state
            print("change game state to: ", state)

    def trigger_listening(self, audio_as_int_array):
        pass

    def timer_listen(self):
        self.set_game_state(STATE_LISTEN)
        self.stop_play_audio()
        self.to_shutdown.start()

    def timer_shutdown(self):
        self.set_game_state(STATE_SHUTDOWN)

    def timer_play(self):
        self.set_game_state(STATE_PLAY)

    def on_triggered(self):
        self.to_listen.cancel()
        self.to_shutdown.cancel()
        self.to_play.cancel()
        # if record
        self.sound_flush = True
        # if play
        self.stop_play_audio()

        self.set_game_state(STATE_RECORD)

    def save_to_file(self, sample_rate, intarray):
        if self.sound_buffer.shape[0] > self.sample_rate * 10 or self.sound_flush == True:
            print("write file")
            self.sound_flush = False
            write(os.path.join(RESOURCE_SOUND_PATH, str(player_id) + "_" +str(time.time())+'.wav'), sample_rate, sound_buffer)
            self.sound_buffer = np.array([], np.dtype('i2'))
            self.set_game_state(STATE_LISTEN)
            self.to_play.start()

        self.sound_buffer = np.append(self.sound_buffer, intarray)

    def start_play_audio(self):
        self.audio_file_list[0] = os.path.join(RESOURCE_SOUND_PATH, "-1_1529134666.0824802.wav")
        self.to_listen.start()
        pass

    def stop_play_audio(self):
        self.audio_file_list[0] = ""

    # for get request only
    def get_audio(self):
        return self.audio_file_list[0]
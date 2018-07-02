import os
from game.utils import *
from threading import Timer, Thread
import time
from scipy.io.wavfile import write
import numpy as np
from queue import Queue
from trigger_word_detection import triggerword
from constants import *
from shutil import copyfile

class AudioLogic():
    def __init__(self, game_state_list, player_id_list, audio_file_list):
        # game related
        self.game_state_list = game_state_list
        self.player_id_list = player_id_list
        self.audio_file_list = audio_file_list
        self.audio_file_list[0] = ""
        
        # for record
        self.sound_buffer = np.array([], np.dtype('i2'))
        self.sound_flush = False

        # global utilities - timer
        self.to_listen = None
        self.to_play = None
        self.to_shutdown = None

        # prepare model
        self.twd_client = triggerword.TWDetection()

        # audio queue
        self.audio_queue = Queue()

        # start detection
        self.audio_detect_thread = Thread(target = self.trigger_listening)
        self.start_detection()

    def timer_listen(self):
        self.stop_play_audio()
        self.set_game_state(STATE_LISTEN, "timer_listen")
        to_shutdown = Timer(5, self.timer_shutdown)
        to_shutdown.start()
        self.to_shutdown = to_shutdown

    def timer_shutdown(self):
        self.set_game_state(STATE_SHUTDOWN, "timer_shutdown")

    def timer_play(self):
        self.set_game_state(STATE_PLAY, "timer_play")
    
    def start_detection(self):
        self.audio_detect_thread.start()

    def set_game_state(self, state, desc):
        if self.game_state_list[0] != state:
            self.game_state_list[0] = state
            print("change game state to: ", state, "by ", desc)
            if state == STATE_LISTEN:
                play_chime(self.audio_file_list)
            if state == STATE_RECORD:
                play_click(self.audio_file_list)
            if state == STATE_SHUTDOWN:
                play_finish(self.audio_file_list)

    def trigger_listening(self):
        while self.audio_queue.not_empty:
            audio_data = self.audio_queue.get()
            # print("audio_data", audio_data)
            is_triggerred = self.twd_client.detect_trigger_word(audio_data)
            if is_triggerred:
                self.on_triggered()

    def on_triggered(self):
        print("triggerred")
        if not self.to_listen is None:
            self.to_listen.cancel()
        if not self.to_shutdown is None:
            self.to_shutdown.cancel()
        if not self.to_play is None:
            self.to_play.cancel()
        # if record
        # self.sound_flush = True
        # if play
        self.stop_play_audio()

        self.set_game_state(STATE_RECORD, "on_triggered")


    def save_to_file(self, sample_rate, intarray):
        if self.sound_buffer.shape[0] > sample_rate * 10:
            # self.sound_flush = False
            sound_path = os.path.join(RESOURCE_USER_SOUND_PATH, str(self.player_id_list[0]))
            if not os.path.exists(sound_path):
                os.makedirs(sound_path)
            sound_file = os.path.join(sound_path, str(time.time())+'.wav')
            print("write file", sound_file)
            write(sound_file, sample_rate, self.sound_buffer)
            self.sound_buffer = np.array([], np.dtype('i2'))
            self.set_game_state(STATE_LISTEN, "save_to_file")
            to_play = Timer(5, self.timer_play)
            to_play.start()
            self.to_play = to_play

        self.sound_buffer = np.append(self.sound_buffer, intarray)

    def start_play_audio(self):
        if not self.to_listen is None and self.to_listen.is_alive():
            return
        # get all sound file of this user
        # play one audio only
        sound_path = os.path.join(RESOURCE_USER_SOUND_PATH, str(self.player_id_list[0]))
        
        sound_files = get_all_ext_files_of_path(sound_path, "wav")
        print("sound_files", sound_files)
        if len(sound_files) == 0:
            self.set_game_state(STATE_LISTEN, "start_play_audio")
            return
        dest_name = str(time.time()) + ".wav"
        dest_file = os.path.join(RESOURCE_SERVER_SOUND_PATH, dest_name)
        copyfile(sound_files[-1], dest_file)
        # os.rename(sound_files[-1], dest_file)
        self.audio_file_list[0] = os.path.join(RESOURCE_CLIENT_SOUND_PATH, dest_name)
        to_listen = Timer(10, self.timer_listen)
        to_listen.start()
        self.to_listen = to_listen

    def stop_play_audio(self):
        print("stop play audio")
        self.audio_file_list[0] = ""

    # for get request only
    # def get_audio(self):
    #     print("current audio:", self.audio_file_list[0])
    #     return self.audio_file_list[0]
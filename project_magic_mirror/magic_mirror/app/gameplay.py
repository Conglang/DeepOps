from scipy.io.wavfile import write
import time
import numpy as np
from constants import *
from threading import Timer


game_state = STATE_SHUTDOWN
player_id = -1  # for test

audio_file = ""


sound_buffer = np.array([], np.dtype('i2'))
sound_flush = False

def timer_listen():
    set_game_state(STATE_LISTEN)
    stop_play_audio()
    to_shutdown.start()

def timer_shutdown():
    set_game_state(STATE_SHUTDOWN)

def timer_play():
    set_game_state(STATE_PLAY)

def set_game_state(state):
    global game_state
    game_state = state
    print("change game state to: ", state)

to_listen = Timer(10, timer_listen)
to_play = Timer(5, timer_play)
to_shutdown = Timer(5, timer_shutdown)
# -------------------------------------------------------
# main loop
def run(photos, sample_rate, audio_as_int_array):
    if game_state == STATE_SHUTDOWN:
        face_recognition(photos)
    if game_state in [STATE_LISTEN, STATE_PLAY, STATE_RECORD]:
        trigger_listening(audio_as_int_array)
    if game_state == STATE_RECORD:
        save_to_file(sample_rate, audio_as_int_array)
    if game_state == STATE_PLAY:
        start_play_audio()

# -------------------------------------------------------
# face recognition
def face_recognition(photos):
    # todo recognize and write to db
    # print(photos)
    print("face recognition")
    global player_id
    player_id = -1
    set_game_state(STATE_LISTEN)
    pass

# -------------------------------------------------------
def trigger_listening(audio_as_int_array):
    print("listening")
    pass
    

def on_triggered():
    global to_listen
    global to_shutdown
    global to_play
    to_listen.cancel()
    to_shutdown.cancel()
    to_play.cancel()
    # if record
    global sound_flush
    sound_flush = True
    # if play
    stop_play_audio()

    set_game_state(STATE_RECORD)



# -------------------------------------------------------


def save_to_file(sample_rate, intarray):
    global sound_buffer
    global sound_flush
    if sound_buffer.shape[0] > sample_rate * 10 or sound_flush == True:
        print("write file")
        sound_flush = False
        write(os.path.join(RESOURCE_SOUND_PATH, str(player_id) + "_" +str(time.time())+'.wav'), sample_rate, sound_buffer)
        sound_buffer = np.array([], np.dtype('i2'))
        set_game_state(STATE_LISTEN)
        to_play.start()

    sound_buffer = np.append(sound_buffer, intarray)

def start_play_audio():
    global audio_file
    audio_file = os.path.join(RESOURCE_SOUND_PATH, "-1_1529134666.0824802.wav")
    to_listen.start()
    pass

def stop_play_audio():
    global audio_file
    audio_file = ""

# for get request only
def get_audio():
    return audio_file
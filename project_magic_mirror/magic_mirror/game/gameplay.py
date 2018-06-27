import os
from scipy.io.wavfile import write
import time
import numpy as np
from constants import *
from threading import Timer
from facenet_face_recognition import whoisit
import imageio
import random
from database import dbop
from PIL import Image

game_state = STATE_SHUTDOWN
player_id = INVALID_USER  # for test

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
def run(sample_rate, audio_as_int_array):
    if game_state in [STATE_LISTEN, STATE_PLAY, STATE_RECORD]:
        trigger_listening(audio_as_int_array)
    if game_state == STATE_RECORD:
        save_to_file(sample_rate, audio_as_int_array)
    if game_state == STATE_PLAY:
        start_play_audio()

# -------------------------------------------------------
# face recognition
def clear_player_id():
    global player_id
    player_id = INVALID_USER

def resize_screenshot(source_path, dest_path):
    image = Image.open(source_path)
    # crop
    width, height = image.size   # Get dimensions

    left = (width - height)/2
    top = (height - height)/2
    right = (width + height)/2
    bottom = (height + height)/2

    image = image.crop((left, top, right, bottom))
    # resize
    size = (TARGET_IMAGE_WIDTH, TARGET_IMAGE_HEIGHT)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(dest_path, "JPEG")

def save_and_resize(width, height, photo):
    # write to temporary folder
    photo_path = os.path.join(RESOURCE_IMAGE_PATH, str(time.time()))
    photo = photo.reshape([height, width, 3])
    imageio.imsave(photo_path + ".jpg", photo)
    # resize image
    resized_photo_path = photo_path + "_resize"
    resize_screenshot(photo_path + ".jpg", resized_photo_path + ".jpg")
    return resized_photo_path + ".jpg"

def move_to_user_folder(photo_path, id):
    os.makedirs(RESOURCE_USER_IMAGE_PATH + str(id))
    dest_path = os.path.join(RESOURCE_USER_IMAGE_PATH + str(id), str(time.time()) + ".jpg")
    os.rename(photo_path, dest_path)

def face_recognition(width, height, photo, isfinish):
    print(len(photo))
    # assert len(photo) == width * height * 3
    global player_id

    if photo is None:
        set_game_state(STATE_SHUTDOWN)
        print("empty")
        return

    if player_id != INVALID_USER:
        print("we already know")
        photo_path = save_and_resize(width, height, photo)
        move_to_user_folder(photo_path, player_id)
        return

    photo_path = save_and_resize(width, height, photo)

    all_users = dbop.get_all_user()

    min_dist, id, img_encoding = whoisit.who_is_it(photo_path, all_users)

    if id is None:
        # add new user
        img_encoding = whoisit.get_embedding(photo_path)
        id = database.dbop.add_user(img_encoding)
        print("add new user", id)
        
    player_id = id
    # move to player folder
    move_to_user_folder(photo_path, id)
    print("player_id", player_id)

    if isfinish:
        set_game_state(STATE_LISTEN)

    

# -------------------------------------------------------
def trigger_listening(audio_as_int_array):
    # print("listening")
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
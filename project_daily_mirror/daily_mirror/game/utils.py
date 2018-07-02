import os
from constants import *

def getIntMsg(msg):
    return (int)(msg.decode("utf-8").split(':')[1])

def get_all_ext_files_of_path(rootdir, ext):
    filenames = []
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if filename.endswith("." + ext):
                filenames.append(os.path.join(folder, filename))
    return sorted(filenames, reverse = True)

def play_chime(audio_file_list):
    print("chime sound.")
    audio_file_list[0] = os.path.join(RESOURCE_CLIENT_SOUND_PATH, "chime.wav")

def play_click(audio_file_list):
    print("play click")
    audio_file_list[0] = os.path.join(RESOURCE_CLIENT_SOUND_PATH, "click.wav")

def play_finish(audio_file_list):
    print("play finish")
    audio_file_list[0] = os.path.join(RESOURCE_CLIENT_SOUND_PATH, "finish.mp3")
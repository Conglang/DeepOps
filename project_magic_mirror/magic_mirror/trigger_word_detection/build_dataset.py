import numpy as np
from pydub import AudioSegment
import random
import sys
import io
import os
import glob
import argparse
from td_utils import *
from constants import *
import time

def get_random_time_segment(segment_ms):
    """
    Gets a random time segment of duration segment_ms in a 10,000 ms audio clip.
    
    Arguments:
    segment_ms -- the duration of the audio clip in ms ("ms" stands for "milliseconds")
    
    Returns:
    segment_time -- a tuple of (segment_start, segment_end) in ms
    """
    
    segment_start = np.random.randint(low=0, high=10000-segment_ms)   # Make sure segment doesn't run past the 10sec background 
    segment_end = segment_start + segment_ms - 1
    
    return (segment_start, segment_end)

def is_overlapping(segment_time, previous_segments):
    """
    Checks if the time of a segment overlaps with the times of existing segments.
    
    Arguments:
    segment_time -- a tuple of (segment_start, segment_end) for the new segment
    previous_segments -- a list of tuples of (segment_start, segment_end) for the existing segments
    
    Returns:
    True if the time segment overlaps with any of the existing segments, False otherwise
    """
    
    segment_start, segment_end = segment_time
    
    # Step 1: Initialize overlap as a "False" flag. (≈ 1 line)
    overlap = False
    
    # Step 2: loop over the previous_segments start and end times.
    # Compare start/end times and set the flag to True if there is an overlap (≈ 3 lines)
    for previous_start, previous_end in previous_segments:
        if not (segment_time[0] > previous_end or segment_time[1] < previous_start):
            overlap = True

    return overlap

def insert_audio_clip(background, audio_clip, previous_segments):
    """
    Insert a new audio segment over the background noise at a random time step, ensuring that the 
    audio segment does not overlap with existing segments.
    
    Arguments:
    background -- a 10 second background audio recording.  
    audio_clip -- the audio clip to be inserted/overlaid. 
    previous_segments -- times where audio segments have already been placed
    
    Returns:
    new_background -- the updated background audio
    """
    
    # Get the duration of the audio clip in ms
    segment_ms = len(audio_clip)
    
    # Step 1: Use one of the helper functions to pick a random time segment onto which to insert 
    # the new audio clip. (≈ 1 line)
    segment_time = get_random_time_segment(segment_ms)
    
    # Step 2: Check if the new segment_time overlaps with one of the previous_segments. If so, keep 
    # picking new segment_time at random until it doesn't overlap. (≈ 2 lines)
    while is_overlapping(segment_time, previous_segments):
        segment_time = get_random_time_segment(segment_ms)

    # Step 3: Add the new segment_time to the list of previous_segments (≈ 1 line)
    previous_segments.append(segment_time)
    
    # Step 4: Superpose audio segment and background
    new_background = background.overlay(audio_clip, position = segment_time[0])
    
    return new_background, segment_time

def insert_ones(y, segment_end_ms):
    """
    Update the label vector y. The labels of the 50 output steps strictly after the end of the segment 
    should be set to 1. By strictly we mean that the label of segment_end_y should be 0 while, the
    50 followinf labels should be ones.
    
    
    Arguments:
    y -- numpy array of shape (1, Ty), the labels of the training example
    segment_end_ms -- the end time of the segment in ms
    
    Returns:
    y -- updated labels
    """
    
    # duration of the background (in terms of spectrogram time-steps)
    segment_end_y = int(segment_end_ms * Ty / 10000.0)
    
    # Add 1 to the correct index in the background label (y)
    for i in range(segment_end_y + 1, segment_end_y + 51):
        if i < Ty:
            y[0, i] = 1
    
    return y

def create_training_example(background, activates, negatives):
    """
    Creates a training example with a given background, activates, and negatives.
    
    Arguments:
    background -- a 10 second background audio recording
    activates -- a list of audio segments of the word "activate"
    negatives -- a list of audio segments of random words that are not "activate"
    
    Returns:
    x -- the spectrogram of the training example
    y -- the label at each time step of the spectrogram
    """
    
    # Set the random seed
    np.random.seed(18)
    
    # Make background quieter
    background = background - 20

    # Step 1: Initialize y (label vector) of zeros (≈ 1 line)
    y = np.zeros((1, Ty))

    # Step 2: Initialize segment times as empty list (≈ 1 line)
    previous_segments = []
    
    # Select 0-4 random "activate" audio clips from the entire list of "activates" recordings
    number_of_activates = np.random.randint(0, 5)
    random_indices = np.random.randint(len(activates), size=number_of_activates)
    random_activates = [activates[i] for i in random_indices]
    
    # Step 3: Loop over randomly selected "activate" clips and insert in background
    for random_activate in random_activates:
        # Insert the audio clip on the background
        background, segment_time = insert_audio_clip(background, random_activate, previous_segments)
        # Retrieve segment_start and segment_end from segment_time
        segment_start, segment_end = segment_time
        # Insert labels in "y"
        y = insert_ones(y, segment_end)

    # Select 0-2 random negatives audio recordings from the entire list of "negatives" recordings
    number_of_negatives = np.random.randint(0, 3)
    random_indices = np.random.randint(len(negatives), size=number_of_negatives)
    random_negatives = [negatives[i] for i in random_indices]

    # Step 4: Loop over randomly selected negative clips and insert in background
    for random_negative in random_negatives:
        # Insert the audio clip on the background 
        background, _ = insert_audio_clip(background, random_negative, previous_segments)
    
    # Standardize the volume of the audio clip 
    background = match_target_amplitude(background, -20.0)

    # Export new training example 
    train_name = os.path.join("./data/sound_data", "train_" + str(time.time()) + ".wav")
    file_handle = background.export(train_name, format="wav")
    print("File (" + train_name + ".wav) was saved in your directory.")
    
    # Get and plot spectrogram of the new recording (background with superposition of positive and negatives)
    x = graph_spectrogram(train_name)
    
    return x, y

# Load raw audio files for speech synthesis
def get_raw_data(data_path):
    activates = []
    backgrounds = []
    negatives = []
    for filename in os.listdir(os.path.join(data_path, "activates/")):
        if filename.endswith("wav"):
            activate = AudioSegment.from_wav(os.path.join(data_path, "activates/")+filename)
            activates.append(activate)
    for filename in os.listdir(os.path.join(data_path, "backgrounds")):
        if filename.endswith("wav"):
            background = AudioSegment.from_wav(os.path.join(data_path, "backgrounds/")+filename)
            backgrounds.append(background)
    for filename in os.listdir(os.path.join(data_path, "negatives")):
        if filename.endswith("wav"):
            negative = AudioSegment.from_wav(os.path.join(data_path, "negatives/")+filename)
            negatives.append(negative)
    return activates, negatives, backgrounds

def save_data(x, y):
    dest_path = "./data/activate_data"
    np.save(os.path.join(dest_path, "X"), x)
    np.save(os.path.join(dest_path, "Y"), y)

def build_dataset(data_path, activates, negatives, backgrounds, num):
    x_list = []
    y_list = []
    for i in range(0, num):
        background = random.choice(backgrounds)
        x, y = create_training_example(background, activates, negatives)
        x_list.append(x)
        y_list.append(y)
        X = np.vstack(x_list)
        Y = np.vstack(y_list)
    return X, Y

def build_whole_datasets(data_path, dest_path):
    activates, negatives, backgrounds = get_raw_data(data_path)
    
    # build training dataset
    X, Y = build_dataset(data_path, activates, negatives, backgrounds, 100)
    save_data(X, Y)
    return X, Y

parser = argparse.ArgumentParser()
parser.add_argument('--data_path', default='raw_data', help="Raw audio data")

if __name__ == '__main__':
    args = parser.parse_args()
    data_path = args.data_path
    dest_path = "./data/activate_data"

    build_whole_datasets(data_path, dest_path)
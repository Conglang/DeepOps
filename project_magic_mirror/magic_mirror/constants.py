# resource path
RESOURCE_SOUND_PATH = "./static/sound/"
RESOURCE_TEMP_PATH = "./temp/"
RESOURCE_USER_IMAGE_PATH = "./resource/user_images/"
RESOURCE_USER_SOUND_PATH = "./resource/user_sounds/"

# game constants
STATE_SHUTDOWN = "STATE_SHUTDOWN"
STATE_LISTEN = "STATE_LISTEN"
STATE_PLAY = "STATE_PLAY"
STATE_RECORD = "STATE_RECORD"

INVALID_USER = -1

# image constants
TARGET_IMAGE_WIDTH = 96
TARGET_IMAGE_HEIGHT = 96


# audio constants
TIMESTEPS_NUM_X = 5511 # The number of time steps input to the model from the spectrogram
TIMESTEPS_NUM_Y = 1375 # The number of time steps in the output of our model
FREQUENCY_NUM = 101 # Number of frequencies input to the model at each time step of the spectrogram
CHUNK_DURATION = 0.5
FEED_DURATION = 10
SAMPLE_RATE = 44100 # sampling rate for mic
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)
FEED_SAMPLES = int(SAMPLE_RATE * FEED_DURATION)
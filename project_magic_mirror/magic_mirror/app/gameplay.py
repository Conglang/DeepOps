from scipy.io.wavfile import write
import time
import numpy as np

sound_buffer = np.array([], np.dtype('i2'))

def run(sample_rate, audio_as_int_array):
    print("run", audio_as_int_array)
    save_to_file(sample_rate, audio_as_int_array)


def save_to_file(sample_rate, intarray):
    global sound_buffer
    print(sound_buffer)
    if sound_buffer.shape[0] > sample_rate * 10:
        print("write file")
        write('test'+str(time.time())+'.wav', sample_rate, sound_buffer)
        sound_buffer = np.array([], np.dtype('i2'))
    sound_buffer = np.append(sound_buffer, intarray)
    
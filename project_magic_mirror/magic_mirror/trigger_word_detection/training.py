import numpy as np
from model import load_exist_model, build_model, save_exist_model
from td_utils import *
from constants import *
import matplotlib
matplotlib.use('TkAgg')
from keras.optimizers import Adam

model = load_exist_model(model_dir)

def load_dataset():
    X = np.load("./data/activate_data/X.npy")
    Y = np.load("./data/activate_data/Y.npy")
    print(X.shape, Y.shape)
    assert X.shape[0] == Y.shape[0]
    split_point = int(X.shape[0] * 0.8)
    X_train, X_dev = X[:split_point], X[split_point:]
    Y_train, Y_dev = Y[:split_point], X[split_point:]
    return X_train, Y_train, X_dev, Y_dev

def training_and_evaluate():
    X, Y, X_dev, Y_dev = load_dataset()

    #model = build_model()
    #model = load_exist_model(model_dir)
    global model
    opt = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999, decay=0.01)
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=["accuracy"])
    model.fit(X, Y, batch_size = 5, epochs=1)

    loss, acc = model.evaluate(X_dev, Y_dev)
    print("Dev set accuracy = ", acc)

    save_exist_model(model_dir)
    return model


chime_file = "./data/chime.wav"
def chime_on_activate(filename, predictions, threshold):
    global model
    audio_clip = AudioSegment.from_wav(filename)
    chime = AudioSegment.from_wav(chime_file)
    Ty = predictions.shape[1]
    # Step 1: Initialize the number of consecutive output steps to 0
    consecutive_timesteps = 0
    # Step 2: Loop over the output steps in the y
    for i in range(Ty):
        # Step 3: Increment consecutive output steps
        consecutive_timesteps += 1
        # Step 4: If prediction is higher than the threshold and more than 75 consecutive output steps have passed
        if predictions[0,i,0] > threshold and consecutive_timesteps > 75:
            # Step 5: Superpose audio and background using pydub
            audio_clip = audio_clip.overlay(chime, position = ((i / Ty) * audio_clip.duration_seconds)*1000)
            # Step 6: Reset consecutive output steps to 0
            consecutive_timesteps = 0
        
    audio_clip.export("chime_output.wav", format='wav')

if __name__ == '__main__':
    training_and_evaluate()
    preprocess_audio(your_filename)
    chime_threshold = 0.5
    prediction = detect_triggerword(your_filename)
    chime_on_activate(your_filename, prediction, chime_threshold)
    IPython.display.Audio("./chime_output.wav")
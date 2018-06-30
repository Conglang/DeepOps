from trigger_word_detection.td_utils import get_spectrogram
from constants import *

from trigger_word_detection.model import load_exist_model, build_model, save_exist_model
import os


class TWDetection():
    def __init__(self):
        model_dir = os.path.join(os.path.dirname(__file__), "./data/model/tr_model.h5")
        self.model = load_exist_model(model_dir)

    def detect_triggerword_spectrum(self, x):
        """
        Function to predict the location of the trigger word.
        
        Argument:
        x -- spectrum of shape (freqs, Tx)
        i.e. (Number of frequencies, The number time steps)

        Returns:
        predictions -- flattened numpy array to shape (number of output time steps)
        """
        # the spectogram outputs  and we want (Tx, freqs) to input into the model
        x  = x.swapaxes(0,1)
        x = np.expand_dims(x, axis=0)
        predictions = self.model.predict(x)
        return predictions.reshape(-1)

    def has_new_triggerword(self, predictions, chunk_duration, feed_duration, threshold=0.5):
        """
        Function to detect new trigger word in the latest chunk of input audio.
        It is looking for the rising edge of the predictions data belongs to the
        last/latest chunk.
        
        Argument:
        predictions -- predicted labels from model
        chunk_duration -- time in second of a chunk
        feed_duration -- time in second of the input to model
        threshold -- threshold for probability above a certain to be considered positive

        Returns:
        True if new trigger word detected in the latest chunk
        """
        predictions = predictions > threshold
        chunk_predictions_samples = int(len(predictions) * CHUNK_DURATION / FEED_DURATION)
        chunk_predictions = predictions[-chunk_predictions_samples:]
        level = chunk_predictions[0]
        for pred in chunk_predictions:
            if pred > level:
                return True
            else:
                level = pred
        return False

    def detect_trigger_word(self, data):
        spectrum = get_spectrogram(data)
        preds = self.detect_triggerword_spectrum(spectrum)
        new_trigger = self.has_new_triggerword(preds, CHUNK_DURATION, FEED_DURATION)
        return new_trigger
import os
import tensorflow as tf
from model.utils import Params
from model.model_fn import model_fn
from model.input_fn import custom_input_fn
import numpy as np

g_estimator = None
g_params = None

def initialize_estimator():
    model_dir = "experiments/base_model"
    tf.reset_default_graph()
    tf.logging.set_verbosity(tf.logging.INFO)

    # Load the parameters from json file
    json_path = os.path.join(model_dir, 'params.json')
    assert os.path.isfile(json_path), "No json configuration file found at {}".format(json_path)
    params = Params(json_path)

    # Define the model
    tf.logging.info("Creating the model...")
    config = tf.estimator.RunConfig(tf_random_seed=629,
                                    model_dir=model_dir)
    estimator = tf.estimator.Estimator(model_fn, params=params, config=config)
    return estimator, params

def get_estimator_param():
    global g_estimator
    global g_params
    if g_estimator is None or g_params is None:
        print("calculating--------------------")
        g_estimator, g_params = initialize_estimator()
    return g_estimator, g_params

def get_img_embedding(filename):
    estimator, params = get_estimator_param()
    tf.logging.info("Predicting")
    predictions = estimator.predict(lambda: custom_input_fn(filename, params))
    for i, p in enumerate(predictions):
        embedding = p['embeddings']
        break
    return embedding, params

def verify(filename, anchor_embedding):
    embedding, params = get_img_embedding(filename)

    dist = np.linalg.norm(embedding - anchor_embedding)
    print("dist", dist)
    if dist < params.verify_score:
        print("same")
        return True
    else:
        print("not same")
        return False

if __name__ == '__main__':
    filename1 = "./data/96x96_CASIA/train_faces/0000099_IMG_016.jpg"
    filename2 = "./data/96x96_CASIA/test_faces/0000099_IMG_096.jpg"
    filename3 = "./data/96x96_CASIA/test_faces/0000103_IMG_040.jpg"
    emb1, params = get_img_embedding(filename1)
    print("emb1", emb1)
    emb2, params = get_img_embedding(filename2)
    print("emb2", emb2)
    emb3, params = get_img_embedding(filename3)
    print("emb3", emb3)
    verify(filename1, emb2)
    verify(filename2, emb3)
    verify(filename1, emb3)
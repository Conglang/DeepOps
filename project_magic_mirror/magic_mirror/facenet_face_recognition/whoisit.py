# from keras.models import Sequential
# from keras.layers import Conv2D, ZeroPadding2D, Activation, Input, concatenate
# from keras.models import Model
# from keras.layers.normalization import BatchNormalization
# from keras.layers.pooling import MaxPooling2D, AveragePooling2D
# from keras.layers.merge import Concatenate
# from keras.layers.core import Lambda, Flatten, Dense
# from keras.initializers import glorot_uniform
# from keras.engine.topology import Layer

# import os
import numpy as np
from PIL import Image
# # from numpy import genfromtxt
# import pandas as pd

# from facenet_face_recognition.fr_utils import *
# from facenet_face_recognition.inception_blocks_v2 import *

def img_to_encoding(image_path, model):
    model._make_predict_function()
    print("new img to encoding", image_path)
    img1 = np.array(Image.open(image_path))
    print("step 1")
    img = img1[...,::-1]
    img = np.around(np.transpose(img, (2,0,1))/255.0, decimals=12)
    print("step 2")
    x_train = np.array([img])
    print("step 3")
    embedding = model.predict_on_batch(x_train)
    print("embedding", embedding)
    return embedding

def triplet_loss(y_true, y_pred, alpha = 0.2):
    """
    Implementation of the triplet loss as defined by formula (3)
    
    Arguments:
    y_true -- true labels, required when you define a loss in Keras, you don't need it in this function.
    y_pred -- python list containing three objects:
            anchor -- the encodings for the anchor images, of shape (None, 128)
            positive -- the encodings for the positive images, of shape (None, 128)
            negative -- the encodings for the negative images, of shape (None, 128)
    
    Returns:
    loss -- real number, value of the loss
    """
    import tensorflow as tf

    anchor, positive, negative = y_pred[0], y_pred[1], y_pred[2]
    
    # Step 1: Compute the (encoding) distance between the anchor and the positive, you will need to sum over axis=-1
    pos_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, positive)))
    # Step 2: Compute the (encoding) distance between the anchor and the negative, you will need to sum over axis=-1
    neg_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, negative)))
    # Step 3: subtract the two previous distances and add alpha.
    basic_loss = tf.add(tf.subtract(pos_dist, neg_dist), alpha)
    # Step 4: Take the maximum of basic_loss and 0.0. Sum over the training examples.
    loss = tf.reduce_sum(tf.maximum(basic_loss, 0.0))
    
    return loss

def load_model():
    from keras import backend as K
    K.set_image_data_format('channels_first')
    from facenet_face_recognition.fr_utils import load_weights_from_FaceNet
    from facenet_face_recognition.inception_blocks_v2 import faceRecoModel
    FRmodel = faceRecoModel(input_shape=(3, 96, 96))
    FRmodel.compile(optimizer = 'adam', loss = triplet_loss, metrics = ['accuracy'])
    load_weights_from_FaceNet(FRmodel)
    FRmodel._make_predict_function()
    return FRmodel

import tensorflow as tf
FRmodel = load_model()

graph = tf.get_default_graph()


def get_embedding(image_path):
    return img_to_encoding(image_path, FRmodel)


def who_is_it(image_path, database):
    from keras import backend as K
    K.set_image_data_format('channels_first')

    print("image_path", image_path)
    print("database", database)
    """
    Implements face recognition for the happy house by finding who is the person on the image_path image.
    
    Arguments:
    image_path -- path to an image
    database -- database containing image encodings along with the name of the person on the image
    model -- your Inception model instance in Keras
    
    Returns:
    min_dist -- the minimum distance between image_path encoding and the encodings from the database
    identity -- string, the name prediction for the person on image_path
    """
    global FRmodel
    model = FRmodel

    identity = None
    global graph
    # with graph.as_default():
    ## Step 1: Compute the target "encoding" for the image. Use img_to_encoding() see example above. ## (≈ 1 line)
    encoding = img_to_encoding(image_path, model)
    
    ## Step 2: Find the closest encoding ##
    
    # Initialize "min_dist" to a large value, say 100 (≈1 line)
    min_dist = 100
    
    # Loop over the database dictionary's names and encodings.
    for (id, db_enc) in database.items():
        
        # Compute L2 distance between the target "encoding" and the current "emb" from the database. (≈ 1 line)
        dist = np.linalg.norm(encoding - db_enc)

        # If this distance is less than the min_dist, then set min_dist to dist, and identity to name. (≈ 3 lines)
        if dist < min_dist:
            min_dist = dist
            identity = id
    
    if min_dist > 0.7:
        print("Not in the database.")
    else:
        print ("it's " + str(identity) + ", the distance is " + str(min_dist))
    return min_dist, identity, encoding
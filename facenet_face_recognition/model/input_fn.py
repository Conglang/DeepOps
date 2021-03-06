"""Create the input data pipeline using `tf.data`"""

import tensorflow as tf
import os

#import model.mnist_dataset as mnist_dataset


# def train_input_fn(data_dir, params):
#     """Train input function for the MNIST dataset.

#     Args:
#         data_dir: (string) path to the data directory
#         params: (Params) contains hyperparameters of the model (ex: `params.num_epochs`)
#     """
#     dataset = mnist_dataset.train(data_dir)
#     dataset = dataset.shuffle(params.train_size)  # whole dataset into the buffer
#     dataset = dataset.repeat(params.num_epochs)  # repeat for multiple epochs
#     dataset = dataset.batch(params.batch_size)
#     dataset = dataset.prefetch(1)  # make sure you always have one batch ready to serve
#     return dataset


# def test_input_fn(data_dir, params):
#     """Test input function for the MNIST dataset.

#     Args:
#         data_dir: (string) path to the data directory
#         params: (Params) contains hyperparameters of the model (ex: `params.num_epochs`)
#     """
#     dataset = mnist_dataset.test(data_dir)
#     dataset = dataset.batch(params.batch_size)
#     dataset = dataset.prefetch(1)  # make sure you always have one batch ready to serve
#     return dataset

def _parse_function(filename, label, size):
    """Obtain the image from the filename (for both training and validation).

    The following operations are applied:
        - Decode the image from jpeg format
        - Convert to float and to range [0, 1]
    """
    image_string = tf.read_file(filename)

    # Don't use tf.image.decode_image, or the output shape will be undefined
    image_decoded = tf.image.decode_jpeg(image_string, channels=3)

    # This will convert to float values in [0, 1]
    image = tf.image.convert_image_dtype(image_decoded, tf.float32)

    resized_image = tf.image.resize_images(image, [size, size])

    return resized_image, label

def train_preprocess(image, label, use_random_flip):
    """Image preprocessing for training.

    Apply the following operations:
        - Horizontally flip the image with probability 1/2
        - Apply random brightness and saturation
    """
    if use_random_flip:
        image = tf.image.random_flip_left_right(image)

    image = tf.image.random_brightness(image, max_delta=32.0 / 255.0)
    image = tf.image.random_saturation(image, lower=0.5, upper=1.5)

    # Make sure the image is still in [0, 1]
    image = tf.clip_by_value(image, 0.0, 1.0)

    return image, label

def grayscale(image, label):
    image = tf.image.rgb_to_grayscale(image)
    return image, label

def input_fn(is_training, filenames, labels, params):
    """Input function for the SIGNS dataset.

    The filenames have format "{label}_IMG_{id}.jpg".
    For instance: "data_dir/2_IMG_4584.jpg".

    Args:
        is_training: (bool) whether to use the train or test pipeline.
                     At training, we shuffle the data and have multiple epochs
        filenames: (list) filenames of the images, as ["data_dir/{label}_IMG_{id}.jpg"...]
        labels: (list) corresponding list of labels
        params: (Params) contains hyperparameters of the model (ex: `params.num_epochs`)
    """
    num_samples = len(filenames)
    assert len(filenames) == len(labels), "Filenames and labels should have same length"

    # Create a Dataset serving batches of images and labels
    # We don't repeat for multiple epochs because we always train and evaluate for one epoch
    parse_fn = lambda f, l: _parse_function(f, l, params.image_size)
    train_fn = lambda f, l: train_preprocess(f, l, params.use_random_flip)
    gray_fn = lambda f, l: grayscale(f, l)

    if is_training:
        dataset = (tf.data.Dataset.from_tensor_slices((tf.constant(filenames), tf.constant(labels)))
            .shuffle(num_samples)  # whole dataset into the buffer ensures good shuffling
            .map(parse_fn, num_parallel_calls=params.num_parallel_calls)
            .map(train_fn, num_parallel_calls=params.num_parallel_calls)
            .map(gray_fn, num_parallel_calls=params.num_parallel_calls)
            .repeat(params.num_epochs)
            .batch(params.batch_size)
            .prefetch(1)  # make sure you always have one batch ready to serve
        )
    else:
        dataset = (tf.data.Dataset.from_tensor_slices((tf.constant(filenames), tf.constant(labels)))
            .map(parse_fn)
            .map(gray_fn, num_parallel_calls=params.num_parallel_calls)
            .batch(params.batch_size)
            .prefetch(1)  # make sure you always have one batch ready to serve
        )

    # Create reinitializable iterator from dataset
    # iterator = dataset.make_initializable_iterator()
    # images, labels = iterator.get_next()
    # iterator_init_op = iterator.initializer

    # inputs = {'images': images, 'labels': labels, 'iterator_init_op': iterator_init_op}
    return dataset

def train_datas(data_dir):
    train_data_dir = os.path.join(data_dir, "train_faces")
    # Get the filenames from the train sets
    train_filenames = [os.path.join(train_data_dir, f) for f in os.listdir(train_data_dir)
                       if f.endswith('.jpg')]
    # Labels
    train_labels = [int(f.split('/')[-1].split('_')[0]) for f in train_filenames]
    return train_filenames, train_labels

def train_input_fn(data_dir, params):
    train_filenames, train_labels = train_datas(data_dir)
    # Specify the sizes of the dataset we train on and evaluate on
    params.train_size = len(train_filenames)
    # Create the iterator
    return input_fn(True, train_filenames, train_labels, params)

def test_datas(data_dir):
    test_data_dir = os.path.join(data_dir, "test_faces")
    # Get the filenames from the test sets
    test_filenames = [os.path.join(test_data_dir, f) for f in os.listdir(test_data_dir)
                       if f.endswith('.jpg')]
    # Labels
    test_labels = [int(f.split('/')[-1].split('_')[0]) for f in test_filenames]
    return test_filenames, test_labels

def test_input_fn(data_dir, params):
    test_filenames, test_labels = test_datas(data_dir)
    # Specify the sizes of the dataset we test on and evaluate on
    params.test_size = len(test_filenames)
    # Create the iterator
    return input_fn(False, test_filenames, test_labels, params)
import argparse
import random
import os

from PIL import Image
from tqdm import tqdm

SIZE = 250

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default='data/CASIA-maxpy-clean', help="Directory with the CASIA dataset")
parser.add_argument('--output_dir', default='data/250x250_CASIA', help="Where to write the new data")

def grayscale(picture):
    res = Image.new(picture.mode, picture.size)
    width, height = picture.size
    for i in range(0, width):
        for j in range(0, height):
            pixel=picture.getpixel((i,j))
            red= pixel[0]
            green= pixel[1]
            blue= pixel[2]
            gray = (int)((red + green + blue)/3)
            res.putpixel((i,j), (gray, gray, gray))
    return res

def get_all_jpg_files_of_path(rootdir):
    filenames = []
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if filename.endswith(".jpg"):
                filenames.append(os.path.join(folder, filename))
    return filenames


def resize_and_save(filename, output_dir, size=SIZE):
    """Resize the image contained in `filename` and save it to the `output_dir`"""
    image = Image.open(filename)
    # Use bilinear interpolation instead of the default "nearest neighbor" method
    image = image.resize((size, size), Image.BILINEAR)
    #image = grayscale(image)
    to_filename = filename.split('/')[-2] + "_IMG_" + filename.split('/')[-1]
    image.save(os.path.join(output_dir, to_filename))


if __name__ == '__main__':
    args = parser.parse_args()

    assert os.path.isdir(args.data_dir), "Couldn't find the dataset at {}".format(args.data_dir)

    # Define the data directories
    data_dir = args.data_dir

    # Get the filenames in each directory (train and test)
    filenames = get_all_jpg_files_of_path(data_dir)
    
    # Split the images in 'train_faces' into 20% test and 80% train
    # Make sure to always shuffle with a fixed seed so that the split is reproducible
    random.seed(629)
    filenames.sort()
    random.shuffle(filenames)

    split = int(0.8 * len(filenames))
    train_filenames = filenames[:split]
    test_filenames = filenames[split:]

    filenames = {'train': train_filenames,
                 'test': test_filenames}

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    else:
        print("Warning: output dir {} already exists".format(args.output_dir))

    # Preprocess train, dev and test
    for split in ['train', 'test']:
        output_dir_split = os.path.join(args.output_dir, '{}_faces'.format(split))
        if not os.path.exists(output_dir_split):
            os.mkdir(output_dir_split)
        else:
            print("Warning: dir {} already exists".format(output_dir_split))

        print("Processing {} data, saving preprocessed data to {}".format(split, output_dir_split))
        for filename in tqdm(filenames[split]):
            resize_and_save(filename, output_dir_split, size=SIZE)

    print("Done building dataset")
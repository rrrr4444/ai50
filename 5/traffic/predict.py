import tensorflow as tf
import numpy as np
import cv2
import sys
import os

from sklearn.model_selection import train_test_split

IMG_WIDTH = 30
IMG_HEIGHT = 30
MODEL = "model"
DATA = "gtsrb"

# to disable annoying tensorflow logging
# level 1 stops info messages but allows warnings, errors
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_image(image):
    image = cv2.imread(image)
    image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT), 3)
    return [image]


def main():
    # load saved tensorflow model
    model = tf.keras.models.load_model(MODEL)
    # get an image array from image specified in cmd arg
    images = load_image(sys.argv[1])
    # get prediction array from model
    prediction = model.predict(np.array(images), batch_size=1)
    # turn 1D array into list
    prediction = prediction[0].tolist()

    for i in range(5):
        max_value = max(prediction)
        if max_value > .95:
            color = bcolors.GREEN
        elif max_value > .0001:
            color = bcolors.YELLOW
        else:
            color = bcolors.RED
        print(color, prediction.index(max_value), " - ", max_value, bcolors.ENDC)
        prediction[prediction.index(max_value)] = 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(bcolors.RED, "Specify image path", bcolors.ENDC)
    elif os.path.exists(sys.argv[1]):
        main()
    else:
        print(bcolors.RED, "Image does not exist", bcolors.ENDC)


import tensorflow as tf
import numpy as np

from sklearn.model_selection import train_test_split

import traffic

MODEL = "model"
DATA = "gtsrb"

model = tf.keras.models.load_model(MODEL)

images, labels = traffic.load_data(DATA)

labels = tf.keras.utils.to_categorical(labels)

model.evaluate(np.array(images),  np.array(labels), verbose=2)

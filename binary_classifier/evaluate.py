from __future__ import absolute_import, division, print_function, unicode_literals
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress tensorflow messages
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras
import tensorflow_datasets as tfds
import numpy as np
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from sklearn.metrics import confusion_matrix

print("Version: ", tf.__version__)
print("Eager mode: ", tf.executing_eagerly())
print("Hub version: ", hub.__version__)
print(tf.config.list_physical_devices())

mpl.rcParams['figure.figsize'] = (12, 10)
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

# load and process data input into tensors
def load_data(split = 0.8):
    # generate path names
    feature_path = 'data/features.txt'
    label_path = 'data/labels.txt'
    # open both feature and label files
    # read data into python lists
    with open(feature_path, 'r', encoding = 'utf8') as features, open(label_path, 'r', encoding = 'utf8') as labels:
        x, y = list(), list()
        for line in labels:
            y.append(int(line.strip()))
        y_count = len(y)

        feature = ''
        x_count = 0
        for line in features:
            # once features count match labels count, stop reading features
            if x_count == y_count:
                break
            if '<<END>>' in line:
                x.append(feature)
                feature = ''
                x_count += 1
            else:
                feature += line
    # display features and labels quantities
    print('\nDetecting {} labels'.format(y_count))
    print('Reading {} features\n'.format(x_count))

    # validate that features and labels match
    assert len(x) == len(y), 'Error: features and labels mismatch'

    # count positives and negatives from dataset
    pos, neg = 0, 0
    for c in y:
        if c == 1:
            pos += 1
        else:
            neg += 1
    print('Detecting {} negatives'.format(neg))
    print('Detecting {} positives ({:.2f}% of total)'.format(pos, 100 * pos / (pos + neg)))

    # split dataset into train and val based on split ratio (shuffled already completed by merge.py)
    # convert python lists to tf.tensors
    print('\nSplit ratio at {}'.format(split))

    split_point = int(round(len(y) * split))

    x_train = tf.convert_to_tensor(x[:split_point], dtype = tf.string)
    y_train = tf.convert_to_tensor(y[:split_point], dtype = tf.float32)
    print('{} training data pairs'.format(len(y_train)))

    x_val = tf.convert_to_tensor(x[split_point:], dtype = tf.string)
    y_val = tf.convert_to_tensor(y[split_point:], dtype = tf.float32)
    print('{} validation data pairs\n'.format(len(y_val)))

    # return
    return x_train, y_train, x_val, y_val, pos, neg

x_train, y_train, x_val, y_val, pos, neg = load_data()

# build model
def model():
    # import Google's USE DAN module
    url = 'https://tfhub.dev/google/universal-sentence-encoder/4'

    universal_sentence_encoder = hub.KerasLayer(
        url,
        output_shape = [512],
        input_shape = [],
        dtype = tf.string
    )

    # define model
    model = keras.Sequential([
        universal_sentence_encoder,
        keras.layers.Dense(512, activation = 'relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(512, activation = 'relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(512, activation = 'relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(512, activation = 'relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(1, activation = 'sigmoid')
    ])
    model.summary()

    # compile model with many metrics
    model.compile(
        optimizer = 'adam',
        loss = 'binary_crossentropy',
        metrics = [
            keras.metrics.TruePositives(name = 'tp'),
            keras.metrics.FalsePositives(name = 'fp'),
            keras.metrics.TrueNegatives(name = 'tn'),
            keras.metrics.FalseNegatives(name = 'fn'),
            keras.metrics.BinaryAccuracy(name = 'accuracy'),
            keras.metrics.Precision(name = 'precision'),
            keras.metrics.Recall(name = 'recall'),
            keras.metrics.AUC(name = 'auc')
        ]
    )
    return model

model = model()

# laod weights
checkpoint_path = 'weights/W'
try:
    model.load_weights(checkpoint_path)
    print('Weights detected.')
except:
    print('No weights detected.')

# evaluate model
confidence_threshold = 0.94

def plot_confusion_matrix(labels, predictions, p = confidence_threshold):
    cm = confusion_matrix(labels, predictions > p)
    plt.figure(figsize = (5, 5))
    sns.heatmap(cm, annot = True, fmt = 'd')
    plt.title('Confusion Matrix @{:.2f}'.format(p))
    plt.ylabel('Actual label')
    plt.xlabel('Predicted label')

    print()
    for name, value in zip(model.metrics_names, predictions):
        print(name, ': ', value)
    print()

    print('Uninteresting jobs suppressed (true negatives): {}'.format(cm[0][0]))
    print('Uninteresting jobs falsely passed (false positives): {}'.format(cm[0][1]))
    print('Interesting jobs falsely suppressed (false negatives): {}'.format(cm[1][0]))
    print('Interesting jobs passed (true positives): {}'.format(cm[1][1]))
    print('Total interesting jobs in dataset: {}'.format(np.sum(cm[1])))

    plt.show()

# model.evaluate(x_val, y_val)
results = model.predict(x_val)
plot_confusion_matrix(y_val, results)

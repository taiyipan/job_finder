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

# human controls
TRAIN = False
EVALUATE = False
EPOCHS = 100 # it will never reach 100 due to early stopping
BATCH_SIZE = 1024 # increase batch size if dataset is large and sparse

print('\nEpochs set to {}'.format(EPOCHS))
print('Batch size set to {}'.format(BATCH_SIZE))
if not TRAIN:
    print('Skipping training')
if not EVALUATE:
    print('Skipping evaluation')

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
    # set output_bias to speed up initial training
    initial_bias = np.log([pos / neg])
    output_bias = keras.initializers.Constant(initial_bias)
    print('\nSetting initial bias on output layer to {} to speed up initial epochs\n'.format(initial_bias))

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
        keras.layers.Dense(1, activation = 'sigmoid', bias_initializer = output_bias)
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

# define save weights callback
checkpoint_path = 'weights/W'
checkpoint_callback = keras.callbacks.ModelCheckpoint(
    checkpoint_path,
    save_weights_only = True
)

try:
    model.load_weights(checkpoint_path)
    print('Weights detected.')
except:
    print('No weights detected.')

# define tensorboard callback
root_logdir = os.path.join(os.curdir, 'logs')

def get_run_logdir():
    run_id = time.strftime('run_%Y_%m_%d-%H_%M_%S')
    return os.path.join(root_logdir, run_id)
run_logdir = get_run_logdir()

tensorboard_callback = keras.callbacks.TensorBoard(run_logdir)

# define nan callback
nan_callback = keras.callbacks.TerminateOnNaN()

# define early stop callback
early_stop_callback = keras.callbacks.EarlyStopping(
    monitor = 'val_auc',
    verbose = 1,
    patience = 10,
    mode = 'max',
    restore_best_weights = True
)

# calculate class weights
weight_for_0 = (1 / neg) * (pos + neg) / 2.0
weight_for_1 = (1 / pos) * (pos + neg) / 2.0

print('\nDifferentiating class weights to compensate for unbalanced dataset')
print('Weight for class 0: {:.2f}'.format(weight_for_0))
print('Weight for class 1: {:.2f}\n'.format(weight_for_1))

class_weight = {0: weight_for_0, 1: weight_for_1}

# train model
if TRAIN:
    model.fit(
        x_train, y_train,
        batch_size = BATCH_SIZE,
        epochs = EPOCHS,
        validation_data = (x_val, y_val),
        callbacks = [
            checkpoint_callback,
            tensorboard_callback,
            nan_callback,
            early_stop_callback
        ],
        class_weight = class_weight
    )

# evaluate model
def plot_confusion_matrix(labels, predictions, p = 0.5):
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

if EVALUATE:
    model.evaluate(x_val, y_val)
    results = model.predict(x_val, batch_size = BATCH_SIZE)
    plot_confusion_matrix(y_val, results)

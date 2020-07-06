from __future__ import absolute_import, division, print_function, unicode_literals
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress tensorflow messages
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras

print("Version: ", tf.__version__)
print("Eager mode: ", tf.executing_eagerly())
print("Hub version: ", hub.__version__)
print(tf.config.list_physical_devices())

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

    # define model: hypertuned by Keras Tuner's Hyperband algorithm
    # hyperparams tuned: num_hidden_layers, dense_units, dropout_rates
    model = keras.Sequential([
        # input encoder
        universal_sentence_encoder,
        # block 1
        keras.layers.Dense(928, activation = 'relu'),
        keras.layers.Dropout(0.4),
        # block 2
        keras.layers.Dense(928, activation = 'relu'),
        keras.layers.Dropout(0.5),
        # block 3
        keras.layers.Dense(800, activation = 'relu'),
        keras.layers.Dropout(0.2),
        # block 4
        keras.layers.Dense(544, activation = 'relu'),
        keras.layers.Dropout(0.2),
        # output sigmoid activation with initialized bias
        keras.layers.Dense(1, activation = 'sigmoid')
    ])
    model.summary()

    # compile model with many metrics
    model.compile(
        optimizer = keras.optimizers.Adam(learning_rate = 0.001), # hypertuned learning rate
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

# save model
model_version = '4'
model_name = 'job_finder'
model_path = os.path.join(model_name, model_version)
tf.saved_model.save(model, model_path)
print('Model saved')

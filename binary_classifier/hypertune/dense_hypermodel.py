import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress tensorflow messages
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow_hub as hub
import kerastuner as kt
from kerastuner import HyperModel
import numpy as np

# derive subclass from HyperModel class
class DenseHyperModel(HyperModel):
    def __init__(self, pos: int, neg: int):
        self.pos = pos
        self.neg = neg
    # required to implement build method
    def build(self, hp):
        model = keras.Sequential()
        # add input layer
        model.add(layers.InputLayer(input_shape = (512), dtype = tf.float32))
        # tune number of hidden layers and number of units per hidden layer
        for i in range(hp.Int('num_hidden_layers', min_value = 1, max_value = 10)):
            model.add(layers.Dense(
                units = hp.Int(
                    'hidden_layer_{}_units'.format(str(i)),
                    min_value = 32,
                    max_value = 1024,
                    step = 32
                ),
                activation = 'relu'
            ))
            model.add(layers.Dropout(
                rate = hp.Float(
                    'hidden_layer_{}_dropout'.format(str(i)),
                    min_value = 0.1,
                    max_value = 0.7,
                    step = 0.1
                )
            ))
        model.add(layers.Dense(
            1, activation = 'sigmoid',
            bias_initializer = keras.initializers.Constant(np.log([self.pos / self.neg]))
        ))
        # tune learning rate
        model.compile(
            optimizer = keras.optimizers.Adam(hp.Choice(
                'learning_rate',
                values = [1e-2, 1e-3, 1e-4]
            )),
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

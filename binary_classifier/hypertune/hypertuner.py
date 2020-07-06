import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress tensorflow messages
import tensorflow as tf
from tensorflow import keras
import kerastuner as kt
from dense_hypermodel import DenseHyperModel
from preprocessor import Preprocessor
from batcher import Batcher

class Hypertuner:
    def __init__(self):
        preprocessor = Preprocessor()
        preprocessor.load_data()
        self.x_train = preprocessor.get_x_train()
        self.y_train = preprocessor.get_y_train()
        self.x_val = preprocessor.get_x_val()
        self.y_val = preprocessor.get_y_val()
        self.pos = preprocessor.get_pos()
        self.neg = preprocessor.get_neg()
        self.hyper_model = DenseHyperModel(self.pos, self.neg)
        self.tuner = None
        self.batch_size = 1024
        self.epochs = 100
        self.batcher = Batcher()
        self.objective = 'val_auc'

    def early_stop_callback(self):
        return keras.callbacks.EarlyStopping(
            monitor = 'val_auc',
            verbose = 1,
            patience = 3,
            mode = 'max',
            restore_best_weights = True
        )

    def nan_callback(self):
        return keras.callbacks.TerminateOnNaN()

    def process_input(self):
        self.x_train = self.batcher.batch_predict(self.x_train)
        self.x_val = self.batcher.batch_predict(self.x_val)

    def pretune(self):
        # instantiate hyberband tuner
        self.tuner = kt.Hyperband(
            self.hyper_model,
            objective = kt.Objective(self.objective, direction = 'max'),
            max_epochs = self.epochs,
            factor = 3,
            directory = self.objective,
            project_name = 'hypertune'
        )

    def hypertune(self):
        # calculate class weights
        weight_for_0 = (1 / self.neg) * (self.pos + self.neg) / 2.0
        weight_for_1 = (1 / self.pos) * (self.pos + self.neg) / 2.0
        class_weight = {0: weight_for_0, 1: weight_for_1}

        self.tuner.search(
            self.x_train,
            self.y_train,
            batch_size = self.batch_size,
            epochs = self.epochs,
            validation_data = (self.x_val, self.y_val),
            callbacks = [
                self.early_stop_callback(),
                self.nan_callback()
            ],
            class_weight = class_weight
        )

    def evaluate(self):
        self.tuner.results_summary()
        models = self.tuner.get_best_models(num_models = 10)
        for i in range(10):
            print('\nModel {}\n'.format(i + 1))
            models[i].summary()
            models[i].evaluate(self.x_val, self.y_val)

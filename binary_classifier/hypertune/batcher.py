import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress tensorflow messages
import tensorflow as tf
import numpy as np
from oracle import Oracle
# implement batched prediction so remote tensorflow model doesn't get overwhelmed by large quantities of input data
class Batcher:
    def __init__(self, batch_size = 1024):
        self.batch_size = batch_size
        self.oracle = Oracle()

    def set_batch_size(self, batch_size: int):
        self.batch_size = batch_size

    # make predictions one batch at a time, then aggregate the results and return
    def batch_predict(self, input_data):
        output = list()
        while input_data:
            batch = self.next_batch(input_data)
            output.append(self.oracle.query(batch))
        output = np.concatenate(output)
        print('{} results predicted'.format(len(output)))
        return tf.convert_to_tensor(output, dtype = tf.float32)

    # pop off a batch from the beginning and return
    # if no more data, return None
    def next_batch(self, input_data) -> list:
        batch = list()
        for i in range(self.batch_size):
            if input_data:
                batch.append(input_data.pop(0))
            else:
                break
        return batch

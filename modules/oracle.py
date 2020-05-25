import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress tensorflow messages
import tensorflow as tf
from tensorflow import keras
import numpy as np
import grpc
from credential import Credential
from tensorflow_serving.apis.predict_pb2 import PredictRequest
from tensorflow_serving.apis import prediction_service_pb2_grpc
# query tensorflow server and output response
class Oracle:
    def __init__(self):
        self.name = 'job_finder'
        self.signature_name = 'serving_default'
        self.input_name = 'keras_layer_input'
        self.output_name = 'dense_4'

    def prepare_request(self, input_data):
        request = PredictRequest()
        request.model_spec.name = self.name
        request.model_spec.signature_name = self.signature_name
        request.inputs[self.input_name].CopyFrom(
            tf.make_tensor_proto(
                tf.convert_to_tensor(
                    input_data,
                    dtype = tf.string
                )
            )
        )
        return request

    def send_query(self, input_data):
        try:
            credentials = Credential()
            server_address = credentials.server_address()
            print('\nSending input data to remote tensorflow server at {}'.format(server_address))
            channel = grpc.insecure_channel(server_address)
            predict_service = prediction_service_pb2_grpc.PredictionServiceStub(channel)
            response = predict_service.Predict(
                self.prepare_request(input_data),
                timeout = 10.0
            )
            print('Response from remote server received')
            return response
        except:
            # if tensorflow server isn't responding, send error report through email and quit program
            print('\nRemote tensorflow server not responding')
            return None

    def process_response(self, response):
        if response is None:
            return None 
        output_proto = response.outputs[self.output_name]
        output = np.squeeze(
            tf.make_ndarray(output_proto)
        )
        print('\nObtained {} results'.format(len(output)))
        return output

    def query(self, input_data):
        return self.process_response(
            self.send_query(input_data)
        )

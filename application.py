from datetime import datetime
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from flask_restplus import Api, Resource, fields
from flask import Flask, request, jsonify
import numpy as np
from werkzeug.datastructures import FileStorage
from PIL import Image
from keras.models import model_from_json
import tensorflow as tf

from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("firebase.json")
firebase_app = initialize_app(cred)
database = firestore.client()
requests_ref = database.collection('requests')

application = Flask(__name__)
api = Api(application, version='1.0', title='MNIST Classification',
          description='CNN for Mnist')
ns = api.namespace('Make_School', description='Methods')

single_parser = api.parser()
single_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)

model = load_model("my_model.h5")
graph = tf.get_default_graph()


@ns.route('/prediction')
class CNNPrediction(Resource):
    """Uploads your data to the CNN"""
    @api.doc(parser=single_parser, description='Upload an mnist image')
    def post(self):
        args = single_parser.parse_args()
        image_file = args.file
        image_file.save('milad.png')
        img = Image.open('milad.png')
        image_red = img.resize((28, 28))
        image = img_to_array(image_red)
        x = image.reshape(1, 28, 28, 1)
        x = x/255

        with graph.as_default():
            out = model.predict(x)

        r = np.argmax(out[0])

        requests_ref.document().set({
            'date': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            'image': str(image_file),
            'prediction': str(r)
        })

        return {'prediction': str(r)}


if __name__ == '__main__':
    application.run()

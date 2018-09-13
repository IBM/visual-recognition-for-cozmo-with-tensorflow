# Copyright 2018 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import flask
import base64
import numpy               as     np
import tensorflow          as     tf
import ibm_boto3
from   ibm_botocore.client import Config
import urllib.request

app       = flask.Flask(__name__)
app.debug = False
graph     = tf.Graph()
labels    = []
modelNeedsToBeLoaded = True

@app.route('/classify', methods=['GET'])
def classify():
    global modelNeedsToBeLoaded
    try:
        if (modelNeedsToBeLoaded == True):
            modelNeedsToBeLoaded = False
            init()            

        imageUrl = flask.request.args.get('image-url', '')
        file_name, headers = urllib.request.urlretrieve(imageUrl)
        file_reader = tf.read_file(file_name, "file_reader")

    except Exception as err:
        response = flask.jsonify({'error': 'Issue with Object Storage credentials or with image URL'})
        response.status_code = 400
        return response
    
    image_reader     = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')
    float_caster     = tf.cast(image_reader, tf.float32)
    dims_expander    = tf.expand_dims(float_caster, 0)
    resized          = tf.image.resize_bilinear(dims_expander, [224, 224])
    normalized       = tf.divide(tf.subtract(resized, [128]), [128])
    input_operation  = graph.get_operation_by_name("import/input")
    output_operation = graph.get_operation_by_name("import/final_result")
    tf_picture       = tf.Session().run(normalized)

    with tf.Session(graph=graph) as sess:
        results = np.squeeze(sess.run(output_operation.outputs[0], {input_operation.outputs[0]: tf_picture}))
        index   = results.argsort()
        answer  = {}

        for i in index:
            answer[labels[i]] = float(results[i])

        response = flask.jsonify(answer)
        response.status_code = 200

    return response

@app.route('/init', methods=['POST'])
def init():
    try:

        message = flask.request.get_json(force=True, silent=True)

        if message and not isinstance(message, dict):
            flask.abort(404)

        cos = ibm_boto3.resource('s3',
			ibm_api_key_id='apikey',
			ibm_service_instance_id='resource_instance_id',
			ibm_auth_endpoint='https://iam.bluemix.net/oidc/token',
			config=Config(signature_version='oauth'),
			endpoint_url='https://s3-api.us-geo.objectstorage.softlayer.net')

        obj       = cos.Object("tensorflow", "retrained_graph_cozmo.pb").get()
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(obj["Body"].read())
        with graph.as_default():
            tf.import_graph_def(graph_def)

        obj    = cos.Object("tensorflow", "retrained_labels_cozmo.txt").get()
        for i in obj["Body"].read().decode("utf-8").split():
            labels.append(i)

    except Exception as e:
        print("Error in downloading content")
        print(e)
        response = flask.jsonify({'error downloading models': e})
        response.status_code = 512

    return ('OK', 200)


@app.route('/run', methods=['POST'])
def run():

    def error():
        response = flask.jsonify({'error': 'The action did not receive a dictionary as an argument.'})
        response.status_code = 404
        return response

    message = flask.request.get_json(force=True, silent=True)

    if message and not isinstance(message, dict):
        return error()
    else:
        args = message.get('value', {}) if message else {}

        if not isinstance(args, dict):
            return error()

        print(args)

        if "payload" not in args:
            return error()

        print("=====================================")
        with open("/test.jpg", "wb") as f:
            f.write(base64.b64decode(args['payload']))

        file_reader      = tf.read_file("/test.jpg", "file_reader")
        #file_reader      = tf.decode_base64(args['payload'])
        image_reader     = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')
        float_caster     = tf.cast(image_reader, tf.float32)
        dims_expander    = tf.expand_dims(float_caster, 0)
        resized          = tf.image.resize_bilinear(dims_expander, [224, 224])
        normalized       = tf.divide(tf.subtract(resized, [128]), [128])
        input_operation  = graph.get_operation_by_name("import/input")
        output_operation = graph.get_operation_by_name("import/final_result")
        tf_picture       = tf.Session().run(normalized)

        with tf.Session(graph=graph) as sess:
            results = np.squeeze(sess.run(output_operation.outputs[0], {input_operation.outputs[0]: tf_picture}))
            index   = results.argsort()
            answer  = {}

            for i in index:
                answer[labels[i]] = float(results[i])

            response = flask.jsonify(answer)
            response.status_code = 200

    return response


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PROXY_PORT', 8080))
    app.run(host='0.0.0.0', port=port)

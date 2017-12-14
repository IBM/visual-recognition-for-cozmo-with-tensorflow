# Visual Recognition for Anki Cozmo with TensorFlow

The [Anki Cozmo](https://www.anki.com/cozmo) robot can recognize [faces](http://cozmosdk.anki.com/docs/generated/cozmo.faces.html) and [objects](http://cozmosdk.anki.com/docs/generated/cozmo.objects.html) like Cozmo's Power Cubes which have markers on them. This [project](https://github.com/nheidloff/visual-recognition-for-cozmo-with-tensorflow) contains sample code so that Cozmo can recognize other types of objects via [TensorFlow](https://www.tensorflow.org/).

Watch the [video](https://www.youtube.com/user/nheidloff) and check out the [slides](https://www.slideshare.net/niklasheidloff/visual-recognition-with-anki-cozmo-and-tensorflow-84050740) to see how Cozmo can recognize three different toys:

[![Video](https://github.com/nheidloff/visual-recognition-for-cozmo-with-tensorflow/raw/master/screenshots/slideshare.png)](https://www.slideshare.net/niklasheidloff/visual-recognition-with-anki-cozmo-and-tensorflow-84050740)

Authors: 

* Niklas Heidloff [@nheidloff](http://twitter.com/nheidloff)
* Ansgar Schmidt [@ansi](https://ansi.23-5.eu/)


## Documentation

The training is done via TensorFlow and a retrained MobileNet model on Kubernetes.

![alt text](https://github.com/nheidloff/visual-recognition-for-cozmo-with-tensorflow/raw/master/screenshots/architecture-1.png "Training")

The classification is done via Tensorflow running in an [OpenWhisk](https://www.ibm.com/cloud/functions) function.

![alt text](https://github.com/nheidloff/visual-recognition-for-cozmo-with-tensorflow/raw/master/screenshots/architecture-2.png "Classification")

For more details check out the blog entries from Ansgar and me:

* [Sample Application to classify Images with TensorFlow and OpenWhisk](https://heidloff.net/article/visual-recognition-tensorflow)
* [Accessing IBM Object Store from Python](https://ansi.23-5.eu/2017/11/accessing-ibm-object-store-python/)
* [Image Recognition with Tensorflow training on Kubernetes](https://ansi.23-5.eu/2017/11/image-recognition-with-tensorflow-training-on-kubernetes/)
* [Image Recognition with Tensorflow classification on OpenWhisk](https://ansi.23-5.eu/2017/11/image-recognition-tensorflow-classification-openwhisk/)
* [Visual Recognition with TensorFlow and OpenWhisk](http://heidloff.net/article/visual-recognition-tensorflow-openwhisk)


## Prerequisites

Install the [Cozmo SDK](http://cozmosdk.anki.com/docs/initial.html).

Get a free [IBM Cloud lite](https://console.bluemix.net/registration/) account.

Install the [IBM Cloud/Bluemix](https://console.bluemix.net/docs/cli/index.html#downloads) CLI.

Install [Docker](https://docs.docker.com/engine/installation/).

Create a free/lite [Kubernetes cluster](https://console.bluemix.net/containers-kubernetes/catalogCluster).

Install the [Kubernetes CLI](https://kubernetes.io/docs/tasks/tools/install-kubectl/).


## 1. Take Pictures

Take pictures of an object by invoking these commands and circling Cozmo around the object for 10 seconds. Replace 'deer' with a name for your object:

```sh
$ git clone https://github.com/nheidloff/visual-recognition-for-cozmo-with-tensorflow.git
$ cd visual-recognition-for-cozmo-with-tensorflow/1-take-pictures
$ python3 take-pictures.py deer
```


## 2. Upload Pictures

Create an [IBM Object Storage](https://console.bluemix.net/catalog/infrastructure/object-storage-group) instance. Choose the lite Swift option. Read Ansgar's [blog](https://ansi.23-5.eu/2017/11/accessing-ibm-object-store-python/) for details.

Copy/remember the IBM Object Storage credentials: ‘region’, ‘projectId’, ‘userId’ and ‘password’. Paste them in [upload-pictures.py](2-upload-pictures/upload-pictures.py).

Invoke these commands:

```sh
$ cd visual-recognition-for-cozmo-with-tensorflow/2-upload-pictures
$ pip3 install python-swiftclient
$ pip3 install python-keystoneclient
$ python3 upload-pictures.py
```


## 3. Train the Model

Paste the values of ‘region’, ‘projectId’, ‘userId’ and ‘password’ in [train.yml](3-train/train.yml).

Replace 'nheidloff' with your DockerHub name and run these commands:

```sh
$ cd visual-recognition-for-cozmo-with-tensorflow/3-train
$ docker build -t nheidloff/tensorflow-openwhisk-train-cozmo:latest .
$ docker push nheidloff/tensorflow-openwhisk-train-cozmo:latest
$ bx login -a api.ng.bluemix.net
$ bx cs cluster-config mycluster
$ export KUBECONFIG=/Users/nheidlo.....
$ kubectl apply -f train.yml 
```

After this you should see the files 'retrained_graph_cozmo.pb' and 'retrained_labels_cozmo.txt' in the 'tensorflow' container in IBM Object Storage.

Read Ansgar's [blog](https://ansi.23-5.eu/2017/11/image-recognition-with-tensorflow-training-on-kubernetes/) for more details.


## 4. Deploy the Model to OpenWhisk

Paste the values of ‘region’, ‘projectId’, ‘userId’ and ‘password’ in [classifier.py](4-classify/classifier.py).

Replace 'nheidloff' with your DockerHub name and run these commands:

```sh
$ cd visual-recognition-for-cozmo-with-tensorflow/4-classify
$ docker build -t nheidloff/tensorflow-openwhisk-classifier-cozmo:latest .
$ docker push nheidloff/tensorflow-openwhisk-classifier-cozmo:latest
$ cd visual-recognition-for-cozmo-with-tensorflow/4-classify/openwhisk-api
$ bx login -a api.ng.bluemix.net
$ bx target -o <your-organization> -s <your-space>
$ bx plugin install Cloud-Functions -r Bluemix
$ wsk package create visualRecognitionCozmo
$ wsk action create visualRecognitionCozmo/tensorflow-classify --docker nheidloff/tensorflow-openwhisk-classifier-cozmo:latest
$ npm install
$ sh ./deploy.sh
$ wsk action create --sequence visualRecognitionCozmo/classifyAPI visualRecognitionCozmo/classifyImage,visualRecognitionCozmo/tensorflow-classify --web raw
```


## 5. Test the Model via the Web Application

In the [OpenWhisk web application](https://console.bluemix.net/openwhisk/manage/actions) choose your sequence and open 'Additional Details'. From there copy the URL into the clipboard. Create a new file '.env' in the '5-test-in-web-app' directory. See [.env-template](5-test-in-web-app/.env-template) for an example. Paste the URL in this file.

From the directory 'web-app' run these commands:

```sh
$ cd visual-recognition-for-cozmo-with-tensorflow/5-test-in-web-app
$ npm install
$ npm start
```
  
Open the web application via [http://localhost:3000/](http://localhost:3000/).

Optionally: In order to deploy the application to the IBM Cloud, change the application name in [manifest.yml](5-test-in-web-app/manifest.yml) to something unique and run these commands:

```sh
$ bx login -a api.ng.bluemix.net
$ bx target -o <your-organization> -s <your-space>
$ cf push
```

Open the web application via [http://your-application-name.mybluemix.net/](http://your-application-name.mybluemix.net/).


## 6. Test Visual Recognition with Cozmo

Place your object(s) in a circle around Cozmo and run these commands. Replace 'deer' with a name for your object:

```sh
$ cd visual-recognition-for-cozmo-with-tensorflow/6-play-with-cozmo
$ python3 find.py deer
```
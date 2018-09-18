#!/usr/bin/env bash

echo ${TF_MODEL}

export COS_ENDPOINT=https://s3-api.us-geo.objectstorage.softlayer.net/

aws --endpoint-url=${COS_ENDPOINT} s3 cp s3://${COS_BUCKET_NAME}/${COS_FILE_NAME} ${COS_FILE_NAME}

unzip ${COS_FILE_NAME} -d tf_files/photos

python -m scripts.retrain                            \
       --bottleneck_dir=tf_files/bottlenecks         \
       --how_many_training_steps=5000                \
       --model_dir=tf_files/models/                  \
       --summaries_dir=tf_files/training_summaries   \
       --output_graph=tf_files/retrained_graph_cozmo.pb    \
       --output_labels=tf_files/retrained_labels_cozmo.txt \
       --architecture=${TF_MODEL}                    \
       --image_dir=tf_files/photos

cd tf_files

aws --endpoint-url=${COS_ENDPOINT} s3 cp retrained_graph_cozmo.pb s3://${COS_BUCKET_NAME}/retrained_graph_cozmo.pb
aws --endpoint-url=${COS_ENDPOINT} s3 cp retrained_labels_cozmo.txt s3://${COS_BUCKET_NAME}/retrained_labels_cozmo.txt


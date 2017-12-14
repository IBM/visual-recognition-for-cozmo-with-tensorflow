#!/usr/bin/env bash

echo ${TF_MODEL}

export OS_AUTH_URL=https://identity.open.softlayer.com/v3
export OS_IDENTITY_API_VERSION=3
export OS_AUTH_VERSION=3

swift auth
swift download ${OS_BUCKET_NAME} ${OS_FILE_NAME}

unzip ${OS_FILE_NAME} -d tf_files/photos

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

swift upload tensorflow retrained_graph_cozmo.pb
swift upload tensorflow retrained_labels_cozmo.txt

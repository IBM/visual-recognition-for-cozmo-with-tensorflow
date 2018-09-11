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
import urllib.request
import shutil
import ibm_boto3
from ibm_botocore.client import Config

def upload():
    try:
        cos = ibm_boto3.resource('s3',
			ibm_api_key_id='apikey',
			ibm_service_instance_id='resource_instance_id',
			ibm_auth_endpoint='https://iam.bluemix.net/oidc/token',
			config=Config(signature_version='oauth'),
			endpoint_url='https://s3-api.us-geo.objectstorage.softlayer.net')

        zipFileName = 'cozmo-photos' 
        shutil.make_archive(zipFileName, 'zip', '../1-take-pictures/pictures')
        print("Done: Zipping Pictures") 

        container = 'tensorflow'
        cos.create_bucket(Bucket=container)            

        with open('./' + zipFileName + '.zip', 'rb') as local:            
            cos.Object(
                container,
                zipFileName + '.zip').upload_file(zipFileName + '.zip')
            print("Done: Uploading Pictures")  

    except Exception as e:
        print("Error: Uploading Pictures")
        print(e)

    return

upload()

import os
from swiftclient.service import Connection
import urllib.request
import shutil

def upload():
    try:
        conn = Connection(key='xxx',
                          authurl='https://identity.open.softlayer.com/v3',
                          auth_version='3',
                          os_options={"project_id": 'xxx',
                                      "user_id": 'xxx',
                                      "region_name": 'dallas'}
                          )       

        zipFileName = 'cozmo-photos' 
        shutil.make_archive(zipFileName, 'zip', '../take-pictures/pictures')
        print("Done: Zipping Pictures") 

        container = 'tensorflow'
        conn.put_container(container)
        resp_headers, containers = conn.get_account()            

        with open('./' + zipFileName + '.zip', 'rb') as local:            
            conn.put_object(
                container,
                zipFileName + '.zip',
                contents=local,
                content_type='application/zip'
            )  
            print("Done: Uploading Pictures")  

    except Exception as e:
        print("Error: Uploading Pictures")
        print(e)

    return

upload()
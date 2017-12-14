import asyncio
import cozmo
import requests
from cozmo.util import degrees, distance_mm, speed_mmps
import json
import time
import datetime
import os
import shutil
import sys

processing = False
takePicture = False
toy = 'deer'
foundToy = False

def parseResponse(response):
    global toy
    global foundToy
    entries = {}
    highestConfidence = 0.0
    highestEntry = ''
    for key in response.keys():        
        entries[response[key]] = key
    for key in entries.keys(): 
        if key > highestConfidence:
            highestConfidence = key
            highestEntry = entries[key]
    print('OpenWhisk responded. Highest probability: ' + highestEntry + '(' + str(highestConfidence) + ')')
    if highestConfidence > 0.8:
        if toy == highestEntry:      
            foundToy = True

def on_new_camera_image(evt, **kwargs):
    global processing
    global takePicture
    global foundToy
    if takePicture:
        if not processing:
            if not foundToy:
                processing = True            
                #print('Invoke OpenWhisk at ...')
                #print(datetime.datetime.now().time())
                #print(kwargs['image'].image_number)
                pilImage = kwargs['image'].raw_image
                pilImage.save("photos/fromcozmo-%d.jpg" % kwargs['image'].image_number, "JPEG")      
                with open("photos/fromcozmo-%d.jpg" % kwargs['image'].image_number, 'rb') as f:
                    r = requests.post('https://openwhisk.ng.bluemix.net/api/v1/web/niklas_heidloff%40de.ibm.com_dev/visualRecognitionCozmo/classifyAPI.json', files={'file1': f})
                    #print('OpenWhisk responded at: ')
                    #print(datetime.datetime.now().time())
                    #print (json.dumps(r.json(), indent=2))
                    parseResponse(r.json())
            processing = False            

def cozmo_program(robot: cozmo.robot.Robot):
    global toy
    toy = sys.argv[1]
    global takePicture
    if os.path.exists('photos'):
        shutil.rmtree('photos')
    if not os.path.exists('photos'):        
        os.makedirs('photos')
    robot.set_head_angle(degrees(10.0)).wait_for_completed()
    robot.set_lift_height(0.0).wait_for_completed()

    #time.sleep(10)

    robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)
    
    while not foundToy:        
        takePicture = False
        robot.turn_in_place(degrees(45)).wait_for_completed()
        takePicture = True
        time.sleep(2)        
    takePicture = False
    
    if foundToy:
        print ('Found toy: ' + toy + ' !!!')
        robot.drive_straight(distance_mm(200), speed_mmps(300)).wait_for_completed()
        robot.say_text("I have found the " + toy).wait_for_completed()
        anim = robot.play_anim_trigger(cozmo.anim.Triggers.MajorWin).wait_for_completed()

cozmo.run_program(cozmo_program, use_viewer=True, force_viewer_on_top=True)

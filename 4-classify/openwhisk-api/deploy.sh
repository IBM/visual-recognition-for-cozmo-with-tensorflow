#!/bin/bash
zip -rq api.zip api.js package.json node_modules
wsk action create visualRecognitionCozmo/classifyImage --kind nodejs:6 api.zip --web raw
rm api.zip

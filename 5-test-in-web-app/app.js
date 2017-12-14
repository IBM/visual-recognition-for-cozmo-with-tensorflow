/**
 * Copyright 2015 IBM Corp. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

var request = require('request');
var express = require('express');
var app = express();
var fs = require('fs');
var extend = require('extend');
var path = require('path');
var async = require('async');
var watson = require('watson-developer-cloud');
var uuid = require('uuid');
var bundleUtils = require('./config/bundle-utils');
var os = require('os');
require('dotenv').load();

var ONE_HOUR = 3600000;
var TWENTY_SECONDS = 20000;

// Bootstrap application settings
require('./config/express')(app);

app.get('/', function (req, res) {
  res.render('use', {
    bluemixAnalytics: !!process.env.BLUEMIX_ANALYTICS,
  });
});

app.get('/thermometer', function(req, res) {
  if (typeof req.query.score === 'undefined') {
    return res.status(400).json({ error: 'Missing required parameter: score', code: 400 });
  }
  var score = parseFloat(req.query.score);
  if (score >= 0.0 && score <= 1.0) {
    res.set('Content-type', 'image/svg+xml');
    res.render('thermometer', scoreData(score));
  } else {
    return res.status(400).json({ error: 'Score value invalid', code: 400 });
  }
});

var scoreData = function (score) {
  var scoreColor;
  if (score >= 0.8) {
    scoreColor = '#b9e7c9';
  } else if (score >= 0.6) {
    scoreColor = '#f5d5bb';
  } else {
    scoreColor = '#f4bac0';
  }
  return { score: score, xloc: (score * 312.0), scoreColor: scoreColor };
};

function deleteUploadedFile(readStream) {
  fs.unlink(readStream.path, function (e) {
    if (e) {
      console.log('error deleting %s: %s', readStream.path, e);
    }
  });
}

/**
 * Parse a base 64 image and return the extension and buffer
 * @param  {String} imageString The image data as base65 string
 * @return {Object}             { type: String, data: Buffer }
 */
function parseBase64Image(imageString) {
  var matches = imageString.match(/^data:image\/([A-Za-z-+/]+);base64,(.+)$/);
  var resource = {};

  if (matches.length !== 3) {
    return null;
  }

  resource.type = matches[1] === 'jpeg' ? 'jpg' : matches[1];
  resource.data = new Buffer(matches[2], 'base64');
  return resource;
}

/**
 * Classifies an image
 * @param req.body.url The URL for an image either.
 *                     images/test.jpg or https://example.com/test.jpg
 * @param req.file The image file.
 */
app.post('/api/classify', app.upload.single('images_file'), function (req, res) {
  var params = {
    url: null,
    images_file: null
  };

  if (req.file) { // file image
    params.images_file = fs.createReadStream(req.file.path);
  } else if (req.body.url && req.body.url.indexOf('images') === 0) { // local image
    params.images_file = fs.createReadStream(path.join('public', req.body.url));
  } else if (req.body.image_data) {
    // write the base64 image to a temp file
    var resource = parseBase64Image(req.body.image_data);
    var temp = path.join(os.tmpdir(), uuid.v1() + '.' + resource.type);
    fs.writeFileSync(temp, resource.data);
    params.images_file = fs.createReadStream(temp);
  } else if (req.body.url) { // url
    params.url = req.body.url;
  } else { // malformed url
    return res.status(400).json({ error: 'Malformed URL', code: 400 });
  }

  var formData = {  
    file1: params.images_file
  };
  request.post({
    url: process.env.OPENWHISK_URL,
    formData: formData
  }, function optionalCallback(err, httpResponse, body) {
    if (err) {
      console.error('upload failed:', err);
      res.status(400).json({ error: 'upload failed', code: 400 });
    }
    console.log('Upload successful!  Server responded ');

    let bodyJson = JSON.parse(body);
    let imageClasses = [];

    for (var i in bodyJson) {
      imageClasses.push(
        {
          "class": i,
          "score": bodyJson[i]
        }
      );
    }

    let output = {
      "custom_classes": 0,
      "images": [
        {
          "classifiers": [
            {
              "classes": imageClasses,
              "classifier_id": "default",
              "name": "default"
            },
            {
              "classes": [
                {
                  "class": "non-food",
                  "score": 0.998
                }
              ],
              "classifier_id": "food",
              "name": "food"
            }
          ],
          "image": "5.jpg",
          "faces": [],
          "text": "",
          "words": []
        }
      ],
      "images_processed": 1,
      "raw": {
        "classify": "",
        "detectFaces": "",
        "recognizeText": ""
      }
    }

    res.json(output);
  });

});

module.exports = app;
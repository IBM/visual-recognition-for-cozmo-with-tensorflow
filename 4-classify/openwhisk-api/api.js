/**
 * Copyright 2018 IBM Corp. All Rights Reserved.
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

var str = require('string-to-stream');
var multipart = require('parted').multipart;
var fs = require('fs');
var request = require('request');


function main(args) {
    return new Promise((resolve, reject) => {
        let decoded = new Buffer(args.__ow_body,'base64');
        let newStream = str(decoded);

        var options = {
            limit: 30 * 1024,
            diskLimit: 30 * 1024 * 1024
        };

        var parser = new multipart(args.__ow_headers["content-type"], options), parts = {};
        parser.on('error', function(err) {
            //console.log('parser error', err);
        });

        parser.on('part', function(field, part) {
            parts[field] = part;
        });

        parser.on('data', function() {
            //console.log('%d bytes written.', this.written);
        });

        parser.on('end', function() {
            //console.log(parts);

            var file = fs.readFileSync(parts.file1);
            var base64File = new Buffer(file).toString('base64');

            resolve({
                statusCode: 200,
                headers: { 'Content-Type': 'application/json' },
                payload: base64File
            });
        });
        newStream.pipe(parser);
    });        
}

exports.main = main;

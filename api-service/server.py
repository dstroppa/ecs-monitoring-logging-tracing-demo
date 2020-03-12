#!/usr/bin/env python
# Copyright 2020 Amazon.com, Inc. or its
# affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License is
# located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
import json
import os
from flask import Flask, request, make_response
import boto3
import logging
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_recorder.configure(service='API')
# plugins = ('ecs_plugin')
# xray_recorder.configure(plugins=plugins)
patch_all()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

JSON_MIME_TYPE = 'application/json'

app = Flask(__name__)
XRayMiddleware(app, xray_recorder)

# Start a segment
xray_recorder.begin_segment('init')

sqsqueue_name = os.environ['QUEUE_NAME']
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=sqsqueue_name)

# Close the segment
xray_recorder.end_segment('init')

@xray_recorder.capture('health_check')
@app.route('/')
def health_check():
    return json_response(status=200)

@xray_recorder.capture('list_jobs')
@app.route('/job')
def list_jobs():
    logging.info("Received GET /job request, do nothing.")
    return json_response(json.dumps({'message': 'No jobs to display, submit jobs with POST'}))


@xray_recorder.capture('create_job')
@app.route('/job', methods=['POST'])
def create_job():
    logging.info("Received POST /job request, processing...")
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        logging.error(error)
        return json_response(error, 400)

    data = request.json
    response = queue.send_message(MessageBody=json.dumps(data))
    logging.info("Processed POST /job request, results: %s", json.dumps(response, indent=4))

    return json_response(status=201)
    
@xray_recorder.capture('json_response')
def json_response(data='', status=200, headers=None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = JSON_MIME_TYPE

    return make_response(data, status, headers)

app.run(host='0.0.0.0', port=80)
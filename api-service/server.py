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
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

JSON_MIME_TYPE = 'application/json'

sqsqueue_name = os.environ['QUEUE_NAME']
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=sqsqueue_name)


app = Flask(__name__)


@app.route('/job')
def list_jobs():
    return json_response(json.dumps({'message': 'No jobs to display, submit jobs with POST'}))


@app.route('/job', methods=['POST'])
def create_job():
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)

    data = request.json
    response = queue.send_message(MessageBody=data)

    return json_response(status=201)
    

def json_response(data='', status=200, headers=None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = JSON_MIME_TYPE

    return make_response(data, status, headers)

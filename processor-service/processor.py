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
import os
import json
import boto3
import random
import time
import logging
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

xray_recorder.configure(service='Job Processor')
# plugins = ( 'ecs_plugin' )
# xray_recorder.configure(plugins=plugins)
patch_all()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

sqsqueue_name = os.environ['QUEUE_NAME']
sqs = boto3.resource('sqs')

@xray_recorder.capture('process_messages')
def process_messages():
    """Process the message

    No real error handling in this sample code. In case of error we'll put
    the message back in the queue and make it visable again. It will end up in
    the dead letter queue after five failed attempts.

    """
    processed = 0
    for message in get_messages_from_sqs():
        try:
            message_content = json.loads(message.body)
            logging.info("Processing message: %s", message_content)

            throwError = random.randint(0,5)
            if throwError:
               errorMsg = 'FATAL: This message was not processed. Message: ' + message_content
               hangingException(errorMsg)

        except:
            message.change_visibility(VisibilityTimeout=0)
            continue
        else:
            message.delete()
            processed+=1
    logging.info("Processed %s messages from the queue.", processed)

@xray_recorder.capture('get_messages_from_sqs')
def get_messages_from_sqs():
    results = []
    queue = sqs.get_queue_by_name(QueueName=sqsqueue_name)
    for message in queue.receive_messages(VisibilityTimeout=120,
                                          WaitTimeSeconds=20,
                                          MaxNumberOfMessages=10):
        results.append(message)
    logging.info("Retrieved %s messages from the queue.", len(results))
    return(results)
    
    
@xray_recorder.capture('hangingException')
def hangingException(msg):
    time.sleep(5)
    logging.error(msg)
    raise Exception(msg)


def main():
    while True:
        # Start a segment
        xray_recorder.begin_segment('processor')

        process_messages()

        # Close the segment
        xray_recorder.end_segment('processor')

        time.sleep(5)

if __name__ == "__main__":
    main()
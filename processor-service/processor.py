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
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

sqsqueue_name = os.environ['QUEUE_NAME']
sqs = boto3.resource('sqs')


def process_messages():
    """Process the message

    No real error handling in this sample code. In case of error we'll put
    the message back in the queue and make it visable again. It will end up in
    the dead letter queue after five failed attempts.

    """
    for message in get_messages_from_sqs():
        try:
            message_content = json.loads(message.body)
            
            throwError = random.randint(0,5)
            if throwError:
               errorMsg = 'FATAL: This message was not processed. Message: ' + message_content
               hangingException(errorMsg)

        except:
            message.change_visibility(VisibilityTimeout=0)
            continue
        else:
            message.delete()


def get_messages_from_sqs():
    results = []
    queue = sqs.get_queue_by_name(QueueName=sqsqueue_name)
    for message in queue.receive_messages(VisibilityTimeout=120,
                                          WaitTimeSeconds=20,
                                          MaxNumberOfMessages=10):
        results.append(message)
    return(results)
    
    
@xray_recorder.capture('hangingException')
def hangingException(msg):
    time.sleep(5)
    raise Exception(msg)


def main():
    while True:
        process_messages()


if __name__ == "__main__":
    main()
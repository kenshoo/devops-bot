import json
import os
import re
import logging
from operator import itemgetter
import jenkins
import boto3
from base64 import b64decode

from jenkins_connector import get_jenkins_job_console_output
from consolelog_processor import parse_consolee_log

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INTENT_NAME = 'JenkinsJobIssueAnalysis'
get_slots = itemgetter('JenkinsJobUrl')


def lambda_handler(event, context):
    print('## EVENT')
    print(event)
    print("## CONTEXT")
    print(context)

    transcript = event["inputTranscript"]
    interpretations = event["interpretations"]
    print("interpretations", interpretations)
    slots = get_intent_slots(interpretations)
    jenkins_job_url = get_needed_values(slots).replace('<', '').replace('>', '')
    for j in jenkins_job_url:
        print(j)
    try:
        # output = get_jenkins_job_console_output(job_url="https://jenkins-prod-microcosm.internalk.com/job/activity-audit-main-dsl/8327/")
        # output = get_jenkins_job_console_output('')
        # output = get_jenkins_job_console_output('https://jenkins-prod-search.internalk.com/job/master-release/44033/")
        output = get_jenkins_job_console_output(jenkins_job_url)
        processed = parse_consolee_log(output)

        return create_response(content=processed)
    except Exception as E:
        return create_response(fulfillmentState='Failed', content=str(E))


def create_response(fulfillmentState="Fulfilled", content=None):
    dialogAction_type = 'Close'
    if fulfillmentState == "Fulfilled":
        message = f"The failed command in your build is '{content['command']}''\nand this are the releated errors {content['errors']}"
    else:
        message = content
        dialogAction_type = 'ElicitSlot'
    response = {
        "messages": [{
            'contentType': 'PlainText',
            'content': message
        }],
        "sessionState": {
            "sessionAttributes": {},
            "intent": {
                "name": INTENT_NAME,
                "state": fulfillmentState
            },
            "dialogAction": {
                "type": dialogAction_type,
                "fulfillmentState": fulfillmentState,
                "slotToElicit": "JenkinsJobUrl"
            }
        }
    }
    return response


def get_intent_slots(interpretations):
    slots = next((interpretation['intent']['slots'] for interpretation in interpretations if
                  interpretation['intent']['name'] == INTENT_NAME))
    print("slots", slots)
    return slots


def get_needed_values(slots):
    return slots['JenkinsJobUrl']['value']['originalValue']

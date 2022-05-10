import json
import random


def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']


def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None


def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}


def elicit_intent(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [message] if message != None else None,
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def elicit_slot(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',
                'intentName': "LabIssueAnalysis",
                'slots': {
                    'AskForJira': "",
                },
                'slotToElicit': "AskForJira",
                'message': {
                    'contentType': "PlainText or SSML",
                    'content': message
                }
            },
            'intent': intent_request['sessionState']['intent']
        },
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def close(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [{
            'contentType': 'PlainText',
            'content': message
        }],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def ask_for_jira(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    account = get_slot(intent_request, 'accountType')
    # The account balance in this case is a random number
    # Here is where you could query a system to get this information
    # try:
    #
    if slots['dev-best-practices']['value']['originalValue'] == 'no':
        fulfillment_state = "Fulfilled"
        intent_request['sessionState']['intent']['state'] = fulfillment_state
        message = "Please check the readme..."
        return close(intent_request, session_attributes, message)
    # except TypeError:
    #     pass

    message = {
        "contentType": "ImageResponseCard",
        "content": "string",
        "imageResponseCard": {
            "title": "Do you want to open a ticket to devops?",
            "buttons": [
                {
                    "text": "Yes",
                    "value": "open jira ticket"
                },
                {
                    "text": "No",
                    "value": "never mind"
                }
            ]
        }
    }
    return elicit_intent(intent_request, session_attributes, message)


def dispatch(intent_request):
    print(intent_request)
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    # Dispatch to your bot's intent handlers
    if intent_name == 'LabIssueAnalysis':
        return ask_for_jira(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    response = dispatch(event)
    return response
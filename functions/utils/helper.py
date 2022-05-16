import json
import os
import logging
import dateutil.parser

logger = logging.getLogger()
try:
    logger.setLevel(os.environ.get("LOG_LEVEL"))
except (ValueError, TypeError) as e:
    logger.setLevel(logger.INFO)

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


# def get_slots(request, intent):
#     return filter(lambda i: i.name == intent, request['interpretations'])[0]['slots']

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']


def get_slot(intent_request, slot_name):
    slots = get_slots(intent_request)
    if slots is not None and slot_name in slots and slots[slot_name] is not None:
        return slots[slot_name]['value']['interpretedValue']
    else:
        return None


def get_transcript(intent_request):
    return intent_request["inputTranscript"]


def get_session_attributes(intent_request):
    session_state = intent_request['sessionState']
    if 'sessionAttributes' in session_state:
        return session_state['sessionAttributes']
    return {}


def get_session_active_contexts(intent_request):
    session_state = intent_request['sessionState']
    if 'activeContexts' in session_state:
        return session_state['activeContexts']
    return {}


def elicit_intent(intent_request, message=None):
    return {
        'sessionState': {
            'sessionAttributes': get_session_attributes(intent_request),
            'dialogAction': {
                'type': 'ElicitIntent',
            },
        },
        'messages': _get_message(message),
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def elicit_slot(intent_request, slot_to_elicit, message):
    return {
        'sessionState': {
            'activeContexts': get_session_active_contexts(intent_request),
            'sessionAttributes': get_session_attributes(intent_request),
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit,
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': _get_message(message),
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def confirm(intent_request, message):
    return {
        'sessionState': {
            'activeContexts': get_session_active_contexts(intent_request),
            'sessionAttributes': get_session_attributes(intent_request),
            'dialogAction': {
                'type': 'ConfirmIntent',
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': _get_message(message),
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def close(intent_request, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': get_session_attributes(intent_request),
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': _get_message(message),
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def delegate(intent_request, slots):
    intent_request['sessionState']['intent']['slots'] = slots
    return {
        'sessionState': {
            'sessionAttributes': get_session_attributes(intent_request),
            'dialogAction': {
                'type': 'Delegate',
            },
            'intent': intent_request['sessionState']['intent']
        },
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def _get_message(message):
    if message is None:
        return None
    elif str(message) == message:
        return [{
            'contentType': 'PlainText',
            'content': message
        }]
    else:
        return [message]


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def dump(event, context):
    logger.debug(f'# Event #\n {json.dumps(event)}')
    logger.debug(f'# Context #\n {json.dumps(context)}')

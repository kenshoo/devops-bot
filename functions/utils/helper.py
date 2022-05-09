import logging
import dateutil.parser

logger = logging.getLogger()
logger.setLevel(logging.INFO)

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(request, intent):
    return filter(lambda i: i.name == intent, request['interpretations'])[0]['slots']


def elicit_intent(session_attributes, message, response_card):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes
            'dialogAction': {
                'type': 'ElicitIntent',
            },
         },
        'messages': [{
            'contentType': 'PlainText',
            'content': message
        }],
        'responseCard': response_card
    }


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'message': {
                'contentType': 'PlainText',
                'content': message
            }
        },
        'intentName': intent_name,
        'slots': slots,
        'slotToElicit': slot_to_elicit,
        'responseCard': response_card
    }


def confirm(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'message': {
                'contentType': 'PlainText',
                'content': message
            }
        },
        'intentName': intent_name,
        'slots': slots,
        'slotToElicit': slot_to_elicit,
        'responseCard': response_card
    }


def close(session_attributes, fulfillment_state, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'message': {
                'contentType': 'PlainText',
                'content': message
            }
        },
        'fulfillmentState': fulfillment_state
    }


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


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

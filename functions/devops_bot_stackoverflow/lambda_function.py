import json
from operator import itemgetter
from stackapi import StackAPI
import requests, traceback, json

STACKOVERFLOW_URL = "https://stackoverflow.com/c/kenshoo/"
INTENT_NAME = 'StackOverflowIntent'
get_slots = itemgetter('Keywords')


def lambda_handler(event, context):
    print('## EVENT')
    print(event)
    print("## CONTEXT")
    print(context)

    transcript = event["inputTranscript"]
    interpretations = event["interpretations"]
    print("interpretations", interpretations)
    slots = get_intent_slots(interpretations)

    # query = get_needed_values(slots)
    query = transcript

    questions = []
    all_items = []
    site = "stackoverflow"
    qa = "questions"  # or answers
    try:
        page = 1
        while 1:
            print(query)
            url = f"https://api.stackexchange.com/2.2/search/advanced/?pagesize=100&page=1&filter=default&key=Su2AR2rGRU1FOWaUH5d3RQ((&title={query}?&team=stackoverflow.com/c/kenshoo&site=stackoverflow"
            j = requests.get(url, headers={"X-API-Access-Token": "5KZ896CHpnWuHHFyAPhmPQ))"}).json()
            print(j)
            if j:

                all_items += j["items"]

                if not j['has_more']:
                    print("No more Pages")
                    break
                elif not j['quota_remaining']:
                    print("No Quota Remaining ")
                    break
            else:
                print("No Questions")
                break

            page += 1

        if all_items:
            for item in all_items:
                print("{0}: {1}".format(item['title'], item['link']))
                questions.append("{0}: {1}".format(item['title'], item['link']))

        body = create_response('\n'.join(questions))
    except Exception as e:
        print("An error has occured: ", e)
        body = create_response(fulfillmentState="Failed")

    print("Returning body: ", body)
    return body


def create_response(content=None, fulfillmentState="Fulfilled"):
    if fulfillmentState == "Fulfilled" and content:
        message = content
    else:
        message = "Sorry, nothing found on stackoverflow."

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
                "type": "Close",
                "fulfillmentState": fulfillmentState
            }
        }
    }
    return response


def get_intent_slots(interpretations):
    intent = next((interpretation['intent']['slots'] for interpretation in interpretations if
                   interpretation['intent']['name'] == INTENT_NAME))
    print("intent", intent)
    return intent


def get_needed_values(slots):
    return [slot['value']['originalValue'] for slot in get_slots(slots)]

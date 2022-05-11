import logging
import requests
from functions.utils import helper

STACKOVERFLOW_URL = "https://stackoverflow.com/c/kenshoo/"
INTENT_NAME = 'StackOverflowIntent'

def lambda_handler(event, context):
    print('## EVENT')
    print(event)
    print("## CONTEXT")
    print(context)

    transcript = event["inputTranscript"]
    query = transcript

    questions = []
    all_items = []
    site = "stackoverflow"
    qa = "questions"  # or answers
    token=get_data_from_consul()['Value']

    try:
        page = 1
        while 1:
            print(query)
            url = f"https://api.stackexchange.com/2.2/search/advanced/?pagesize=100&page=1&filter=default&key=Su2AR2rGRU1FOWaUH5d3RQ((&title={query}?&team=stackoverflow.com/c/kenshoo&site=stackoverflow"
            j = requests.get(url, headers={"X-API-Access-Token": token}).json()
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
        return helper.close(event, 'Fulfilled' '\n'.join(questions))
    except Exception as e:
        return helper.close(event, 'Failed' 'Sorry, nothing found on stackoverflow.')

def get_data_from_consul():
    logging.info("Getting data from Consul")
    response = requests.get(f'http://consul.kenshoo.com/v1/kv/devopsBot/SOToken', timeout=20)
    if response.status_code != 200:
        logging.error(f"An error occurred while getting data from GitHub. Status code: {response.status_code}, Reason: {response.reason}. Sending an email")
    return response.json()

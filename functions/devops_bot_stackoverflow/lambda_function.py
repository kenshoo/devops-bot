import requests
from functions.utils import helper
from functions.utils.helper import logger
import os

STACKOVERFLOW_URL = "stackoverflow.com/c/kenshoo"


def lambda_handler(event, context):
    helper.dump(event, context)

    transcript = event["inputTranscript"]
    query = transcript

    questions = []
    all_items = []
    site = "stackoverflow"
    qa = "questions"  # or answers
    # token = get_data_from_consul()[0]['Value']
    token = os.getenv('STACKOVERFLOW_TOKEN')
    print(token)

    try:
        page = 1
        while 1:
            logger.debug(query)
            url = f"https://api.stackexchange.com/2.2/search/advanced/?pagesize=100&page=1&filter=default&key=WYpIqX0UcIHHopYLKw3wXQ((&title={query}?&team={STACKOVERFLOW_URL}&site=stackoverflow"
            j = requests.get(url, headers={"X-API-Access-Token": token}).json()
            logger.debug(j)
            if j:

                all_items += j["items"]

                if not j['has_more']:
                    logger.debug("No more Pages")
                    break
                elif not j['quota_remaining']:
                    logger.debug("No Quota Remaining ")
                    break
            else:
                logger.debug("No Questions")
                break

            page += 1

        if all_items:
            for item in all_items:
                logger.debug("{0}: {1}".format(item['title'], item['link']))
                questions.append("{0}: {1}".format(item['title'], item['link']))
        return helper.close(event, 'Fulfilled', '\n'.join(questions))
    except Exception as e:
        return helper.close(event, 'Failed', 'Sorry, nothing found on stackoverflow.')


def get_data_from_consul():
    logger.info("Getting data from Consul")
    response = requests.get(f'http://consul.kenshoo.com/v1/kv/devopsBot/SOToken', timeout=20)
    if response.status_code != 200:
        logger.error(f"An error occurred while getting data from GitHub. Status code: {response.status_code}, "
                     f"Reason: {response.reason}. Sending an email")
    return response.json()

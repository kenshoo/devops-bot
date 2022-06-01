from functions.utils import helper


def ask_for_jira(intent_request):
    slots = helper.get_slots(intent_request)
    account = helper.get_slot(intent_request, 'accountType')
    # The account balance in this case is a random number
    # Here is where you could query a system to get this information
    if slots['dev-best-practices']['value']['originalValue'] == 'no':
        return helper.close(intent_request, 'Fulfilled', "Please check the readme...")
    else:
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
        return helper.elicit_intent(intent_request, message)


def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'LabIssueAnalysis':
        return ask_for_jira(intent_request)
    else:
        raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    helper.dump(event, context)
    response = dispatch(event)
    return response

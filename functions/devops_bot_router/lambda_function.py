import json
import boto3
from functions.utils import helper
from functions.utils.helper import logger

# reuse client connection as global
client = boto3.client('lambda')


def router(event):
    intent_name = event['sessionState']['intent']['name']
    # fn_name = os.environ.get(intent_name)
    fn_name = intent_handlers[intent_name]
    logger.info(f"Intent: {intent_name} -> Lambda: {fn_name}")
    if fn_name:
        # invoke lambda and return result
        invoke_response = client.invoke(FunctionName=fn_name, Payload=json.dumps(event))
        logger.debug(invoke_response)
        payload = json.load(invoke_response['Payload'])
        return payload
    raise Exception('No lambda defined for intent: ' + intent_name)


def lambda_handler(event, context):
    helper.dump(event, context)
    response = router(event)
    return response


intent_handlers = {
  "jiraTicket": "pulumi-lambda-devops-bot-jira-ticket",
  "JenkinsJobIssueAnalysis": "pulumi-lambda-devops-bot-jenkins",
  "LabIssueAnalysis": "pulumi-lambda-devops-bot-lab-issue",
  "StackOverflowIntent": "pulumi-lambda-devops-bot-stackoverflow",
  "KSLABCreationIntent": "pulumi-lambda-devops-bot-aws-lab-creation"
}

import json
import boto3

# reuse client connection as global
client = boto3.client('lambda')


def router(event):
    intent_name = event['sessionState']['intent']['name']
    # fn_name = os.environ.get(intent_name)
    fn_name = intent_handlers[intent_name]
    print(f"Intent: {intent_name} -> Lambda: {fn_name}")
    if fn_name:
        # invoke lambda and return result
        invoke_response = client.invoke(FunctionName=fn_name, Payload=json.dumps(event))
        print(invoke_response)
        payload = json.load(invoke_response['Payload'])
        return payload
    raise Exception('No lambda defined for intent: ' + intent_name)


def lambda_handler(event, context):
    print(event)
    # return event['sessionState']['intent']['name']
    response = router(event)
    return response


intent_handlers = {
  "jiraTicket": "devops-bot-jira-ticket-intent",
  "JenkinsJobIssueAnalysis": "devops-bot-jenkins-intent",
  "LabIssueAnalysis": "devops-bot-lab-issue-intent",
  "StackOverflowIntent": "devops-bot-stackoverflow-intent"
}

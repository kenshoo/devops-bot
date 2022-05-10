import os
from operator import itemgetter
from jira import JIRA
import ssl
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

jira_intent = "jiraTicket"
get_slots = itemgetter('severity', 'supportType', 'reportingTeam', 'components', 'requestImpact', 'summary')


def lambda_handler(event, context):
    severity = "customfield_10411"
    supporttype = "customfield_15415"
    request_impact = "customfield_15412"
    reporting_team = "customfield_15417"
    print('## EVENT')
    print(event)
    print("## CONTEXT")
    print(context)
    token = os.environ.get('JIRA_TOKEN')
    base_url = "https://kenshoo.atlassian.net"
    jira = JIRA(server=base_url, basic_auth=("aws-iam-rotator@kenshoo.com", token))

    transcript = event["inputTranscript"]
    interpretations = event["interpretations"]
    print("interpretations", interpretations)
    slots = get_jira_intent_slots(interpretations)

    severity_val, support_type, team, component, request_impact_val, summary = get_needed_values(slots)

    create_issue_payload = {
        "project": {'key': 'DEVOPS'},
        "issuetype": {'name': 'Support'},
        severity: {'value': severity_val},
        supporttype: {'value': support_type},
        request_impact: {'value': request_impact_val},
        reporting_team: {'value': team},
        "components": [{"name": component}],
        "summary": summary,
        "description": transcript
    }

    user_slack_id = event.get('sessionId', "").split(":")[-1]
    user_slack_id = "U1NDHKECU"

    try:
        print("About to create an issue with these fields: ", create_issue_payload)
        issue = jira.create_issue(fields=create_issue_payload)
        print("Ticket created: ", issue.key)
        issue.fields.labels.append("devops-bot")

        issue_update_payload = {
            "fields": {
                "labels": issue.fields.labels
            }
        }

        if user_slack_id:
            email = get_email_from_slack(user_slack_id)
            if email:
                jira_user_id = jira._get_user_id(email)

                if jira_user_id:
                    issue.fields.reporter = {"accountId": jira_user_id}
                    issue_update_payload["fields"]["repoter"] = issue.fields.reporter

        issue.update(fields=issue_update_payload)
        print("Updated labels: ", issue.fields.labels)

        body = create_response(base_url, issue)
    except Exception as e:
        print("An error has occured: ", e)
        body = create_response(fulfillmentState="Failed")

    print("Returning body: ", body)
    return body


def create_response(base_url=None, issue=None, fulfillmentState="Fulfilled"):
    if fulfillmentState == "Fulfilled":
        message = f"Your ticket has been opened here => {base_url}/browse/{issue.key}"
    else:
        message = "Your ticket could not be opened"

    response = {
        "messages": [{
            'contentType': 'PlainText',
            'content': message
        }],
        "sessionState": {
            "sessionAttributes": {},
            "intent": {
                "name": jira_intent,
                "state": fulfillmentState
            },
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": fulfillmentState
            }
        }
    }
    return response


def get_jira_intent_slots(interpretations):
    a = next((interpretation['intent']['slots'] for interpretation in interpretations if
              interpretation['intent']['name'] == jira_intent))
    print("a", a)
    return a


def get_needed_values(slots):
    print("slots", slots)
    return [slot['value']['originalValue'] for slot in get_slots(slots)]


def get_email_from_slack(user_id):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token, ssl=ssl_context)
    try:
        result = client.users_info(user=user_id)
        return result.get("user").get("profile").get("email")
    except SlackApiError as e:
        print("Couldn't get slack user's email: ", e)
        return None
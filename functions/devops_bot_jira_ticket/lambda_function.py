import json
import os
from operator import itemgetter
from jira import JIRA
import ssl
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from functions.utils import helper
from functions.utils.helper import logger

SEVERITY = "customfield_10411"
SUPPORT_TYPE = "customfield_15415"
REQUEST_IMPACT = "customfield_15412"
REPORTING_TEAM = "customfield_15417"
BASE_URL = "https://kenshoo.atlassian.net"
JIRA_INTENT = "jiraTicket"


def lambda_handler(event, context):
    helper.dump(event.event, context)

    obj = {}
    obj.transcript = helper.get_transcript(event)
    # obj.user_slack_id = event.get('sessionId', "").split(":")[-1]
    obj.user_slack_id = "U1NDHKECU"
    slots = helper.get_slots(event)
    obj.severity_val, obj.support_type, obj.team, obj.component, obj.request_impact_val, obj.summary \
        = _get_needed_values(slots)
    if not _validate_slots(obj):
        return helper.elicit_slot(event, '', _get_slack_block_kits(obj))

    try:
        issue = _create_jira_ticket(obj)
        message = f"Your ticket has been opened here => {BASE_URL}/browse/{issue.key}"
        return helper.close(event, "Fulfilled", message)
    except Exception as e:
        logger.error("An error has occurred: ", e)
        return helper.close(event, "Failed", f'Error: your ticket could not be opened: {str(e)}')


def _validate_slots(obj):
    for k in obj:
        if k is None:
            return False
    return True


def _get_needed_values(slots):
    logger.debug("slots", slots)
    get_specific_slots = itemgetter('severity', 'supportType', 'reportingTeam',
                                    'components', 'requestImpact', 'summary')
    return [slot['value']['originalValue'] for slot in get_specific_slots(slots)]


def _get_email_from_slack(user_id):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token, ssl=ssl_context)
    try:
        result = client.users_info(user=user_id)
        return result.get("user").get("profile").get("email")
    except SlackApiError as e:
        logger.error("Couldn't get slack user's email: ", e)
        return None


def _create_jira_ticket(obj):
    token = os.environ.get('JIRA_TOKEN')
    jira = JIRA(server=BASE_URL, basic_auth=("aws-iam-rotator@kenshoo.com", token))
    create_issue_payload = {
        "project": {'key': 'DEVOPS'},
        "issuetype": {'name': 'Support'},
        SEVERITY: {'value': obj.severity_val},
        SUPPORT_TYPE: {'value': obj.support_type},
        REQUEST_IMPACT: {'value': obj.request_impact_val},
        REPORTING_TEAM: {'value': obj.team},
        "components": [{"name": obj.component}],
        "summary": obj.summary,
        "description": obj.transcript
    }

    logger.log("About to create an issue with these fields: ", create_issue_payload)
    issue = jira.create_issue(fields=create_issue_payload)
    logger.log("Ticket created: ", issue.key)
    issue.fields.labels.append("devops-bot")

    issue_update_payload = {
        "fields": {
            "labels": issue.fields.labels
        }
    }

    if obj.user_slack_id:
        email = _get_email_from_slack(obj.user_slack_id)
        if email:
            jira_user_id = jira._get_user_id(email)

            if jira_user_id:
                issue.fields.reporter = {"accountId": jira_user_id}
                issue_update_payload["fields"]["reporter"] = issue.fields.reporter

    issue.update(fields=issue_update_payload)
    logger.log("Updated labels: ", issue.fields.labels)
    return issue


def _get_slack_block_kits(obj):
    return json.load({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello {UserName} to proceed in creating a ticket, please fill out the following survey.\n *Make sure to fill all the fields*:\n\n "
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Ticket title",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Team1",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Team2",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Team3",
                                "emoji": True
                            },
                            "value": "value-2"
                        }
                    ],
                    "action_id": "static_select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Reporting Team (need to create logic to import the list)",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                                "emoji": True
                            },
                            "value": "value-0"
                        }
                    ],
                    "action_id": "static_select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Support Type (import options from JIRA/list)",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*Low*",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*Middle*",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*High*",
                                "emoji": True
                            },
                            "value": "value-2"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*Hotfix*",
                                "emoji": True
                            },
                            "value": "value-3"
                        }
                    ],
                    "action_id": "static_select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Severity",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Description(What did you try, what conclusions you have, any info)",
                    "emoji": True
                }
            }
        ]
    })

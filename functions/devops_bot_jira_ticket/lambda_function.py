import json
import os
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
    helper.dump(event, context)

    slots = {'transcript': helper.get_transcript(event),
             'user_slack_id': "U1NDHKECU",
             'severity': helper.get_slot(event, 'severity'),
             'supportType': helper.get_slot(event, 'supportType'),
             'reportingTeam': helper.get_slot(event, 'reportingTeam'),
             'components': helper.get_slot(event, 'components'),
             'requestImpact': helper.get_slot(event, 'requestImpact'),
             'summary': helper.get_slot(event, 'summary')}

    # slots['user_slack_id'] = event.get('sessionId', "").split(":")[-1]

    if helper.get_invocation_source == "DialogCodeHook":
        validation_result = helper.validate_slots(slots)
        if not validation_result['isValid']:
            logger.debug(slots)
            return helper.elicit_slot(event, validation_result['violatedSlot'], _get_slack_block_kits(slots))

    try:
        issue = _create_jira_ticket(slots)
        message = f"Your ticket has been opened here => {BASE_URL}/browse/{issue.key}"
        return helper.close(event, "Fulfilled", message)
    except Exception as e:
        logger.error("An error has occurred: ", str(e))
        return helper.close(event, "Failed", f'Error: your ticket could not be opened: {str(e)}')


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


def _create_jira_ticket(slots):
    token = os.environ.get('JIRA_TOKEN')
    jira = JIRA(server=BASE_URL, basic_auth=("aws-iam-rotator@kenshoo.com", token))
    create_issue_payload = {
        "project": {'key': 'DEVOPS'},
        "issuetype": {'name': 'Support'},
        SEVERITY: {'value': slots.severity_val},
        SUPPORT_TYPE: {'value': slots.support_type},
        REQUEST_IMPACT: {'value': slots.request_impact_val},
        REPORTING_TEAM: {'value': slots.team},
        "components": [{"name": slots.component}],
        "summary": slots.summary,
        "description": slots.transcript
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

    if slots.user_slack_id:
        email = _get_email_from_slack(slots.user_slack_id)
        if email:
            jira_user_id = jira._get_user_id(email)

            if jira_user_id:
                issue.fields.reporter = {"accountId": jira_user_id}
                issue_update_payload["fields"]["reporter"] = issue.fields.reporter

    issue.update(fields=issue_update_payload)
    logger.log("Updated labels: ", issue.fields.labels)
    return issue


def _get_slack_block_kits(slots):
    return {
        "contentType": "CustomPayload",
        "content": json.dumps(
            [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hello {slots.get('user_slack_id')} to proceed in creating a ticket, please fill out the following "
                                "survey.\n *Make sure to fill all the fields*:\n\n "
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
        )
    }

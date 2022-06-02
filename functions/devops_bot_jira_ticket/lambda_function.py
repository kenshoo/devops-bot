import os
from jira import JIRA
from functions.utils import helper, slack
from functions.utils.helper import logger

SEVERITY = "customfield_10411"
SUPPORT_TYPE = "customfield_15415"
REQUEST_IMPACT = "customfield_15412"
REPORTING_TEAM = "customfield_15417"
BASE_URL = "https://kenshoo.atlassian.net"


def lambda_handler(event, context):
    helper.dump(event, context)

    user_slack_id = event.get('sessionId', "").split(":")[-1]
    email = slack.get_email_from_slack(user_slack_id),
    slots = {'transcript': helper.get_transcript(event),
             'user_slack_id': user_slack_id,
             'email': email,
             'severity': helper.get_slot(event, 'severity'),
             'supportType': helper.get_slot(event, 'supportType'),
             'reportingTeam': helper.get_slot(event, 'reportingTeam'),
             'components': helper.get_slot(event, 'components'),
             'requestImpact': helper.get_slot(event, 'requestImpact'),
             'summary': helper.get_slot(event, 'summary')}

    if helper.get_invocation_source(event) == "DialogCodeHook":
        validation_result = helper.validate_slots(slots)
        if not validation_result['isValid']:
            logger.debug(slots)
            slack.post_in_slack(slots.get('user_slack_id'), 'Please provide the missing fields',
                                _get_slack_block_kits(slots))
            return helper.elicit_slot(event, validation_result['violatedSlot'], validation_result['message'])

    try:
        issue = _create_jira_ticket(slots)
        message = f"Your ticket has been opened here => {BASE_URL}/browse/{issue.key}"
        return helper.close(event, "Fulfilled", message)
    except Exception as e:
        logger.error(f"An error has occurred: {e}")
        return helper.close(event, "Failed", f'Error: your ticket could not be opened: {e}')


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
        if slots.email:
            jira_user_id = jira._get_user_id(slots.email)

            if jira_user_id:
                issue.fields.reporter = {"accountId": jira_user_id}
                issue_update_payload["fields"]["reporter"] = issue.fields.reporter

    issue.update(fields=issue_update_payload)
    logger.log("Updated labels: ", issue.fields.labels)
    return issue


def _get_slack_block_kits(slots):
    return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hello {(slots.get('email'))} to proceed in creating a "
                                f"ticket, please fill out the following survey.\n *Make sure to fill all the fields*:\n"
                    }
                },
                {
                    "type": "divider"
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
                        "text": "Please describe your issue",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Which components are relevant? (example: jenkins,microcosm)",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Which team are you in?",
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
                                    "text": "*Build*",
                                    "emoji": True
                                },
                                "value": "Build"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*Deployment*",
                                    "emoji": True
                                },
                                "value": "Deployment"
                            }
                        ],
                        "action_id": "static_select-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Support Type",
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
                                    "text": "*General guidance*",
                                    "emoji": True
                                },
                                "value": "General guidance"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*Development impaired*",
                                    "emoji": True
                                },
                                "value": "Development impaired"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*Development blocked*",
                                    "emoji": True
                                },
                                "value": "Development blocked"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*System impaired*",
                                    "emoji": True
                                },
                                "value": "System impaired"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*System down*",
                                    "emoji": True
                                },
                                "value": "System down"
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
                                    "text": "*Single person*",
                                    "emoji": True
                                },
                                "value": "Single person"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*Single Team*",
                                    "emoji": True
                                },
                                "value": "Single Team"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*Multiple teams*",
                                    "emoji": True
                                },
                                "value": "Multiple teams"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*All tech*",
                                    "emoji": True
                                },
                                "value": "All tech"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*All Kenshoo*",
                                    "emoji": True
                                },
                                "value": "All Kenshoo"
                            }
                        ],
                        "action_id": "static_select-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "What's the impact",
                        "emoji": True
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Submit",
                                "emoji": True
                            },
                            "value": "click_me_123",
                            "action_id": "actionId-0"
                        }
                    ]
                }
            ]

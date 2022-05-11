import logging
from functions/utils import helper

from jenkins_connector import get_jenkins_job_console_output
from consolelog_processor import parse_consolee_log

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INTENT_NAME = 'JenkinsJobIssueAnalysis'


def lambda_handler(event, context):
    print('## EVENT')
    print(event)
    print("## CONTEXT")
    print(context)

    slots = helper.get_slots(event)
    jenkins_job_url = helper.get_slot(slots, 'JenkinsJobUrl')
    if jenkins_job_url is not None:
        jenkins_job_url = jenkins_job_url.replace('<', '').replace('>', '')

    try:
        output = get_jenkins_job_console_output(jenkins_job_url)
        processed = parse_consolee_log(output)
        message = f"The failed command in your build is {processed['command']}\n" \
                  f"and this are the related errors {processed['errors']}"

        return helper.close(event, "Fulfilled", message)
    except Exception as E:
        return helper.elicit_slot(event, "JenkinsJobUrl", str(E))

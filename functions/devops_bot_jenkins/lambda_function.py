from functions.utils import helper
from functions.devops_bot_jenkins.jenkins_connector import get_jenkins_job_console_output
from functions.devops_bot_jenkins.consolelog_processor import parse_console_log


def lambda_handler(event, context):
    helper.dump(event, context)

    jenkins_job_url = helper.get_slot(event, 'JenkinsJobUrl')
    if jenkins_job_url is not None:
        jenkins_job_url = jenkins_job_url.replace('<', '').replace('>', '')

    try:
        output = get_jenkins_job_console_output(jenkins_job_url)
        processed = parse_console_log(output)
        message = f"The failed command in your build is {processed['command']}\n" \
                  f"and this are the related errors {processed['errors']}"

        return helper.close(event, "Fulfilled", message)
    except Exception as E:
        return helper.elicit_slot(event, "JenkinsJobUrl", str(E))

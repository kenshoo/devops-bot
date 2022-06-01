from functions.utils import helper
from functions.devops_bot_jenkins.jenkins_connector import get_jenkins_job_console_output
from functions.devops_bot_jenkins.consolelog_processor import parse_console_log
from servers_creation import servers_creation_main
from jenkins_initiator import JenkinsInit
from pullrequest_util import PullRequestUtils
from environment_util import GithubEnvironmentUtil


def lambda_handler(event, context):
    pr_utils = PullRequestUtils('pulumi-ks-provision', 1200)
    github_env_utils = GithubEnvironmentUtil('prod', '.', 'pulumi-ks-provision')
    jenkins = JenkinsInit('core', 1200)
    servers_creation_main(jenkins, github_env_utils, pr_utils, event)

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

from functions.utils import helper, slack
from functions.utils.helper import logger
from functions.devops_bot_aws_lab_creation.servers_creation import servers_creation_main
from functions.devops_bot_aws_lab_creation.jenkins_initiator import JenkinsInit
from functions.devops_bot_aws_lab_creation.pullrequest_util import PullRequestUtils
from functions.devops_bot_aws_lab_creation.environment_util import GithubEnvironmentUtil


def lambda_handler(event, context):
    helper.dump(event, context)
    user_slack_id = event.get('sessionId', "").split(":")[-1]
    email = slack.get_email_from_slack(user_slack_id),
    pr_utils = PullRequestUtils('pulumi-ks-provision', 1200)
    github_env_utils = GithubEnvironmentUtil('prod', '.', 'pulumi-ks-provision')
    jenkins = JenkinsInit('core', 1200)
    slots = {'transcript': helper.get_transcript(event),
             'user_slack_id': user_slack_id,
             'email': email,
             'team_name': helper.get_slot(event, 'team_name'),
             'source_ks_id': helper.get_slot(event, 'source_ks_id'),
             'is_memsql': helper.get_slot(event, 'is_memsql')}
    print(event)
    try:
        issue = servers_creation_main(jenkins, github_env_utils, pr_utils, slots)
        message = f"Your lab creation job is finished => \n {issue}"
        return helper.close(event, "Fulfilled", message)
    except Exception as e:
        logger.error(f"An error has occurred: {e}")
        return helper.close(event, "Failed", f'Error: your lab creation failed: {e}')

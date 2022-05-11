import os
import time
from github import Github

HUBOT_CONFIG = {'name': 'web',
                'config': {'insecure_ssl': '0', 'content_type': 'json',
                           'url': 'https://hubot.kenshoo.com/hubot/github-repo-listener'},
                'events': ['issue_comment'],
                'active': True}
JENKINS_CONFIG = {'name': 'web',
                  'config': {'insecure_ssl': '0', 'content_type': 'application/x-www-form-urlencoded',
                             'url': 'https://microcosm-jenkins.kenshoo.com/ghprbhook/'},
                  'events': ['issue_comment', 'pull_request'],
                  'active': True}
WEBHOOKS = (JENKINS_CONFIG, HUBOT_CONFIG)


def _create_default_webhooks(repo):
    for hook_config in WEBHOOKS:
        repo.create_hook(**hook_config)


def _ok_with_result(repo_name):
    return {
        'statusCode': 201,
        'headers': {'Content-Type': 'application/json'},
        'body': repo_name + " created!\n https://github.com/kenshoo/" + repo_name
    }


def lambda_handler(event, context):
    gh_token = os.getenv("GITHUB_TOKEN")
    g = Github(gh_token)
    org = g.get_organization("kenshoo")
    query_string_params = event['queryStringParameters']
    repo_name_param = query_string_params['repo_name']
    print("the input repo name: " + repo_name_param)
    new_repo = org.create_repo(name=repo_name_param,
                               private=True,
                               auto_init=True,
                               allow_squash_merge=True,
                               delete_branch_on_merge=True)
    time.sleep(5)
    _create_default_webhooks(new_repo)
    print("webhooks created")
    created_repo = org.get_repo(repo_name_param)
    master = created_repo.get_branch("master")
    print("I got master")
    master.edit_protection(strict=True,
                           contexts=["default", "SpectralCheck"],
                           required_approving_review_count=1)
    print("set protection")
    return _ok_with_result(repo_name_param)

from lambda_tasks_plugin.lambda_module import LambdaModule

stacks_to_lambda_module = {
    'devops_bot_router': LambdaModule(packages=[], entry_point='devops_bot_router/lambda_function.py'),
    'devops_bot_github_repo': LambdaModule(
        packages=['utils'],
        entry_point='devops_bot_github_repo/lambda_function.py'),
    'devops_bot_jenkins': LambdaModule(
        packages=[
            'utils',
            'devops_bot_jenkins'],
        entry_point='devops_bot_jenkins/lambda_function.py'),
    'devops_bot_jira_ticket': LambdaModule(
        packages=['utils', 'devops_bot_jira_ticket'],
        entry_point='devops_bot_jira_ticket/lambda_function.py'),
    'devops_bot_lab_issue': LambdaModule(
        packages=['utils'],
        entry_point='devops_bot_lab_issue/lambda_function.py'),
    'devops_bot_stackoverflow': LambdaModule(
        packages=['utils'],
        entry_point='devops_bot_stackoverflow/lambda_function.py')
}

repo_name = "devops-bot"
app_root = "./"
line_coverage_min_threshold = 0

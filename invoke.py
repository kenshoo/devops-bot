from lambda_tasks_plugin.lambda_module import LambdaModule

stacks_to_lambda_module = {
    'devops_bot_router': LambdaModule(packages=[], entry_point='devops-bot-jira-ticket/lambda_function.py'),
    'devops_bot_jenkins': LambdaModule(packages=[], entry_point='devops-bot-jira-ticket/lambda_function.py'),
    'devops_bot_jira_ticket': LambdaModule(packages=[], entry_point='devops-bot-jira-ticket/lambda_function.py'),
    'devops_bot_lab_issue': LambdaModule(packages=[], entry_point='devops-bot-jira-ticket/lambda_function.py'),
    'devops_bot_stackoverflow': LambdaModule(packages=[], entry_point='devops-bot-jira-ticket/lambda_function.py')
}

repo_name = "devops-bot"
app_root = "./"
line_coverage_min_threshold = 0

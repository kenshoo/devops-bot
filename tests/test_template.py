from collections import Callable

from functions.devops_bot_lab_issue import lambda_function as lab
from functions.utils.globals import APP_ROOT, PROJECT_NAME


class TestTemplate(object):

    def test_should_access_api_gateway_handler_modules_and_run_handler(self):
        assert isinstance(lab.lambda_handler, Callable)

    def test_should_have_access_to_global_helper_objects(self):
        assert "devops-bot" in APP_ROOT

from collections import Callable

from functions.api_gateway_lambda import api_gateway_handler
from functions.utils.globals import APP_ROOT, PROJECT_NAME


class TestTemplate(object):

    def test_should_access_api_gateway_handler_modules_and_run_handler(self):
        assert isinstance(api_gateway_handler.lambda_handler, Callable)

    def test_should_have_access_to_global_helper_objects(self):
    	assert "devops-bot" in APP_ROOT

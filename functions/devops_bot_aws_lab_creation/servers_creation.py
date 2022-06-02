import traceback
from jinja2 import Template

TEMPLATE_PATH = 'functions/devops_bot_aws_lab_creation/Pulumi.ks_sdlc.yaml.tpl'
MASTER_JOB = 'Build_KS_AWS'
DEFAULT_PARAMS_DICT = {'ks_namne': '', 'root_size': 30, 'kdata': 20, 'local': 60,
                       'binlog': 100, 'data1': 200, 'data2': 20, 'db_root_size': 30,
                       'tmpdb': 80}


class ServersCreator(object):
    def __init__(self, jenkins_client, github_env_utils, pr_utils, ks_name):
        self._jenkins_client = jenkins_client
        self._github_env_utils = github_env_utils
        self._pr_utils = pr_utils
        self._ks_name = ks_name

    @staticmethod
    def create_stack_text_from_template(params_dict):
        with open('stack.j2', 'r') as stack_template:
            stack_text = Template(stack_template.read())
        return stack_text.render(params_dict)

    def is_stack_exists_in_master(self):
        return self._github_env_utils.file_exists_in_branch(f'ks/environments/sdlc/Pulumi.sdlc-{self._ks_name}.yaml',
                                                            'master')

    def create_pr(self, stack_text):
        self._pr_utils.create_side_branch()
        self._pr_utils.create_file(f'ks/environments/sdlc/Pulumi.sdlc-{self._ks_name}.yaml', stack_text,
                                   f'{self._ks_name} migration servers creation')
        return self._pr_utils.create_pr(f'DevOps Bot: Lab Creation for {self._ks_name}')

    def merge_pr(self, pr_obj):
        if self._pr_utils.validate_pr_checks_is_success(pr_obj):
            build_num = self._jenkins_client.get_candidate_build(MASTER_JOB)
            if self._pr_utils.merge_pr(pr_obj):
                return build_num

            raise Exception(f'{pr_obj.url} could not be merged, please check')

    def validate_master_build(self, build_num):
        build_res = self._jenkins_client.get_build_result(MASTER_JOB, build_num)
        self._jenkins_client.validate_is_build_successful({'number': build_num,
                                                           'result': build_res,
                                                           'url': f'{self._jenkins_client.jobs_url}{MASTER_JOB}/{build_num}/'
                                                           })


def run_workflow(jenkins, github_env, pr_utils, _lab_params):
    ks_name = f'{_lab_params.get("team_name")}{_lab_params.get("source_ks_id")}'
    params_dict = create_params_dict_from_evnet_config(_lab_params, ks_name)
    server_creator = ServersCreator(jenkins, github_env, pr_utils, ks_name)
    stack_text = server_creator.create_stack_text_from_template(params_dict)
    if not server_creator.is_stack_exists_in_master():
        master_build_num = server_creator.merge_pr(server_creator.create_pr(stack_text))
    else:
        master_build_num = jenkins.trigger_jenkins_job(MASTER_JOB, {'ks_id': f'{ks_name}', 'ks_env': 'sdlc'})['number']
    server_creator.validate_master_build(master_build_num)


def servers_creation_main(jenkins, github_env, pr_utils, _lab_params):
    try:
        run_workflow(jenkins, github_env, pr_utils, _lab_params)
    except Exception as e:
        print('An error occurred during servers creation, please check. Exception: {0}'.format(str(e)))
        traceback.print_tb(e.__traceback__)
        exit(1)




def create_params_dict_from_evnet_config(_lab_params, ks_name):
    params_dict = DEFAULT_PARAMS_DICT.copy()
    params_dict.update(_lab_params)
    params_dict.update(ks_name=ks_name)
    return params_dict

import backoff
import requests
import jenkins
import os

from .jenkins_custom_exception import JenkinsJobInvalidResultException

URLS = {'lego': 'https://lego-jenkins.kenshoo.com/', 'core': 'http://jenkins-prod-core.internalk.com/',
        'core-astronomer': "https://astronomer.kenshoo.com:10517/",
        'search': 'https://jenkins-prod-search.internalk.com/',
        'microcosom': 'https://jenkins-prod-microcosm.internalk.com/'}


class JenkinsInit:
    def __init__(self, jenkins_instance, build_result_max_time=360, user=None, token=None, wait_for_build_result=True):
        self.user_name = os.environ.get('jenkins_user')
        self.api_token = os.environ.get('jenkins_api_token')
        self.auth = self.user_name, self.api_token
        self.base_url = URLS[jenkins_instance]
        self.jobs_url = f'{self.base_url}job/'
        self.build_result_max_time = build_result_max_time
        self.jenkins_connection = jenkins.Jenkins(self.base_url, self.user_name, self.api_token)
        self.wait_for_build_result = wait_for_build_result

    def get_candidate_build(self, job_name):
        return requests.get(f'{self.jobs_url}{job_name}/lastBuild/api/json',
                            auth=self.auth,
                            ).json()['number'] + 1

    def get_build_result(self, job_name, build_number):
        @backoff.on_predicate(backoff.constant, lambda x: x is None, interval=10, max_time=self.build_result_max_time)
        def get_build_result_inner():
            try:
                build_info = self.jenkins_connection.get_build_info(name=job_name, number=build_number)
                if not build_info['building']:
                    return build_info['result']
            except jenkins.JenkinsException as e:
                if '] does not exist' in str(e):
                    return None
                else:
                    raise e
        return get_build_result_inner()

    @backoff.on_predicate(backoff.constant, lambda x: x is False, interval=10, max_time=600)
    def wait_for_job_to_start(self, queued_item_id):
        if self.jenkins_connection.get_queue_item(queued_item_id)['why'] is None:
            return True
        return False

    @backoff.on_predicate(backoff.constant, lambda x: x is None, interval=3, max_time=600)
    def wait_for_build_number(self, queued_item_id):
        queue_item_data = self.jenkins_connection.get_queue_item(queued_item_id)
        if 'executable' in queue_item_data:
            return queue_item_data['executable']['number']

    def build_jenkins_job(self, job_name, params):
        return self.jenkins_connection.build_job(name=job_name, parameters=params)

    def trigger_jenkins_job(self, job_name, params):
        queued_item_id = self.build_jenkins_job(job_name, params)
        build_number = self.wait_for_build_number(queued_item_id)
        build_url = f'{self.jobs_url}{job_name}/{build_number}/'
        print(f'Jenkins job triggered: {build_url}')
        self.wait_for_job_to_start(queued_item_id)
        return {'number': build_number,
                'result': self.get_build_result(job_name, build_number) if self.wait_for_build_result else None,
                'url': build_url
                }

    @staticmethod
    def validate_is_build_successful(build):
        if build['result'] != 'SUCCESS':
            raise JenkinsJobInvalidResultException(
                build['url'], build['number'], build['result'])
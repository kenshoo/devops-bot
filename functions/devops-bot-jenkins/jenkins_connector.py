import json
import os
import re
import logging
import jenkins
import boto3
from base64 import b64decode



new_jenkinses_pattern = "(.+)jenkins-prod-(\w)(.+)\/job\/(.+)\/(\d)+"
pulsar_pattern = "(.+)pulsar.kenshoo.com\/job\/(.+)\/(\d)+"
lego_pattern = "(.+)lego-jenkins\.(\w)(.+)\:8443\/job\/(.+)\/(\d)+"


def get_decrypted(encrypted_key):
    return boto3.client('kms').decrypt(
        CiphertextBlob=b64decode(encrypted_key),
        EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']})['Plaintext'].decode('utf-8')

def get_token_for_jenkins(jenkins_env):
    token = get_decrypted(encrypted_key = os.environ[f'{jenkins_env}_token'])
    return token

def is_valid_jenkins_url(job_url):
    if re.search(new_jenkinses_pattern, job_url) or re.search(pulsar_pattern, job_url) or re.search(lego_pattern, lego_pattern):
        return True
    return False

def split_job_relevant_data(job_url):
    relevant_params = job_url.split("/job/")
    url = relevant_params[0]
    job_data = relevant_params[1].split("/")
    job_name = job_data[0]
    build_number = job_data[1]
    print(url, job_name, build_number)
    return url, job_name, build_number

def get_jenkins_relevant_params(job_url):
    username = "jenkins_hubot@kenshootlv.local"
    if ('prod-search' in job_url):
        token = get_token_for_jenkins(jenkins_env='search')
        jenkins_url, job_name, build_number = split_job_relevant_data(job_url)
        return jenkins_url, job_name, build_number, username, token
    elif ('prod-microcosm' in job_url):
        token = get_token_for_jenkins(jenkins_env='microcosm')
        jenkins_url, job_name, build_number = split_job_relevant_data(job_url)
        return jenkins_url, job_name, build_number, username, token
    elif ('prod-core' in job_url):
        token = get_token_for_jenkins(jenkins_env='core')
        jenkins_url, job_name, build_number = split_job_relevant_data(job_url)
        return jenkins_url, job_name, build_number, username, token
    # elif ('lego-jenkins' in job_url)


def get_jenkins_job_console_output(job_url):
    if is_valid_jenkins_url(job_url):
        params = get_jenkins_relevant_params(job_url)
        if params:
            url, job, build_number, username, passwd = params
            server = jenkins.Jenkins(url, username=username, password=passwd)
            return server.get_build_console_output(job, int(build_number)).split('\n')
    raise Exception("Not a valid URL - valid url format https://<jenkins-url>/job/<job-name>/<build-number>\nExample: https://jenkins-prod-search.internalk.com/job/master-release/44033/\nPlease enter valid URL")
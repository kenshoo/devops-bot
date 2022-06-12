from github import Github
from github.GithubException import UnknownObjectException
from datetime import datetime
import os
import backoff


class PullRequestUtils:
    def __init__(self, repo_name, build_result_max_time=360):
        __conn = Github(os.getenv('GITHUB_TOKEN_LABS_CREATION'))
        self.repo_name = repo_name
        self.repo = __conn.get_repo(f'kenshoo/{self.repo_name}')
        self.side_branch_name = f'{os.getenv("JOB_NAME")}-{os.getenv("BUILD_ID")}-' \
                                f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")}'
        self.build_result_max_time = build_result_max_time

    def create_side_branch(self, side_branch_name=None):
        self.repo.create_git_ref(f'refs/heads/'
                                 f'{side_branch_name if side_branch_name is not None else self.side_branch_name}',
                                 self.repo.get_branch('master').commit.sha)

    def create_pr(self, pr_title='Automation PR', pr_description='Automation PR', side_branch_name=None):
        return self.repo.create_pull(pr_title, pr_description, 'master',
                                     side_branch_name if side_branch_name is not None else self.side_branch_name)

    def validate_pr_checks_is_success(self, pr_obj):
        @backoff.on_predicate(backoff.expo, max_time=self.build_result_max_time)
        def validate_pr_checks_is_success_inner():
            checks_status = list(pr_obj.get_commits())[-1].get_combined_status().state
            if checks_status == 'failure':
                raise Exception("PR checks failed")
            return checks_status == 'success'
        return validate_pr_checks_is_success_inner()

    def merge_pr(self, pr_obj, merge_message='Added by automation', method='squash'):
        if self.validate_pr_checks_is_success(pr_obj):
            return pr_obj.merge(merge_message, merge_method=method).merged
        return False

    def delete_branch(self, branch_name=None):
        try:
            ref = self.repo.get_git_ref(f"heads/{branch_name if branch_name is not None else self.side_branch_name}")
            ref.delete()
            return True
        except UnknownObjectException:
            print('No such branch', self.side_branch_name)
            return False

    def create_file(self, file_path, file_content, commit_message, side_branch_name=None):
        self.repo.create_file(file_path, commit_message, file_content,
                              branch=side_branch_name if side_branch_name is not None else self.side_branch_name)

    def update_file(self, file_path, new_content, commit_message='Changed by automation', branch=None):
        old_file_content = self.repo.get_contents(file_path)
        self.repo.update_file(file_path, commit_message, new_content,
                              old_file_content.sha,
                              branch=branch if branch is not None else self.side_branch_name)
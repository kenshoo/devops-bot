import os
from github import Github
from github.Label import Label


class GithubEnvironmentUtil(object):
    """
    Constructs a GithubEnvironmentUtil.
    :param environments: An a set of environments in which: for example: {"sdlc", "prod"}.
    :param path: the path to the folder where the environments are located in example: environments/
    :param hierarchy: an optinal to state what hirerarchy in the path to state the files you would like to use
    """

    def __init__(self, environments, path, repository=None, hierarchy=1):
        self.ENVIRONMENTS = frozenset(environments)
        self.LABELS = [Label(None, None, {"name": env}, None) for env in self.ENVIRONMENTS]
        self.GITHUB_CRED = 'kenshoo-build2', os.environ.get('GITHUB_TOKEN_LABS_CREATION', "")
        self.path = path
        self.repository = repository
        self.hierarchy = hierarchy
        self.git_command_map = {
            "pr": f"git diff `git merge-base origin/master HEAD`..HEAD --name-only {self.path}",
            "merge": f"git diff --name-only HEAD HEAD~1 --name-only {self.path}"
        }

    def update_environment_label(self):
        self.set_pr_environment_label(self.get_changes_environment())

    def validate_one_environment_change(self):
        number_changed_environments = len(self.get_changes_environment())
        return number_changed_environments <= 1

    def get_changes_environment(self, event="pr"):
        files = self.get_changed_files(self.git_command_map.get(event))
        files_path_splited = [file.split("/") for file in files if
                              len(file.split("/")) > 0 and file.split("/")[0] != '']
        return {file[self.hierarchy] for file in files_path_splited if len(file) > self.hierarchy}

    @staticmethod
    def get_changed_files(command):
        return os.popen(command).read().split("\n")

    def set_pr_environment_label(self, changed_environments):
        pull_request = self.get_pull_request_number()
        self.orgenize_labels(pull_request, changed_environments)

    def get_pull_request_number(self):
        return int(os.environ.get('CHANGE_ID'))

    def get_pull_request_labels(self):
        pull_request_number = self.get_pull_request_number()
        pull_request = self.get_github_pull_request_issue(pull_request_number)
        labels = [label.name for label in pull_request.get_labels()]
        return labels

    def orgenize_labels(self, pull_request_number, changed_environments):
        pullrequest_issue = self.get_github_pull_request_issue(pull_request_number)
        self.remove_label_from_pull_request_issue(pullrequest_issue, self.ENVIRONMENTS)
        for label in changed_environments:
            pullrequest_issue.add_to_labels(label)

    @staticmethod
    def remove_label_from_pull_request_issue(issue, labels):
        [issue.remove_from_labels(label) for label in issue.get_labels() if label.name in labels]

    def get_github_pull_request_issue(self, pull_request_number):
        return self.get_repo().get_issue(pull_request_number)

    def get_repo(self):
        if self.repository:
            return Github(*self.GITHUB_CRED).get_organization("kenshoo").get_repo(self.repository)
        raise Exception('in order to get_repo you have to provide repository name')

    def is_pr_merged(self, pr_id):
        return self.get_repo().get_pull(pr_id).merged

    def has_only_one_env_label(self, issue):
        issue_labels = {label.name for label in issue.get_labels()}
        return len(issue_labels.intersection(self.ENVIRONMENTS)) == 1

    def get_envs_to_build(self):
        repo = self.get_repo()
        return {label.name: [issue for issue in repo.get_issues(state="closed", labels=[label])
                             if self.has_only_one_env_label(issue) and self.is_pr_merged(issue.number)]
                for label in self.LABELS}

    def set_issue_comment(self, comment):
        pullrequest_issue = self.get_github_pull_request_issue(self.get_pull_request_number())
        pullrequest_issue.create_comment(comment)

    @staticmethod
    def file_exists_in_branch(file_name, branch):
        return file_name in os.popen(f"git ls-tree -r --name-only origin/{branch}").read().split('\n')

    def get_files_list_from_repo_master_branch(self, path='/'):
        return [file for file in self.get_repo().get_contents(path=path)]

    def get_file_content_from_repo(self, file_name):
        list_of_files_in_repo = self.get_files_list_from_repo_master_branch()
        for index in range(len(list_of_files_in_repo)):
            if self._is_file_name_equals(file_name, list_of_files_in_repo[index].name):
                return list_of_files_in_repo[index]

    def _is_file_name_equals(self, searched_file, file_in_repo):
        return searched_file == file_in_repo
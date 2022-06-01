class JenkinsJobInvalidResultException(Exception):
    """Exception raised for errors in the input jenkins job result.
    Attributes:
        candidate_build - candidate build that we currently running
        candidate_build_result -- input candidate_build_result which caused the error
        url - link to the failed jenkins job
    """
    def __init__(self, url, candidate_build, candidate_build_result):
        self.candidate_build = candidate_build
        self.candidate_build_result = candidate_build_result
        self.url = url
        self.message=f"The job isn't finish successful, job status: {candidate_build_result} \n link to job: \n\t {url}/{candidate_build}"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.candidate_build_result} -> {self.message}'

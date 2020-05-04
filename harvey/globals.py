# pylint: disable=R0903,C0114
class Global():
    """Contains global configuration for Harvey"""
    DOCKER_VERSION = 'v1.40' # Docker API version
    HARVEY_VERSION = '0.1.0' # Harvey release
    BASE_URL = f'http+unix://%2Fvar%2Frun%2Fdocker.sock/{DOCKER_VERSION}/'
    JSON_HEADERS = {'Content-Type': 'application/json'}
    TAR_HEADERS = {'Content-Type': 'application/tar'}
    ATTACH_HEADERS = {'Content-Type': 'application/vnd.docker.raw-stream'}
    PROJECTS_PATH = 'projects'
    PROJECTS_LOG_PATH = 'logs/projects'
    HARVEY_LOG_PATH = 'logs/harvey'

    @classmethod
    def repo_name(cls, webhook):
        """Return the repo name from the webhook JSON"""
        return webhook["repository"]["name"].lower()

    @classmethod
    def repo_full_name(cls, webhook):
        """Return the repo's full name from the webhook JSON"""
        return webhook["repository"]["full_name"].lower()

    @classmethod
    def repo_commit_author(cls, webhook):
        """Return the repo's commit author name from the webhook JSON"""
        return webhook["commits"][0]["author"]["name"]

    @classmethod
    def repo_url(cls, webhook):
        """Return the repo's URL from the webhook JSON"""
        return webhook["repository"]["ssh_url"] # Use SSH URL so private repos can be cloned/pulled

    @classmethod
    def repo_owner_name(cls, webhook):
        """Return the repo's owner's name from the webhook JSON"""
        return webhook["repository"]["owner"]["name"].lower()

    @classmethod
    def repo_commit_id(cls, webhook):
        """Return the repo's id from the webhook JSON"""
        return webhook["commits"][0]["id"]

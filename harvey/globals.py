import os


class Global:
    DOCKER_VERSION = 'v1.41'  # Docker API version
    # TODO: Figure out how to sync this version number with the one in `setup.py`
    HARVEY_VERSION = '0.14.0'  # Harvey release
    PROJECTS_PATH = 'projects'
    PROJECTS_LOG_PATH = 'logs/projects'
    HARVEY_LOG_PATH = 'logs/harvey'
    DEPLOY_TIMEOUT = 1800  # 30 minutes
    GIT_TIMEOUT = 300
    BASE_URL = f'http+unix://%2Fvar%2Frun%2Fdocker.sock/{DOCKER_VERSION}/'
    FILTER_WEBHOOKS = os.getenv('FILTER_WEBHOOKS', False)
    ALLOWED_BRANCHES = [branch.strip().lower() for branch in os.getenv('ALLOWED_BRANCHES', 'main,master').split(',')]
    SLACK = os.getenv('SLACK')
    SUPPORTED_PIPELINES = [
        'pull',
        'test',
        'deploy',
        'full',
    ]

    @staticmethod
    def repo_name(webhook):
        """Return the repo name from the webhook JSON."""
        return webhook['repository']['name'].lower()

    @staticmethod
    def repo_full_name(webhook):
        """Return the repo's full name from the webhook JSON."""
        return webhook['repository']['full_name'].lower()

    @staticmethod
    def repo_commit_author(webhook):
        """Return the repo's commit author name from the webhook JSON."""
        return webhook['commits'][0]['author']['name']

    @staticmethod
    def repo_url(webhook):
        """Return the repo's URL from the webhook JSON."""
        return webhook['repository']['ssh_url']  # Use SSH URL so private repos can be cloned/pulled

    @staticmethod
    def repo_owner_name(webhook):
        """Return the repo's owner's name from the webhook JSON."""
        return webhook['repository']['owner']['name'].lower()

    @staticmethod
    def repo_commit_id(webhook):
        """Return the repo's id from the webhook JSON."""
        return webhook['commits'][0]['id']

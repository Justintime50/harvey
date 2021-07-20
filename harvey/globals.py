import ipaddress
import os


class Global():
    """Contains global configuration for Harvey
    """
    DOCKER_VERSION = 'v1.41'  # Docker API version
    # TODO: Figure out how to sync this version number with the one in `setup.py`
    HARVEY_VERSION = '0.11.0'  # Harvey release
    PROJECTS_PATH = 'projects'
    PROJECTS_LOG_PATH = 'logs/projects'
    HARVEY_LOG_PATH = 'logs/harvey'
    BUILD_TIMEOUT = 1800  # 30 minutes
    GIT_TIMEOUT = 180
    BASE_URL = f'http+unix://%2Fvar%2Frun%2Fdocker.sock/{DOCKER_VERSION}/'
    JSON_HEADERS = {'Content-Type': 'application/json'}
    TAR_HEADERS = {'Content-Type': 'application/tar'}
    APP_MODE = os.getenv('MODE', 'production').lower()
    FILTER_WEBHOOKS = os.getenv('FILTER_WEBHOOKS', False)
    ALLOWED_BRANCHES = [
        'refs/heads/master',
        'refs/heads/main',
    ]
    SUPPORTED_PIPELINES = [
        'pull',
        'test',
        'deploy',
        'full'
    ]
    # TODO: Get these directly from the API instead of a static list
    GITHUB_WEBHOOK_IP_RANGES = [
        '192.30.252.0/22',
        '185.199.108.0/22',
        '140.82.112.0/20',
        '143.55.64.0/20',
    ]

    @classmethod
    def repo_name(cls, webhook):
        """Return the repo name from the webhook JSON
        """
        return webhook['repository']['name'].lower()

    @classmethod
    def repo_full_name(cls, webhook):
        """Return the repo's full name from the webhook JSON
        """
        return webhook['repository']['full_name'].lower()

    @classmethod
    def repo_commit_author(cls, webhook):
        """Return the repo's commit author name from the webhook JSON
        """
        return webhook['commits'][0]['author']['name']

    @classmethod
    def repo_url(cls, webhook):
        """Return the repo's URL from the webhook JSON
        """
        return webhook['repository']['ssh_url']  # Use SSH URL so private repos can be cloned/pulled

    @classmethod
    def repo_owner_name(cls, webhook):
        """Return the repo's owner's name from the webhook JSON
        """
        return webhook['repository']['owner']['name'].lower()

    @classmethod
    def repo_commit_id(cls, webhook):
        """Return the repo's id from the webhook JSON
        """
        return webhook['commits'][0]['id']

    @classmethod
    def docker_project_name(cls, webhook):
        """Return the project name to be used for containers and images
        """
        return f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}'

    @classmethod
    def github_webhook_ip_ranges(cls):
        """Returns a list of public IP addresses GitHub sends webhooks from

        TODO: Refactor this so it's not a static list but a list pulled from GitHub
        and stored in redis or a database:

        https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/about-githubs-ip-addresses  # noqa
        """
        ip_address_list = [str(ip_address) for ip_range in Global.GITHUB_WEBHOOK_IP_RANGES
                           for ip_address in ipaddress.IPv4Network(ip_range)]

        # Keep localhost included for testing
        ip_address_list.append('127.0.0.1')

        return ip_address_list

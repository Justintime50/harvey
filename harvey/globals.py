import ipaddress
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
    # TODO: Get these directly from the API instead of a static list
    GITHUB_WEBHOOK_IP_RANGES = [
        '192.30.252.0/22',
        '185.199.108.0/22',
        '140.82.112.0/20',
        '143.55.64.0/20',
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

    @staticmethod
    def github_webhook_ip_ranges():
        """Returns a list of public IP addresses GitHub sends webhooks from.

        TODO: Refactor this so it's not a static list but a list pulled from GitHub
        and stored in redis or a database:

        https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/about-githubs-ip-addresses
        """
        ip_address_list = [
            str(ip_address)
            for ip_range in Global.GITHUB_WEBHOOK_IP_RANGES
            for ip_address in ipaddress.IPv4Network(ip_range)
        ]

        # Keep localhost included for testing
        ip_address_list.append('127.0.0.1')

        return ip_address_list

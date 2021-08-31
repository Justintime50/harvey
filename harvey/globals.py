import ipaddress
import os
import re


class Global:
    DOCKER_VERSION = 'v1.41'  # Docker API version
    # TODO: Figure out how to sync this version number with the one in `setup.py`
    HARVEY_VERSION = '0.13.1'  # Harvey release
    PROJECTS_PATH = 'projects'
    PROJECTS_LOG_PATH = 'logs/projects'
    HARVEY_LOG_PATH = 'logs/harvey'
    BUILD_TIMEOUT = 1800  # 30 minutes
    GIT_TIMEOUT = 300
    BASE_URL = f'http+unix://%2Fvar%2Frun%2Fdocker.sock/{DOCKER_VERSION}/'
    JSON_HEADERS = {'Content-Type': 'application/json'}
    TAR_HEADERS = {'Content-Type': 'application/tar'}
    APP_MODE = os.getenv('MODE', 'production').lower()
    FILTER_WEBHOOKS = os.getenv('FILTER_WEBHOOKS', False)
    ALLOWED_BRANCHES = [branch.strip().lower() for branch in os.getenv('ALLOWED_BRANCHES', 'main,master').split(',')]
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
    def docker_project_name(webhook):
        """Return the project name to be used for containers and images.

        This name is the same format for compose and non-compose containers but assumes
        that the `container_name` or `service_name` fields match the repo name found on GitHub.

        NOTE: (From the Docker API docs) - Because Docker container names must be unique, you cannot scale a
        service beyond 1 container if you have specified a custom name. Attempting to do so results in an error.

        TODO: Investigate why some container names have a `_1` appended and others don't (Docker's default behavior?)
        """
        project_name = f'harvey_{Global.repo_owner_name(webhook)}_{Global.repo_name(webhook)}'

        # We strip non-alphanumeric characters in the name because Docker does the same
        strip_non_alphanumeric = re.compile('[^a-zA-Z0-9_-]')
        docker_formatted_project_name = strip_non_alphanumeric.sub('', project_name)

        return docker_formatted_project_name

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

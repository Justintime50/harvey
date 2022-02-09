import os
from typing import Any, Dict

from dotenv import load_dotenv

from version import VERSION

load_dotenv()  # Must remain at the top of this file


class Global:
    # TODO: Reconfigure all these constants and static methods below to be class variables/properties
    # User configurable settings
    ALLOWED_BRANCHES = [branch.strip().lower() for branch in os.getenv('ALLOWED_BRANCHES', 'main,master').split(',')]
    DEPLOY_TIMEOUT = int(os.getenv('DEPLOY_TIMEOUT', 1800))  # Default is 30 minutes
    GIT_TIMEOUT = int(os.getenv('GIT_TIMEOUT', 300))  # Default is 5 minutes
    PAGINATION_LIMIT = int(os.getenv('PAGINATION_LIMIT', 20))
    DEPLOY_ON_TAG = os.getenv('DEPLOY_ON_TAG', True)  # Whether a tag pushed will trigger a deploy or not
    SLACK = os.getenv('SLACK')

    # Harvey constants
    HARVEY_VERSION = VERSION
    SUPPORTED_PIPELINES = {
        'deploy',
        'pull',
    }

    # Paths
    HARVEY_PATH = os.getenv('HARVEY_PATH', os.path.expanduser('~/harvey'))
    PROJECTS_PATH = os.path.join(HARVEY_PATH, 'projects')
    STORES_PATH = os.path.join(HARVEY_PATH, 'stores')
    PIPELINES_STORE_PATH = os.path.join(STORES_PATH, 'pipelines.sqlite')
    LOCKS_STORE_PATH = os.path.join(STORES_PATH, 'locks.sqlite')

    # Emoji (used for Slack messages, set defaults if slack isn't in use)
    # TODO: Defaults are nice for when slack isn't in use; however, the emoji text will
    # still show up in log files, we should be writting the fallback message to logs instead of emojis
    WORK_EMOJI = ':hammer_and_wrench:' if SLACK else ''
    SUCCESS_EMOJI = ':white_check_mark:' if SLACK else 'Success!'
    FAILURE_EMOJI = ':skull_and_crossbones:' if SLACK else 'Failure!'

    @staticmethod
    def repo_name(webhook: Dict[str, Any]) -> str:
        """Return the repo name from the webhook JSON."""
        return webhook['repository']['name'].lower()

    @staticmethod
    def repo_full_name(webhook: Dict[str, Any]) -> str:
        """Return the repo's full name from the webhook JSON."""
        return webhook['repository']['full_name'].lower()

    @staticmethod
    def repo_commit_author(webhook: Dict[str, Any]) -> str:
        """Return the repo's commit author name from the webhook JSON."""
        return webhook['commits'][0]['author']['name']

    @staticmethod
    def repo_url(webhook: Dict[str, Any]) -> str:
        """Return the repo's URL from the webhook JSON."""
        return webhook['repository']['ssh_url']  # Use SSH URL so private repos can be cloned/pulled

    @staticmethod
    def repo_owner_name(webhook: Dict[str, Any]) -> str:
        """Return the repo's owner's name from the webhook JSON."""
        return webhook['repository']['owner']['name'].lower()

    @staticmethod
    def repo_commit_id(webhook: Dict[str, Any]) -> str:
        """Return the repo's id from the webhook JSON."""
        return str(webhook['commits'][0]['id'])

    @staticmethod
    def pipeline_id(webhook: Dict[str, Any]) -> str:
        """Return the pipeline ID used for the SQLite stores."""
        return f'{Global.repo_full_name(webhook).replace("/", "-")}@{Global.repo_commit_id(webhook)}'

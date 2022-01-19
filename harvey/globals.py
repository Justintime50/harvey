import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()  # Must remain at the top of this file


class Global:
    # TODO: Reconfigure all these constants and static methods below to be class variables/properties
    ALLOWED_BRANCHES = [branch.strip().lower() for branch in os.getenv('ALLOWED_BRANCHES', 'main,master').split(',')]
    DEPLOY_TIMEOUT = 1800  # 30 minutes
    GIT_TIMEOUT = 300  # 5 minutes
    HARVEY_LOG_PATH = os.path.join('logs', 'harvey')
    # TODO: Is there a way to sync this with `setup.py`? (short answer: not easily since you can't import this there)
    HARVEY_VERSION = '0.15.0'
    PROJECTS_PATH = os.path.expanduser('~/harvey/projects')
    STORES_PATH = os.path.expanduser('~/harvey/stores')
    PIPELINES_STORE_PATH = os.path.join(STORES_PATH, 'pipelines.sqlite')
    LOCKS_STORE_PATH = os.path.join(STORES_PATH, 'locks.sqlite')
    SLACK = os.getenv('SLACK')
    SUPPORTED_PIPELINES = {
        'deploy',
        'pull',
    }
    PAGINATION_LIMIT = 100

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

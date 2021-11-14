import os

import woodchips
from dotenv import load_dotenv

load_dotenv()  # Must remain at the top of this file


class Global:
    # TODO: Reconfigure all these constants and static methods below to be class variables/properties
    ALLOWED_BRANCHES = [branch.strip().lower() for branch in os.getenv('ALLOWED_BRANCHES', 'main,master').split(',')]
    DEPLOY_TIMEOUT = 1800  # 30 minutes
    GIT_TIMEOUT = 300  # 5 minutes
    HARVEY_LOG_PATH = 'logs/harvey'
    # TODO: Is there a way to sync this with `setup.py`? (short answer: not easily since you can't import this there)
    HARVEY_VERSION = '0.15.0'
    PROJECTS_LOG_PATH = 'logs/projects'
    PROJECTS_PATH = 'projects'
    SLACK = os.getenv('SLACK')
    SUPPORTED_PIPELINES = {
        'deploy',
        'pull',
    }

    # TODO: We should be able to prepend every logged message with the name of the repo for easy organization and
    # searching of log files, this will most likely require a change on the woodchips side to allow for this config
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOGGER = woodchips.setup(
        logger_name=__name__,
        log_location=os.path.expanduser('~/harvey/logs'),
        log_level=LOG_LEVEL,
    )

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
        return str(webhook['commits'][0]['id'])

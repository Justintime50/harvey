import datetime
import os
import sys
from typing import Any, Dict

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.globals import Global
from harvey.messages import Message

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOGGER_NAME = 'harvey'
LOG_LOCATION = os.path.join(Global.HARVEY_PATH, 'logs')


class Utils:
    @staticmethod
    def kill(final_output: str, webhook: Dict[str, Any]):
        """A kill util to write everything to logs, send messages,
        tear down Docker stuff, and quit.
        """
        logger = woodchips.get(LOGGER_NAME)

        failure_message = f'{Global.repo_full_name(webhook)} pipeline failed!'
        logger.warning(failure_message)

        pipeline_logs = final_output + failure_message
        Utils.store_pipeline_details(webhook, pipeline_logs)

        if Global.SLACK:
            Message.send_slack_message(pipeline_logs)

        Utils.update_project_lock(webhook=webhook, locked=False)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def success(final_output: str, webhook: Dict[str, Any]):
        """Log output and send message on pipeline success."""
        logger = woodchips.get(LOGGER_NAME)

        success_message = f'{Global.repo_full_name(webhook)} pipeline succeeded!'
        logger.info(success_message)

        pipeline_logs = final_output + success_message
        Utils.store_pipeline_details(webhook, pipeline_logs)

        if Global.SLACK:
            Message.send_slack_message(pipeline_logs)

        Utils.update_project_lock(webhook=webhook, locked=False)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def store_pipeline_details(webhook: Dict[str, Any], final_output: str = 'NA'):
        """Store the pipeline's details including logs and metadata to a Sqlite database.

        A project ID consists of the `project_name@commit_id`.
        """
        logger = woodchips.get(LOGGER_NAME)

        logger.debug(f'Storing pipeline details for {Global.repo_full_name(webhook)}...')

        with SqliteDict(Global.PIPELINES_STORE_PATH) as mydict:
            # Naively check the logs for an indicator of the status being success
            if 'success' in final_output.lower() or 'succeeded' in final_output.lower():
                pipeline_status = 'Success'
            elif final_output == 'NA':
                pipeline_status = 'In-Progress'
            else:
                pipeline_status = 'Failure'

            mydict[Global.pipeline_id(webhook)] = {
                'project': Global.repo_full_name(webhook).replace("/", "-"),
                'commit': Global.repo_commit_id(webhook),
                'log': final_output,
                'status': pipeline_status,
                'timestamp': str(datetime.datetime.utcnow()),
            }

            mydict.commit()

    @staticmethod
    def update_project_lock(webhook: Dict[str, Any], locked: bool = False):
        """Locks or unlocks the project's deployments to ensure we don't crash Docker with two inflight deployments.

        Locking should only happen once a pipeline is begun. A locked deployment should then always be
        unlocked once it's finished regardless of status so another deployment can follow.
        """
        logger = woodchips.get(LOGGER_NAME)

        locked_string = 'Locking' if locked is True else 'Unlocking'
        logger.info(f'{locked_string} deployments for {Global.repo_full_name(webhook)}...')

        with SqliteDict(Global.LOCKS_STORE_PATH) as mydict:
            mydict[Global.repo_full_name(webhook).replace("/", "-")] = {
                'locked': locked,
            }

            mydict.commit()

    @staticmethod
    def lookup_project_lock(project_name: str) -> bool:
        """Checks if a project is locked or not by its full name."""
        locked_value = False
        corrected_project_name = project_name.replace("/", "-")

        with SqliteDict(Global.LOCKS_STORE_PATH) as mydict:
            for key, value in mydict.iteritems():
                if key == corrected_project_name:
                    locked_value = value['locked']
                    break

        return locked_value


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=LOGGER_NAME,
        level=LOG_LEVEL,
    )
    logger.log_to_console()
    logger.log_to_file(location=LOG_LOCATION)

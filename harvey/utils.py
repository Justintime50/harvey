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
LOG_LOCATION = os.path.expanduser(os.path.join('~', 'harvey', 'logs'))


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
        Utils.store_pipeline_details(pipeline_logs, webhook)

        if Global.SLACK:
            Message.send_slack_message(pipeline_logs)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def success(final_output: str, webhook: Dict[str, Any]):
        """Log output and send message on pipeline success."""
        logger = woodchips.get(LOGGER_NAME)

        success_message = f'{Global.repo_full_name(webhook)} pipeline succeeded!'
        logger.info(success_message)

        pipeline_logs = final_output + success_message
        Utils.store_pipeline_details(pipeline_logs, webhook)

        if Global.SLACK:
            Message.send_slack_message(pipeline_logs)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def store_pipeline_details(final_output: str, webhook: Dict[str, Any]):
        """Store the pipeline's details including logs and metadata to a Sqlite database."""
        logger = woodchips.get(LOGGER_NAME)

        logger.debug(f'Generating pipeline logs for {Global.repo_full_name(webhook)}...')

        if not os.path.exists(Global.STORES_PATH):
            os.mkdir(Global.STORES_PATH)

        with SqliteDict(Global.PIPELINES_STORE_PATH) as mydict:
            pipeline_status = (
                'Success' if 'success' in final_output.lower() or 'succeeded' in final_output.lower() else 'Failure'
            )  # Naively check the logs for an indicator of the status being success

            mydict[f'{Global.repo_full_name(webhook).replace("/", "-")}-{Global.repo_commit_id(webhook)}'] = {
                'commit': Global.repo_commit_id(webhook),
                'log': final_output,
                'status': pipeline_status,
                'timestamp': str(datetime.datetime.utcnow()),
            }
            mydict.commit()


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=LOGGER_NAME,
        level=LOG_LEVEL,
    )
    logger.log_to_console()

    # TODO: We should be able to prepend every logged message with the name of the repo for easy organization and
    # searching of log files
    logger.log_to_file(location=LOG_LOCATION)

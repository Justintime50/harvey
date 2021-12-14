import os
import sys
from typing import Any, Dict

import woodchips

from harvey.globals import Global
from harvey.messages import Message

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOGGER_NAME = 'harvey'


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
        Utils.generate_pipeline_logs(pipeline_logs, webhook)

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
        Utils.generate_pipeline_logs(pipeline_logs, webhook)

        if Global.SLACK:
            Message.send_slack_message(pipeline_logs)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def generate_pipeline_logs(final_output: str, webhook: Dict[str, Any]):
        """Generate a complete log file with the entire pipeline's output.

        These logs are not to be confused with the internal Harvey `woodchips` logs for the
        app itself; instead, there is a log file for every project deployed via Harvey that
        contains the details of the last deploy of that service on the platform.
        """
        logger = woodchips.get(LOGGER_NAME)

        logger.debug(f'Generating pipeline logs for {Global.repo_full_name(webhook)}...')

        project_log_name = f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}.log'
        project_log_path = os.path.join(Global.PROJECTS_LOG_PATH, project_log_name)

        try:
            with open(project_log_path, 'w') as log:
                log.write(final_output)
        except OSError as error:
            final_output = f'Harvey could not save the log file for {Global.repo_full_name(webhook)}.'
            logger.error(error)
            Utils.kill(final_output, webhook)


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=LOGGER_NAME,
        level=LOG_LEVEL,
    )
    logger.log_to_console()

    # TODO: We should be able to prepend every logged message with the name of the repo for easy organization and
    # searching of log files
    logger.log_to_file(location=os.path.expanduser('~/harvey/logs'))

import os
import sys
from typing import Any, Dict

import woodchips

from harvey.globals import Global
from harvey.messages import Message

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOGGER_NAME = 'harvey'


class Utils:
    # TODO: None of these need this class or get anything from it, let's flatten these utilities as needed
    @staticmethod
    def kill(final_output: str, webhook: Dict[str, Any]):
        """A kill util to write everything to logs, send messages,
        tear down Docker stuff, and quit.
        """
        logger = woodchips.get(LOGGER_NAME)

        Utils.generate_pipeline_logs(final_output, webhook)
        logger.warning(f'{Global.repo_full_name(webhook)} pipeline failed!')

        if Global.SLACK:
            Message.send_slack_message(final_output)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def success(final_output: str, webhook: Dict[str, Any]):
        """Log output and send message on pipeline success."""
        logger = woodchips.get(LOGGER_NAME)

        Utils.generate_pipeline_logs(final_output, webhook)
        logger.info(f'{Global.repo_full_name(webhook)} pipeline succeeded!')

        if Global.SLACK:
            Message.send_slack_message(final_output)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def generate_pipeline_logs(final_output: str, webhook: Dict[str, Any]):
        """Generate a complete log file with the entire pipeline's output."""
        logger = woodchips.get(LOGGER_NAME)

        logger.debug(f'Generating pipeline logs for {Global.repo_full_name(webhook)}...')

        pipeline_log_path = os.path.join(Global.PROJECTS_LOG_PATH, Global.repo_full_name(webhook))
        if not os.path.exists(pipeline_log_path):
            os.makedirs(pipeline_log_path)

        try:
            filename = os.path.join(pipeline_log_path, Global.repo_commit_id(webhook) + '.log')
            with open(filename, 'w') as log:
                log.write(final_output)
        except OSError as error:
            final_output = 'Harvey could not save the log file.'
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

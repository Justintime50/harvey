import datetime
import os
from typing import Any, Dict

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.locks import Lock
from harvey.messages import Message
from harvey.webhooks import Webhook


class Utils:
    @staticmethod
    def kill(final_output: str, webhook: Dict[str, Any]):
        """Log output, send message, and cleanup on pipeline failure."""
        logger = woodchips.get(Config.logger_name)

        failure_message = f'{Webhook.repo_full_name(webhook)} pipeline failed!'
        logger.warning(failure_message)

        pipeline_logs = final_output + failure_message
        Utils.store_pipeline_details(webhook, Utils._strip_emojis_from_logs(pipeline_logs))

        if Config.use_slack:
            Message.send_slack_message(pipeline_logs)

        _ = Lock.update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

        # Exit the thread safely to ensure we don't continue executing
        # TODO: This kills the entire Docker container and not just the thread
        os._exit(1)

    @staticmethod
    def success(final_output: str, webhook: Dict[str, Any]):
        """Log output, send message, and cleanup on pipeline success."""
        logger = woodchips.get(Config.logger_name)

        success_message = f'{Webhook.repo_full_name(webhook)} pipeline succeeded!'
        logger.info(success_message)

        pipeline_logs = final_output + success_message
        Utils.store_pipeline_details(webhook, Utils._strip_emojis_from_logs(pipeline_logs))

        if Config.use_slack:
            Message.send_slack_message(pipeline_logs)

        _ = Lock.update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

        # Exit the thread safely to ensure we don't continue executing
        # TODO: This kills the entire Docker container and not just the thread
        os._exit(1)

    @staticmethod
    def _strip_emojis_from_logs(output: str) -> str:
        """Replace the emojis for logs since they won't render properly there."""
        logs_without_emoji = (
            output.replace(Message.success_emoji, 'Success!')
            .replace(Message.failure_emoji, 'Failure!')
            .replace(Message.work_emoji, '')
        )

        return logs_without_emoji

    @staticmethod
    def store_pipeline_details(webhook: Dict[str, Any], final_output: str = 'NA'):
        """Store the pipeline's details including logs and metadata to a Sqlite database.

        A project ID consists of the `project_name@commit_id`.
        """
        logger = woodchips.get(Config.logger_name)

        logger.debug(f'Storing pipeline details for {Webhook.repo_full_name(webhook)}...')

        with SqliteDict(Config.pipelines_store_path) as mydict:
            # Naively check the logs for an indicator of the status being success
            if 'success' in final_output.lower() or 'succeeded' in final_output.lower():
                pipeline_status = 'Success'
            elif final_output == 'NA':
                pipeline_status = 'In-Progress'
            else:
                pipeline_status = 'Failure'

            mydict[Webhook.pipeline_id(webhook)] = {
                'project': Webhook.repo_full_name(webhook).replace("/", "-"),
                'commit': Webhook.repo_commit_id(webhook),
                'log': final_output,
                'status': pipeline_status,
                'timestamp': str(datetime.datetime.utcnow()),
            }

            mydict.commit()


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=Config.logger_name,
        level=Config.log_level,
    )
    logger.log_to_console()
    logger.log_to_file(location=Config.log_location)

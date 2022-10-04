import datetime
import sys
from typing import (
    Any,
    Dict,
)

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.locks import Lock
from harvey.messages import Message
from harvey.webhooks import Webhook


DEPLOYMENTS_DATABASE_TABLE_NAME = 'deployments'


class Utils:
    @staticmethod
    def kill(final_output: str, webhook: Dict[str, Any]):
        """Log output, send message, and cleanup on deployment failure."""
        logger = woodchips.get(Config.logger_name)

        failure_message = f'{Webhook.repo_full_name(webhook)} deployment failed!'
        logger.warning(failure_message)

        deployment_logs = final_output + failure_message
        Utils.store_deployment_details(webhook, Utils._strip_emojis_from_logs(deployment_logs))

        if Config.use_slack:
            Message.send_slack_message(deployment_logs)

        _ = Lock.update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

        # Exit the thread safely to ensure we don't continue executing
        # TODO: This raises an error which we don't want
        sys.exit(1)

    @staticmethod
    def success(final_output: str, webhook: Dict[str, Any]):
        """Log output, send message, and cleanup on deployment success."""
        logger = woodchips.get(Config.logger_name)

        success_message = f'{Webhook.repo_full_name(webhook)} deployment succeeded!'
        logger.info(success_message)

        deployment_logs = final_output + success_message
        Utils.store_deployment_details(webhook, Utils._strip_emojis_from_logs(deployment_logs))

        if Config.use_slack:
            Message.send_slack_message(deployment_logs)

        _ = Lock.update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

        # Exit the thread safely to ensure we don't continue executing
        # TODO: This raises an error which we don't want
        sys.exit(1)

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
    def store_deployment_details(webhook: Dict[str, Any], final_output: str = 'NA'):
        """Store the deployment's details including logs and metadata to a Sqlite database.

        A project ID consists of the `project_name@commit_id`.
        """
        logger = woodchips.get(Config.logger_name)

        logger.debug(f'Storing deployment details for {Webhook.repo_full_name(webhook)}...')

        with SqliteDict(filename=Config.database_file, tablename=DEPLOYMENTS_DATABASE_TABLE_NAME) as database_table:
            # Naively check the logs for an indicator of the status being success
            if 'success' in final_output.lower() or 'succeeded' in final_output.lower():
                deployment_status = 'Success'
            elif final_output == 'NA':
                deployment_status = 'In-Progress'
            else:
                deployment_status = 'Failure'

            database_table[Webhook.deployment_id(webhook)] = {
                'project': Webhook.repo_full_name(webhook).replace("/", "-"),
                'commit': Webhook.repo_commit_id(webhook),
                'log': final_output,
                'status': deployment_status,
                'timestamp': str(datetime.datetime.utcnow()),
            }

            database_table.commit()


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=Config.logger_name,
        level=Config.log_level,
    )
    logger.log_to_console()
    logger.log_to_file(location=Config.log_location)

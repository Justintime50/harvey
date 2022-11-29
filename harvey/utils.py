import datetime
import sys
from typing import (
    Any,
    Dict,
    Optional,
)

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.errors import HarveyError
from harvey.locks import Lock
from harvey.messages import Message
from harvey.webhooks import Webhook


DEPLOYMENTS_DATABASE_TABLE_NAME = 'deployments'


class Utils:
    @staticmethod
    def kill_deployment(message: str, webhook: Dict[str, Any], raise_error: Optional[bool] = False):
        """Log output, send message, and cleanup on deployment failure."""
        logger = woodchips.get(Config.logger_name)

        error_message = f'{Webhook.repo_full_name(webhook)} deployment failed: {message}'
        logger.error(error_message)

        Utils.store_deployment_details(webhook, Utils._strip_emojis_from_logs(error_message))

        if Config.use_slack:
            Message.send_slack_message(error_message)

        # Only unlock deployments that were locked by the system and not a user to preserve their preferences
        deployment_lock = Lock.lookup_project_lock(project_name=Webhook.repo_full_name(webhook))
        if deployment_lock['system_lock']:
            _ = Lock.update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

        if raise_error:
            raise HarveyError(error_message)

        sys.exit(1)

    @staticmethod
    def succeed_deployment(message: str, webhook: Dict[str, Any]):
        """Log output, send message, and cleanup on deployment success."""
        logger = woodchips.get(Config.logger_name)

        success_message = f'{Webhook.repo_full_name(webhook)} deployment succeeded!'
        logger.info(success_message)

        deployment_logs = message + success_message
        Utils.store_deployment_details(webhook, Utils._strip_emojis_from_logs(deployment_logs))

        if Config.use_slack:
            Message.send_slack_message(deployment_logs)

        _ = Lock.update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

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

        try:
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
        except Exception as error:
            Utils.kill_deployment(
                message=f'Could not store deployment details to database: {error}',
                webhook=webhook,
                raise_error=True,
            )


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=Config.logger_name,
        level=Config.log_level,
    )
    logger.log_to_console()
    logger.log_to_file(location=Config.log_location)

import datetime
import sys
from typing import Any, Dict

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.messages import Message
from harvey.webhooks import Webhook


class Utils:
    @staticmethod
    def kill(final_output: str, webhook: Dict[str, Any]):
        """A kill util to write everything to logs, send messages,
        tear down Docker stuff, and quit.
        """
        logger = woodchips.get(Config.logger_name)

        failure_message = f'{Webhook.repo_full_name(webhook)} pipeline failed!'
        logger.warning(failure_message)

        pipeline_logs = final_output + failure_message
        Utils.store_pipeline_details(webhook, Utils._strip_emojis_from_logs(pipeline_logs))

        if Config.use_slack:
            Message.send_slack_message(pipeline_logs)

        Utils.update_project_lock(webhook=webhook, locked=False)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def success(final_output: str, webhook: Dict[str, Any]):
        """Log output and send message on pipeline success."""
        logger = woodchips.get(Config.logger_name)

        success_message = f'{Webhook.repo_full_name(webhook)} pipeline succeeded!'
        logger.info(success_message)

        pipeline_logs = final_output + success_message
        Utils.store_pipeline_details(webhook, Utils._strip_emojis_from_logs(pipeline_logs))

        if Config.use_slack:
            Message.send_slack_message(pipeline_logs)

        Utils.update_project_lock(webhook=webhook, locked=False)

        # Close the thread safely
        sys.exit()

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

    @staticmethod
    def update_project_lock(webhook: Dict[str, Any], locked: bool = False):
        """Locks or unlocks the project's deployments to ensure we don't crash Docker with two inflight deployments.

        Locking should only happen once a pipeline is begun. A locked deployment should then always be
        unlocked once it's finished regardless of status so another deployment can follow.
        """
        logger = woodchips.get(Config.logger_name)

        locked_string = 'Locking' if locked is True else 'Unlocking'
        logger.info(f'{locked_string} deployments for {Webhook.repo_full_name(webhook)}...')

        with SqliteDict(Config.locks_store_path) as mydict:
            mydict[Webhook.repo_full_name(webhook).replace("/", "-")] = {
                'locked': locked,
            }

            mydict.commit()

    @staticmethod
    def lookup_project_lock(project_name: str) -> bool:
        """Checks if a project is locked or not by its full name."""
        locked_value = False
        corrected_project_name = project_name.replace("/", "-")

        with SqliteDict(Config.locks_store_path) as mydict:
            for key, value in mydict.iteritems():
                if key == corrected_project_name:
                    locked_value = value['locked']
                    break

        return locked_value


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=Config.logger_name,
        level=Config.log_level,
    )
    logger.log_to_console()
    logger.log_to_file(location=Config.log_location)

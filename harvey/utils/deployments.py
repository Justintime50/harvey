import sys
from typing import (
    Any,
    Dict,
    Optional,
)

import woodchips

from harvey.config import Config
from harvey.errors import HarveyError
from harvey.messages import Message
from harvey.repos.deployments import store_deployment_details
from harvey.repos.locks import (
    lookup_project_lock,
    update_project_lock,
)
from harvey.webhooks import Webhook


def kill_deployment(message: str, webhook: Dict[str, Any], raise_error: Optional[bool] = False):
    """Log output, send message, and cleanup on deployment failure."""
    logger = woodchips.get(Config.logger_name)

    error_message = f'{Message.failure_emoji} `{Webhook.repo_full_name(webhook)}` deployment failed!'
    logger.error(_strip_emojis_from_logs(error_message))

    deployment_logs = error_message + '\n' + message
    store_deployment_details(webhook, _strip_emojis_from_logs(deployment_logs))

    # Only unlock deployments that were locked by the system and not a user to preserve their preferences
    deployment_lock = lookup_project_lock(project_name=Webhook.repo_full_name(webhook))
    if deployment_lock.get('system_lock'):
        update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

    if Config.use_slack:
        Message.send_slack_message(error_message)

    if raise_error:
        raise HarveyError(error_message)

    sys.exit(1)


def succeed_deployment(message: str, webhook: Dict[str, Any]):
    """Log output, send message, and cleanup on deployment success."""
    logger = woodchips.get(Config.logger_name)

    success_message = f'{Message.success_emoji} `{Webhook.repo_full_name(webhook)}` deployment succeeded!'
    logger.info(_strip_emojis_from_logs(success_message))

    deployment_logs = success_message + '\n' + message
    store_deployment_details(webhook, _strip_emojis_from_logs(deployment_logs))

    update_project_lock(project_name=Webhook.repo_full_name(webhook), locked=False)

    if Config.use_slack:
        Message.send_slack_message(success_message)

    sys.exit(1)


def _strip_emojis_from_logs(output: str) -> str:
    """Replace the emojis for logs since they won't render properly there."""
    logs_without_emoji = (
        output.replace(Message.success_emoji, 'Success!')
        .replace(Message.failure_emoji, 'Failure!')
        .replace(Message.work_emoji, '')
    )

    return logs_without_emoji

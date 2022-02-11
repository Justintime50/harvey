import hashlib
import hmac
from typing import Any, Dict

import woodchips

from harvey.config import Config


class Webhook:
    @staticmethod
    def validate_webhook_secret(data: Any, signature: str) -> bool:
        """Decode and validate a webhook's secret key."""
        logger = woodchips.get(Config.logger_name)

        secret_validated = False

        if signature:
            secret = bytes(Config.webhook_secret, 'utf-8')
            expected_signature = hmac.new(secret, msg=data, digestmod=hashlib.sha1)
            digest = 'sha1=' + expected_signature.hexdigest()

            if hmac.compare_digest(digest, signature):
                secret_validated = True

        logger.debug(f'{signature} webhook validated: {secret_validated}')

        return secret_validated

    @staticmethod
    def repo_full_name(webhook: Dict[str, Any]) -> str:
        """Return the repo's full name from the webhook JSON."""
        return webhook['repository']['full_name'].lower()

    @staticmethod
    def repo_commit_author(webhook: Dict[str, Any]) -> str:
        """Return the repo's commit author name from the webhook JSON."""
        return webhook['commits'][0]['author']['name']

    @staticmethod
    def repo_url(webhook: Dict[str, Any]) -> str:
        """Return the repo's URL from the webhook JSON."""
        return webhook['repository']['ssh_url']  # Use SSH URL so private repos can be cloned/pulled

    @staticmethod
    def repo_owner_name(webhook: Dict[str, Any]) -> str:
        """Return the repo owner's name from the webhook JSON."""
        return webhook['repository']['owner']['name'].lower()

    @staticmethod
    def repo_commit_id(webhook: Dict[str, Any]) -> str:
        """Return the repo's ID from the webhook JSON."""
        return str(webhook['commits'][0]['id'])

    @staticmethod
    def repo_commit_message(webhook: Dict[str, Any]) -> str:
        """Return the repo's commit message from the webhook JSON."""
        return str(webhook['commits'][0]['message'])

    @staticmethod
    def pipeline_id(webhook: Dict[str, Any]) -> str:
        """Return the pipeline ID used for the SQLite stores."""
        return f'{Webhook.repo_full_name(webhook).replace("/", "-")}@{Webhook.repo_commit_id(webhook)}'

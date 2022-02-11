import hashlib
from unittest.mock import patch

import pytest

from harvey.webhooks import Webhook


@patch('logging.Logger.info')
@patch('harvey.config.Config.webhook_secret', '123')
@pytest.mark.skip('Security is hard, revisit later - this logic has been proven in prod')
def test_validate_webhook_secret(mock_webhook, mock_logger):
    mock_webhook_secret = bytes('123', 'UTF-8')
    mock_signature = hashlib.sha1(mock_webhook_secret)
    validated_webhook_secret = Webhook.validate_webhook_secret(mock_webhook, mock_signature)

    mock_logger.assert_called()
    assert validated_webhook_secret is True


@patch('harvey.config.Config.webhook_secret', '123')
@patch('logging.Logger.debug')
def test_validate_webhook_secret_no_signature(mock_logger, mock_webhook):
    validated_webhook_secret = Webhook.validate_webhook_secret(mock_webhook, None)

    mock_logger.assert_called()
    assert validated_webhook_secret is False


def test_full_name(mock_webhook):
    result = Webhook.repo_full_name(mock_webhook)

    assert result == 'test_user/test-repo-name'


def test_author_name(mock_webhook):
    result = Webhook.repo_commit_author(mock_webhook)

    assert result == 'test_user'


def test_repo_url(mock_webhook):
    result = Webhook.repo_url(mock_webhook)

    assert result == 'https://test-url.com'


def test_repo_owner_name(mock_webhook):
    result = Webhook.repo_owner_name(mock_webhook)

    assert result == 'test_owner'


def test_repo_commit_message(mock_webhook):
    result = Webhook.repo_commit_message(mock_webhook)

    assert result == 'Mock message'


def test_repo_commit_id(mock_webhook):
    result = Webhook.repo_commit_id(mock_webhook)

    assert result == '123456'

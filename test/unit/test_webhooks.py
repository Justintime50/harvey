import json
from unittest.mock import patch

from harvey.webhooks import Webhook


@patch('harvey.config.Config.webhook_secret', '123')
@patch('logging.Logger.debug')
def test_validate_webhook_secret(mock_logger, mock_webhook):
    expected_signature = 'sha256=4af0238859f28cb06c07486335e33b337328358f60abee450e7fbe6197e58c09'
    encoded_webhook = json.dumps(mock_webhook).encode()
    validated_webhook_secret = Webhook.validate_webhook_secret(
        webhook_body=encoded_webhook,
        signature=expected_signature,
    )

    mock_logger.assert_called()
    assert validated_webhook_secret is True


@patch('harvey.config.Config.webhook_secret', 'invalid_secret')
@patch('logging.Logger.debug')
def test_validate_webhook_secret_mismatch(mock_logger, mock_webhook):
    expected_signature = 'sha256=4af0238859f28cb06c07486335e33b337328358f60abee450e7fbe6197e58c09'
    encoded_webhook = json.dumps(mock_webhook).encode()
    validated_webhook_secret = Webhook.validate_webhook_secret(
        webhook_body=encoded_webhook,
        signature=expected_signature,
    )

    mock_logger.assert_called()
    assert validated_webhook_secret is False


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

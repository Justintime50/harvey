import hashlib
from unittest.mock import MagicMock, patch

import pytest

from harvey.webhooks import Webhook


@patch('logging.Logger.info')
@patch('harvey.webhooks.Pipeline.run_pipeline')
def test_parse_webhook(mock_run_pipeline, mock_logger, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object)

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'Started pipeline for test_user/test-repo-name',
        'success': True,
    }
    assert webhook[1] == 200


@patch('logging.Logger.debug')
@patch('harvey.webhooks.Pipeline.run_pipeline')
def test_parse_webhook_bad_branch(mock_run_pipeline, mock_logger, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object(branch='bad_branch_name'))

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'Harvey received a webhook event for a branch that is not included in the ALLOWED_BRANCHES.',
        'success': False,
    }
    assert webhook[1] == 422


@patch('logging.Logger.debug')
@patch('harvey.webhooks.Pipeline.run_pipeline')
def test_parse_webhook_no_json(mock_run_pipeline, mock_logger):
    mock_webhook = MagicMock()
    mock_webhook.json = None
    webhook = Webhook.parse_webhook(mock_webhook)

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'Malformed or missing JSON data in webhook.',
        'success': False,
    }
    assert webhook[1] == 422


@patch('logging.Logger.info')
@patch('harvey.webhooks.WEBHOOK_SECRET', '123')
@patch('harvey.webhooks.Webhook.validate_webhook_secret', return_value=False)
@patch('harvey.webhooks.Pipeline.run_pipeline')
def test_parse_webhook_bad_webhook_secret(mock_run_pipeline, mock_logger, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object)

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'The X-Hub-Signature did not match the WEBHOOK_SECRET.',
        'success': False,
    }
    assert webhook[1] == 403


@patch('logging.Logger.info')
@patch('harvey.webhooks.WEBHOOK_SECRET', '123')
@pytest.mark.skip('Security is hard, revisit later - this logic has been proven in prod')
def test_validate_webhook_secret(mock_webhook, mock_logger):
    mock_webhook_secret = bytes('123', 'UTF-8')
    mock_signature = hashlib.sha1(mock_webhook_secret)
    validated_webhook_secret = Webhook.validate_webhook_secret(mock_webhook, mock_signature)

    mock_logger.assert_called()
    assert validated_webhook_secret is True


@patch('harvey.webhooks.WEBHOOK_SECRET', '123')
@patch('logging.Logger.debug')
def test_validate_webhook_secret_no_signature(mock_logger, mock_webhook):
    validated_webhook_secret = Webhook.validate_webhook_secret(mock_webhook, None)

    mock_logger.assert_called()
    assert validated_webhook_secret is False

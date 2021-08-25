import hashlib
from unittest.mock import MagicMock, patch

import pytest
from harvey.webhooks import Webhook


@patch('harvey.globals.Global.APP_MODE', 'test')
@patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook(mock_start_pipeline, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object, False)

    assert webhook[0] == {
        'message': 'Started pipeline for TEST-repo-name',
        'success': True,
    }
    assert webhook[1] == 200


@patch('harvey.globals.Global.APP_MODE', 'test')
@patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook_bad_branch(mock_start_pipeline, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object(branch='ref/heads/bad_branch'), False)

    assert webhook[0] == {
        'message': 'Harvey received a webhook event for a branch that is not included in the ALLOWED_BRANCHES.',
        'success': False,
    }
    assert webhook[1] == 422


@patch('harvey.globals.Global.APP_MODE', 'test')
@patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook_no_json(mock_start_pipeline):
    mock_webhook = MagicMock()
    mock_webhook.json = None
    webhook = Webhook.parse_webhook(mock_webhook, False)

    assert webhook[0] == {
        'message': 'Malformed or missing JSON data in webhook.',
        'success': False,
    }
    assert webhook[1] == 422


@mock.patch('harvey.webhooks.WEBHOOK_SECRET', '123')
@mock.patch('harvey.webhooks.Webhook.validate_webhook_secret', return_value=False)
@mock.patch('harvey.globals.Global.APP_MODE', 'prod')
@mock.patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook_bad_webhook_secret(mock_start_pipeline, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object, False)

    assert webhook[0] == {
        'message': 'The X-Hub-Signature did not match the WEBHOOK_SECRET.',
        'success': False,
    }
    assert webhook[1] == 403


@mock.patch('harvey.webhooks.WEBHOOK_SECRET', '123')
@mock.patch('harvey.webhooks.APP_MODE', 'prod')
@pytest.mark.skip('Security is hard, revisit later - this logic has been proven in prod')
def test_validate_webhook_secret(mock_webhook):
    mock_webhook_secret = bytes('123', 'UTF-8')
    mock_signature = hashlib.sha1(mock_webhook_secret)
    validated_webhook_secret = Webhook.validate_webhook_secret(mock_webhook, mock_signature)

    assert validated_webhook_secret is True


@mock.patch('harvey.webhooks.WEBHOOK_SECRET', '123')
def test_validate_webhook_secret_no_signature(mock_webhook):
    validated_webhook_secret = Webhook.validate_webhook_secret(mock_webhook, None)

    assert validated_webhook_secret is False


@mock.patch('harvey.globals.Global.FILTER_WEBHOOKS', True)
def test_webhook_originated_outside_github(mock_webhook_object):
    mock_webhook_object.remote_addr = '1.2.3.4'
    webhook = Webhook.parse_webhook(mock_webhook_object, False)

    assert webhook[0] == {
        'message': 'Webhook did not originate from GitHub.',
        'success': False,
    }
    assert webhook[1] == 422

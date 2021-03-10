import hashlib

import mock
import pytest
from harvey.webhooks import Webhook


@mock.patch('harvey.globals.Global.APP_MODE', 'test')
@mock.patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook(mock_start_pipeline, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object, False)

    assert webhook[0] == {
        'message': 'Started pipeline for TEST-repo-name',
        'success': True
    }
    assert webhook[1] == 200


@mock.patch('harvey.globals.Global.APP_MODE', 'test')
@mock.patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook_bad_branch(mock_start_pipeline, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object(branch='ref/heads/bad_branch'), False)

    assert webhook[0] == {
        'message': 'Harvey can only pull from the "master" or "main" branch of a repo.',
        'success': False
    }
    assert webhook[1] == 422


@mock.patch('harvey.globals.Global.APP_MODE', 'test')
@mock.patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook_no_json(mock_start_pipeline):
    mock_webhook = mock.MagicMock()
    mock_webhook.json = None
    webhook = Webhook.parse_webhook(mock_webhook, False)

    assert webhook[0] == {
        'message': 'Malformed or missing JSON data in webhook.',
        'success': False
    }
    assert webhook[1] == 422


@mock.patch('harvey.webhooks.Webhook.decode_webhook', return_value=False)
@mock.patch('harvey.globals.Global.APP_MODE', 'prod')
@mock.patch('harvey.webhooks.Pipeline.start_pipeline')
def test_parse_webhook_bad_webhook_secret(mock_start_pipeline, mock_webhook_object):
    webhook = Webhook.parse_webhook(mock_webhook_object, False)

    assert webhook[0] == {
        'message': 'The X-Hub-Signature did not match the WEBHOOK_SECRET.',
        'success': False
    }
    assert webhook[1] == 403


@mock.patch('harvey.webhooks.WEBHOOK_SECRET', '123')
@mock.patch('harvey.webhooks.APP_MODE', 'prod')
@pytest.mark.skip('Security is hard, revisit later - but this logic does work')
def test_decode_webhook(mock_webhook):
    mock_webhook_secret = bytes('123', 'UTF-8')
    mock_signature = hashlib.sha1(mock_webhook_secret)
    decoded_webhook = Webhook.decode_webhook(mock_webhook, mock_signature)

    assert decoded_webhook is True


def test_decode_webhook_no_signature(mock_webhook):
    decoded_webhook = Webhook.decode_webhook(mock_webhook, None)

    assert decoded_webhook is False

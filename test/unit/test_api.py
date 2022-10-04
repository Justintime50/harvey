from unittest.mock import (
    MagicMock,
    patch,
)

from harvey.api import Api


@patch('logging.Logger.info')
@patch('harvey.deployments.Deployment.run_deployment')
def test_parse_github_webhook(mock_run_deployment, mock_logger, mock_webhook_object):
    webhook = Api.parse_github_webhook(mock_webhook_object)

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'Started deployment for test_user/test-repo-name',
        'success': True,
    }
    assert webhook[1] == 200


@patch('logging.Logger.debug')
@patch('harvey.deployments.Deployment.run_deployment')
def test_parse_github_webhook_bad_branch(mock_run_deployment, mock_logger, mock_webhook_object):
    webhook = Api.parse_github_webhook(mock_webhook_object(branch='bad_branch_name'))

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'Harvey received a webhook event for a branch that is not included in the ALLOWED_BRANCHES.',
        'success': False,
    }
    assert webhook[1] == 422


@patch('logging.Logger.debug')
@patch('harvey.deployments.Deployment.run_deployment')
def test_parse_github_webhook_no_json(mock_run_deployment, mock_logger):
    mock_webhook = MagicMock()
    mock_webhook.json = None
    webhook = Api.parse_github_webhook(mock_webhook)

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'Malformed or missing JSON data in webhook.',
        'success': False,
    }
    assert webhook[1] == 422


@patch('logging.Logger.info')
@patch('harvey.config.Config.webhook_secret', '123')
@patch('harvey.webhooks.Webhook.validate_webhook_secret', return_value=False)
@patch('harvey.deployments.Deployment.run_deployment')
def test_parse_github_webhook_bad_webhook_secret(mock_run_deployment, mock_logger, mock_webhook_object):
    webhook = Api.parse_github_webhook(mock_webhook_object)

    mock_logger.assert_called()
    assert webhook[0] == {
        'message': 'The X-Hub-Signature did not match the WEBHOOK_SECRET.',
        'success': False,
    }
    assert webhook[1] == 403

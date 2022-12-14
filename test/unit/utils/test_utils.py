from unittest.mock import patch

from harvey.utils.utils import (
    Utils,
    setup_logger,
)


@patch('sys.exit')
@patch('harvey.utils.utils.lookup_project_lock')
@patch('harvey.utils.utils.store_deployment_details')
@patch('logging.Logger.info')
def test_kill(mock_logger, mock_store_deployment_details, mock_lookup_lock, mock_exit, mock_output, mock_webhook):
    Utils.kill_deployment(mock_output, mock_webhook)

    mock_store_deployment_details.assert_called_once()
    mock_lookup_lock.assert_called_once()
    mock_exit.assert_called_once()


@patch('sys.exit')
@patch('harvey.utils.utils.lookup_project_lock')
@patch('harvey.config.Config.use_slack', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.utils.store_deployment_details')
@patch('logging.Logger.error')
def test_kill_with_slack(
    mock_logger, mock_store_deployment_details, mock_slack, mock_lookup_lock, mock_exit, mock_output, mock_webhook
):
    Utils.kill_deployment(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_store_deployment_details.assert_called_once()
    mock_slack.assert_called_once()
    mock_lookup_lock.assert_called_once()
    mock_exit.assert_called_once()


@patch('sys.exit')
@patch('harvey.utils.utils.store_deployment_details')
@patch('logging.Logger.info')
def test_success(mock_logger, mock_store_deployment_details, mock_exit, mock_output, mock_webhook):
    Utils.succeed_deployment(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_store_deployment_details.assert_called_once()
    mock_exit.assert_called_once()


@patch('sys.exit')
@patch('harvey.config.Config.use_slack', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.utils.store_deployment_details')
@patch('logging.Logger.info')
def test_success_with_slack(
    mock_logger, mock_store_deployment_details, mock_slack, mock_exit, mock_output, mock_webhook
):
    Utils.succeed_deployment(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_store_deployment_details.assert_called_once()
    mock_slack.assert_called_once()
    mock_exit.assert_called_once()


@patch('woodchips.Logger')
def test_setup_logger(mock_logger):
    """Tests that we setup a `woodchips` logger correctly."""
    setup_logger()

    mock_logger.assert_called_once()

import tempfile
from unittest.mock import mock_open, patch

from harvey.utils import Utils, setup_logger


@patch('harvey.utils.Utils.store_pipeline_details')
@patch('sys.exit')
@patch('logging.Logger.info')
def test_kill(mock_logger, mock_sys_exit, mock_generate_logs, mock_output, mock_webhook):
    Utils.kill(mock_output, mock_webhook)

    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()


@patch('harvey.globals.Global.SLACK', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.Utils.store_pipeline_details')
@patch('sys.exit')
@patch('logging.Logger.warning')
def test_kill_with_slack(mock_logger, mock_sys_exit, mock_generate_logs, mock_slack, mock_output, mock_webhook):
    Utils.kill(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()
    mock_slack.assert_called_once()


@patch('harvey.utils.Utils.store_pipeline_details')
@patch('sys.exit')
@patch('logging.Logger.info')
def test_success(mock_logger, mock_sys_exit, mock_generate_logs, mock_output, mock_webhook):
    Utils.success(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()


@patch('harvey.globals.Global.SLACK', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.Utils.store_pipeline_details')
@patch('sys.exit')
@patch('logging.Logger.info')
def test_success_with_slack(mock_logger, mock_sys_exit, mock_generate_logs, mock_slack, mock_output, mock_webhook):
    Utils.success(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()
    mock_slack.assert_called_once()


@patch('logging.Logger.debug')
def test_store_pipeline_details(mock_logger, mock_output, mock_webhook):
    with patch('builtins.open', mock_open()):
        Utils.store_pipeline_details(mock_webhook, mock_output)

        mock_logger.assert_called()


@patch('woodchips.Logger')
def test_setup_logger(mock_logger):
    """Tests that we setup a `woodchips` logger correctly."""
    setup_logger()

    mock_logger.assert_called_once()

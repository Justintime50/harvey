import os
from unittest.mock import mock_open, patch

from harvey.utils import Utils


@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('harvey.globals.Global.LOGGER')
def test_kill(mock_logger, mock_sys_exit, mock_generate_logs, mock_output, mock_webhook):
    Utils.kill(mock_output, mock_webhook)

    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()


@patch('harvey.globals.Global.SLACK', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('harvey.globals.Global.LOGGER')
def test_kill_with_slack(mock_logger, mock_sys_exit, mock_generate_logs, mock_slack, mock_output, mock_webhook):
    Utils.kill(mock_output, mock_webhook)

    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()
    mock_slack.assert_called_once()


@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('harvey.globals.Global.LOGGER')
def test_success(mock_logger, mock_sys_exit, mock_generate_logs, mock_output, mock_webhook):
    Utils.success(mock_output, mock_webhook)

    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()


@patch('harvey.globals.Global.SLACK', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('harvey.globals.Global.LOGGER')
def test_success_with_slack(mock_logger, mock_sys_exit, mock_generate_logs, mock_slack, mock_output, mock_webhook):
    Utils.success(mock_output, mock_webhook)

    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()
    mock_slack.assert_called_once()


@patch('harvey.globals.Global.PROJECTS_LOG_PATH', os.path.join('test', 'logs'))
@patch('harvey.globals.Global.LOGGER')
def test_generate_pipeline_logs(mock_logger, mock_output, mock_webhook):
    # TODO: Mock this better so we don't need a gitignored directory to run tests
    with patch('builtins.open', mock_open()):
        Utils.generate_pipeline_logs(mock_output, mock_webhook)


@patch('harvey.globals.Global.PROJECTS_LOG_PATH', 'mock_dir')
@patch('os.makedirs')
@patch('harvey.globals.Global.LOGGER')
def test_generate_pipeline_logs_dir_exists(mock_logger, mock_makedirs, mock_output, mock_webhook):
    with patch('builtins.open', mock_open()):
        Utils.generate_pipeline_logs(mock_output, mock_webhook)


@patch('harvey.utils.Utils.kill')
@patch('harvey.globals.Global.LOGGER')
def test_generate_pipeline_logs_exception(mock_logger, mock_output, mock_webhook):
    with patch('builtins.open', mock_open()) as mock_open_file:
        mock_open_file.side_effect = OSError
        Utils.generate_pipeline_logs(mock_output, mock_webhook)

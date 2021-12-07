import tempfile
from unittest.mock import mock_open, patch

from harvey.utils import Utils


@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('logging.Logger.info')
def test_kill(mock_logger, mock_sys_exit, mock_generate_logs, mock_output, mock_webhook):
    Utils.kill(mock_output, mock_webhook)

    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()


@patch('harvey.globals.Global.SLACK', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('logging.Logger.warning')
def test_kill_with_slack(mock_logger, mock_sys_exit, mock_generate_logs, mock_slack, mock_output, mock_webhook):
    Utils.kill(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()
    mock_slack.assert_called_once()


@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('logging.Logger.info')
def test_success(mock_logger, mock_sys_exit, mock_generate_logs, mock_output, mock_webhook):
    Utils.success(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()


@patch('harvey.globals.Global.SLACK', True)
@patch('harvey.messages.Message.send_slack_message')
@patch('harvey.utils.Utils.generate_pipeline_logs')
@patch('sys.exit')
@patch('logging.Logger.info')
def test_success_with_slack(mock_logger, mock_sys_exit, mock_generate_logs, mock_slack, mock_output, mock_webhook):
    Utils.success(mock_output, mock_webhook)

    mock_logger.assert_called()
    mock_generate_logs.assert_called_once()
    mock_sys_exit.assert_called_once()
    mock_slack.assert_called_once()


@patch('os.makedirs')
@patch('logging.Logger.debug')
def test_generate_pipeline_logs(mock_logger, mock_makedirs, mock_output, mock_webhook):
    with patch('builtins.open', mock_open()):
        Utils.generate_pipeline_logs(mock_output, mock_webhook)

        mock_logger.assert_called()
        mock_makedirs.assert_called_once()


@patch('harvey.globals.Global.repo_full_name', return_value='')
@patch('os.makedirs')
@patch('logging.Logger.debug')
def test_generate_pipeline_logs_dir_exists(mock_logger, mock_makedirs, mock_output, mock_webhook):
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('harvey.globals.Global.PROJECTS_LOG_PATH', temp_dir):
            with patch('builtins.open', mock_open()):
                Utils.generate_pipeline_logs(mock_output, mock_webhook)

                mock_logger.assert_called()
                mock_makedirs.assert_not_called()


@patch('harvey.utils.Utils.kill')
@patch('logging.Logger.error')
def test_generate_pipeline_logs_exception(mock_logger, mock_output, mock_webhook):
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('harvey.globals.Global.PROJECTS_LOG_PATH', temp_dir):
            with patch('builtins.open', mock_open()) as mock_open_file:
                mock_open_file.side_effect = OSError
                Utils.generate_pipeline_logs(mock_output, mock_webhook)

                mock_logger.assert_called()

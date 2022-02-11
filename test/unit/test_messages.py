from unittest.mock import patch

import slack

from harvey.messages import Message


@patch('harvey.config.Config.slack_channel', 'mock-channel')
@patch('harvey.config.Config.slack_bot_token', '123')
@patch('logging.Logger.debug')
@patch('slack.WebClient.chat_postMessage')
def test_send_slack_message_success(mock_slack, mock_logger):
    message = 'mock message'
    Message.send_slack_message(message)

    mock_logger.assert_called()
    mock_slack.assert_called_once_with(channel='mock-channel', text=message)


@patch('logging.Logger.error')
@patch('sys.exit')
@patch(
    'slack.WebClient.chat_postMessage',
    side_effect=slack.errors.SlackApiError(
        message='The request to the Slack API failed.',
        response={
            'ok': False,
            'error': 'not_authed',
        },
    ),
)
def test_send_slack_message_exception(mock_slack, mock_sys_exit, mock_logger):
    message = 'mock message'
    Message.send_slack_message(message)

    mock_logger.assert_called()
    mock_sys_exit.assert_called_once()

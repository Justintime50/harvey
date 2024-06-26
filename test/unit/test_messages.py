from unittest.mock import patch

import slack_sdk

from harvey.messages import Message


@patch('harvey.config.Config.slack_channel', 'mock-channel')
@patch('harvey.config.Config.slack_bot_token', '123')
@patch('logging.Logger.debug')
@patch('slack_sdk.WebClient.chat_postMessage')
def test_send_slack_message_success(mock_slack, mock_logger):
    message = 'mock message'
    Message.send_slack_message(message)

    mock_logger.assert_called_once()
    mock_slack.assert_called_once_with(channel='mock-channel', text=message)


@patch('logging.Logger.error')
@patch('sentry_sdk.Scope.capture_message')
@patch(
    'slack_sdk.WebClient.chat_postMessage',
    side_effect=slack_sdk.errors.SlackApiError(
        message='The request to the Slack API failed.',
        response={
            'ok': False,
            'error': 'not_authed',
        },
    ),
)
def test_send_slack_message_exception(mock_slack, mock_sentry, mock_logger):
    message = 'mock message'
    expected_error_message = "Harvey could not send the Slack message: The request to the Slack API failed.\nThe server responded with: {'ok': False, 'error': 'not_authed'}"  # noqa

    Message.send_slack_message(message)

    mock_logger.assert_called_once_with(expected_error_message)
    mock_sentry.assert_called_once_with(expected_error_message, None, scope=None)

import mock
import pytest
import slack
from harvey.message import Message


@mock.patch('harvey.message.SLACK_CHANNEL', 'mock-channel')
@mock.patch('harvey.message.SLACK_BOT_TOKEN', '123')
@mock.patch('slack.WebClient.chat_postMessage')
def test_send_slack_message_success(mock_slack):
    message = 'mock message'
    Message.send_slack_message(message)
    mock_slack.assert_called_once_with(channel='mock-channel', text=message)


@mock.patch('sys.exit')
@mock.patch('slack.WebClient.chat_postMessage',
            side_effect=slack.errors.SlackApiError(
                message='The request to the Slack API failed.',
                response={'ok': False, 'error': 'not_authed'}
            ))
def test_send_slack_message_exception(mock_slack, mock_sys_exit):
    message = 'mock message'
    Message.send_slack_message(message)
    mock_sys_exit.assert_called_once_with('Harvey could not send the Slack message.')


def test_send_email():
    message = 'mock message'
    with pytest.raises(NotImplementedError):
        Message.send_email(message)

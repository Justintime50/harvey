import os
import sys

import slack

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')


class Message():
    @classmethod
    def send_slack_message(cls, message):
        """Send a Slack message via a Slackbot
        """
        slack_client = slack.WebClient(SLACK_BOT_TOKEN)
        try:
            slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=message
            )
            print('Slack message sent!')
        except slack.errors.SlackApiError:
            final_output = 'Harvey could not send the Slack message.'
            print(final_output)
            sys.exit(final_output)

    @classmethod
    def send_email(cls, message):
        """Send an email message
        """
        # TODO: Add email functionality
        raise NotImplementedError()

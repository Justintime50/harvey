import os
import sys

import slack

from harvey.globals import Global

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')


class Message:
    @staticmethod
    def send_slack_message(message):
        """Send a Slack message via a Slackbot."""
        slack_client = slack.WebClient(SLACK_BOT_TOKEN)

        try:
            slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=message,
            )
            Global.LOGGER.debug('Slack message sent!')
        except slack.errors.SlackApiError:
            final_output = 'Harvey could not send the Slack message.'
            Global.LOGGER.error(final_output)
            sys.exit()

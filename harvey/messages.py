import os
import sys

import slack
import woodchips

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', 'general')
LOGGER_NAME = 'harvey'  # Redefined here to avoid circular import


class Message:
    @staticmethod
    def send_slack_message(message: str):
        """Send a Slack message via a Slackbot."""
        logger = woodchips.get(LOGGER_NAME)

        slack_client = slack.WebClient(SLACK_BOT_TOKEN)

        try:
            slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=message,
            )
            logger.debug('Slack message sent!')
        except slack.errors.SlackApiError:
            final_output = 'Harvey could not send the Slack message.'
            logger.error(final_output)
            sys.exit()

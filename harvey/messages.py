import sys

import slack
import woodchips

from harvey.config import Config


class Message:
    @staticmethod
    def send_slack_message(message: str):
        """Send a Slack message via a Slackbot."""
        logger = woodchips.get(Config.logger_name)

        slack_client = slack.WebClient(Config.slack_bot_token)

        try:
            slack_client.chat_postMessage(
                channel=Config.slack_channel,
                text=message,
            )
            logger.debug('Slack message sent!')
        except slack.errors.SlackApiError:
            final_output = 'Harvey could not send the Slack message.'
            logger.error(final_output)
            sys.exit()

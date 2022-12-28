import slack
import woodchips

from harvey.config import Config
from harvey.errors import HarveyError


class Message:
    @property
    def work_emoji(self):
        return ':hammer_and_wrench:' if Config.use_slack else ''

    @property
    def success_emoji(self):
        return ':white_check_mark:' if Config.use_slack else 'Success!'

    @property
    def failure_emoji(self):
        return ':skull_and_crossbones:' if Config.use_slack else 'Failure!'

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
            error_message = 'Harvey could not send the Slack message.'
            logger.error(error_message)
            raise HarveyError(error_message)

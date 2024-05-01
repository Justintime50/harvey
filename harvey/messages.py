import slack_sdk
import woodchips
from sentry_sdk import capture_message

from harvey.config import Config


class Message:
    work_emoji = ':hammer_and_wrench:' if Config.use_slack else ''
    success_emoji = ':white_check_mark:' if Config.use_slack else 'Success!'
    failure_emoji = ':skull_and_crossbones:' if Config.use_slack else 'Failure!'

    @staticmethod
    def send_slack_message(message: str):
        """Send a Slack message via a Slackbot."""
        logger = woodchips.get(Config.logger_name)

        slack_client = slack_sdk.WebClient(Config.slack_bot_token)

        try:
            slack_client.chat_postMessage(
                channel=Config.slack_channel,
                text=message,
            )
            logger.debug('Slack message sent!')
        except slack_sdk.errors.SlackApiError as error:
            error_message = f'Harvey could not send the Slack message: {str(error)}'
            logger.error(error_message)
            capture_message(error_message)

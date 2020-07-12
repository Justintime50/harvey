"""Message logic once a pipeline has exited"""
# pylint: disable=W0511,R0903,E1101
import os
import sys
import slack


class Message():
    """Send message methods"""
    @classmethod
    def slack(cls, message):
        """Send Slack messages via a bot"""
        slack_client = slack.WebClient(os.getenv('SLACK_BOT_TOKEN'))
        try:
            slack_client.chat_postMessage(
                channel=os.getenv('SLACK_CHANNEL'),
                text=message
            )
            print('Slack message sent!')
        except slack.errors.SlackApiError:
            final_output = 'Error: Harvey could not send the Slack message.'
            print(final_output)
            sys.exit(final_output)
            # TODO: Add Harvey logging here

# TODO: Add email functionality

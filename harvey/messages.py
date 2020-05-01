"""Message logic once a pipeline has exited"""
# pylint: disable=W0511,R0903
import os
import sys
import slack

class Message():
    """Send message methods"""
    @classmethod
    def slack(cls, message):
        """Send Slack messages via a bot"""
        # Make the POST request through the python slack client
        slack_client = slack.WebClient(os.getenv("SLACK_BOT_TOKEN"))
        try:
            slack_client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL"),
                text=message
            )
            print("Slack message Sent!")
        except:
            sys.exit("Error: Harvey could not send the Slack message")

# TODO: Add email functionality

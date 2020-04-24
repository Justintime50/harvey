"""Message logic once a pipeline has exited"""
import os
import requests
from dotenv import load_dotenv
import slack

# Setup variables
load_dotenv()

class Messages():
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
            print("Error: Harvey could not send the Slack message")

# TODO: Add email functionality

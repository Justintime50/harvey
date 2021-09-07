import os
import sys

from harvey.globals import Global
from harvey.messages import Message


class Utils:
    @staticmethod
    def kill(final_output, webhook):
        """A kill util to write everything to logs, send messages,
        tear down Docker stuff, and quit.
        """
        Utils.generate_pipeline_logs(final_output, webhook)
        if Global.SLACK:
            Message.send_slack_message(final_output)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def success(final_output, webhook):
        """Log output and send message on pipeline success."""
        Utils.generate_pipeline_logs(final_output, webhook)
        if Global.SLACK:
            Message.send_slack_message(final_output)

        # Close the thread safely
        sys.exit()

    @staticmethod
    def generate_pipeline_logs(final_output, webhook):
        """Generate a complete log file with the entire pipeline's output"""
        pipeline_log_path = os.path.join(Global.PROJECTS_LOG_PATH, Global.repo_full_name(webhook))
        if not os.path.exists(pipeline_log_path):
            os.makedirs(pipeline_log_path)

        try:
            filename = os.path.join(pipeline_log_path, Global.repo_commit_id(webhook) + '.log')
            with open(filename, 'w') as log:
                log.write(final_output)
        except OSError as os_error:
            final_output = 'Error: Harvey could not save the log file.'
            print(os_error)
            Utils.kill(final_output, webhook)

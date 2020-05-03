"""Import Utils modules"""
# pylint: disable=W0511
import os
import sys
import shutil
from .globals import Global
from .messages import Message

class Utils():
    """Harvey Utilities used throughout the program"""
    @classmethod
    def project_logs(cls, final_output, webhook):
        """Generate log file with all output"""
        if not os.path.exists(os.path.join(Global.PROJECTS_LOG_PATH, \
            Global.repo_full_name(webhook))):
            os.makedirs(os.path.join(Global.PROJECTS_LOG_PATH, Global.repo_full_name(webhook)))
        try:
            filename = os.path.join(Global.PROJECTS_LOG_PATH, Global.repo_full_name(webhook), \
                Global.repo_commit_id(webhook)+'.log')
            with open(filename, 'w') as log:
                log.write(final_output)
        except OSError as os_error:
            final_output = 'Error: Harvey could not save the log file.'
            print(os_error)
            Utils.kill(final_output, webhook)

    @classmethod
    def kill(cls, final_output, webhook):
        """
        A kill util to write everything to logs, send messages,
        tear down Docker stuff, and quit
        """
        Utils.project_logs(final_output, webhook)
        Message.slack(final_output)
        if os.path.exists(os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))):
            shutil.rmtree(os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook)))
        sys.exit()

    @classmethod
    def success(cls, final_output, webhook):
        """Log output and send message on pipeline success"""
        Utils.project_logs(final_output, webhook)
        Message.slack(final_output)
        if os.path.exists(os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))):
            shutil.rmtree(os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook)))

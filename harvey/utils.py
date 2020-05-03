"""Import Utils modules"""
# pylint: disable=W0511
import os
import sys
from datetime import datetime
from .globals import Global
from .messages import Message

class Utils():
    """Harvey Utilities used throughout the program"""
    @classmethod
    def project_logs(cls, final_output):
        """Generate log file with all output"""
        if not os.path.exists(Global.PROJECTS_LOG_PATH):
            os.makedirs(Global.PROJECTS_LOG_PATH)
        try:
            filename = os.path.join(Global.PROJECTS_LOG_PATH, f'{datetime.today()}.txt')
            with open(filename, 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(final_output)
        except OSError as os_error:
             # TODO: Add the repo/project name here
            final_output = 'Error: Harvey could not save the log file.'
            print(os_error)
            Utils.kill(final_output)

    @classmethod
    def kill(cls, final_output):
        """
        A kill util to write everything to logs, send messages,
        tear down Docker stuff, and quit
        """
        Utils.project_logs(final_output)
        Message.slack(final_output)
        # TODO: Uncomment when you consolidate the full_name variable
        # if os.path.exists(os.path.join(Global.PROJECTS_PATH, full_name)):
        #     shutil.rmtree(os.path.join(Global.PROJECTS_PATH, full_name))
        sys.exit()

    @classmethod
    def success(cls, final_output):
        """Log output and send message on pipeline success"""
        Utils.project_logs(final_output)
        Message.slack(final_output)
        # TODO: Uncomment when you consolidate the full_name variable
        # if os.path.exists(os.path.join(Global.PROJECTS_PATH, full_name)):
        #     shutil.rmtree(os.path.join(Global.PROJECTS_PATH, full_name))

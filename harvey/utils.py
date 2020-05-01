import os
import sys
from datetime import datetime
from .globals import Global
from .container import Container
from .image import Image
from .messages import Message

class Utils(Global):
    """Harvey Utilities used throughout the program"""
    @classmethod
    def logs(cls, final_output):
        """Generate log file with all output"""
        if not os.path.exists(Global.LOGS_PATH):
            os.makedirs(Global.LOGS_PATH)
        # TODO: This does not catch if the logs cannot be saved
        filename = os.path.join(Global.LOGS_PATH, f'{datetime.today()}.txt')
        with open(filename, 'w+') as log:
            # TODO: We may want to save project name in filename as well
            log.write(final_output)

    @classmethod
    def kill(cls, final_output, image='', container=''):
        """
        A kill util to write everything to logs, send messages,
        tear down Docker stuff, and quit
        """
        Utils.logs(final_output)
        Message.slack(final_output)
        # Container.remove(container['Id']) # TODO: How do we want to handle this?
        Image.remove(image)
        # TODO: Uncomment when you consolidate the full_name variable
        # if os.path.exists(os.path.join(Global.PROJECTS_PATH, full_name)):
        #     shutil.rmtree(os.path.join(Global.PROJECTS_PATH, full_name))
        sys.exit()

    @classmethod
    def success(cls, final_output):
        """Log output and send message on pipeline success"""
        Utils.logs(final_output)
        Message.slack(final_output)
        # TODO: Uncomment when you consolidate the full_name variable
        # if os.path.exists(os.path.join(Global.PROJECTS_PATH, full_name)):
        #     shutil.rmtree(os.path.join(Global.PROJECTS_PATH, full_name))

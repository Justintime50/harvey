import os
import sys
from datetime import datetime
from .globals import Global

class Utils(Global):
    """Harvey Utilities used throughout the program"""
    @classmethod
    def logs(cls, final_output):
        """Generate log file with all output"""
        try:
            if not os.path.exists(f'{Global.LOGS_PATH}'):
                os.makedirs(f'{Global.LOGS_PATH}')
            with open(f'{Global.LOGS_PATH}/{datetime.today()}.txt', 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(final_output)
        except:
            sys.exit("Error: Harvey could not save log file")

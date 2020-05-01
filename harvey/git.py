"""Import git modules"""
# pylint: disable=R0903
import os
import shutil
import subprocess
from .globals import Global
from .utils import Utils

class Git():
    """Git methods"""
    @classmethod
    def pull(cls, webhook):
        """Pull/clone changes from git"""
        full_name = webhook["repository"]["full_name"].lower()
        url = webhook["repository"]["url"]

        if os.path.exists(os.path.join(Global.PROJECTS_PATH, full_name)):
            shutil.rmtree(os.path.join(Global.PROJECTS_PATH, full_name))
        try:
            final_output = subprocess.call(f'git clone --depth=50 --branch=master {url} {os.path.join(Global.PROJECTS_PATH, full_name)}', stdin=None, stdout=None, stderr=None, shell=True)
            print(final_output)
        except:
            final_output = '\nError: Harvey could not clone the project'
            Utils.kill(final_output)

        return final_output

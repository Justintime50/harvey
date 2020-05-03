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
        """Clone project using git"""
        if os.path.exists(os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))):
            shutil.rmtree(os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook)))
        try:
            final_output = subprocess.check_call(f'git clone --depth=50 --branch=master \
                {Global.repo_url(webhook)} \
                {os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))}', \
                stdin=None, stdout=None, stderr=None, shell=True)
            print(final_output)
        except subprocess.CalledProcessError:
            final_output = f'\nError: Harvey could not clone {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

        return final_output

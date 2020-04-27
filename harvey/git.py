"""Import git modules"""
# pylint: disable=R0903
import os
import sys
from .globals import Global

class Git(Global):
    """Git methods"""
    @classmethod
    def pull(cls, webhook):
        """Pull/clone changes from git"""
        full_name = webhook["repository"]["full_name"].lower()
        owner_name = webhook["repository"]["owner"]["name"].lower()
        url = webhook["repository"]["url"]
        if not os.path.exists(f'{Global.PROJECTS_PATH}'):
            os.makedirs(f'{Global.PROJECTS_PATH}', exist_ok=True)
        if not os.path.exists(f'{Global.PROJECTS_PATH}{full_name}'):
            try:
                command = os.system(f'cd {Global.PROJECTS_PATH} && mkdir {owner_name} \
                    && cd {owner_name} && git clone {url}')
            except:
                sys.exit("Error: Harvey could not clone project")
        else:
            try:
                command = os.system(f'cd {Global.PROJECTS_PATH}{full_name} && git pull')
            except:
                sys.exit("Error: Harvey could not pull project")

        return command

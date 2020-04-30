"""Import git modules"""
# pylint: disable=R0903
import os
import sys
from .globals import Global
from .utils import Utils
from .messages import Message

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
        if not os.path.exists(f'{Global.PROJECTS_PATH}/{full_name}'):
            try:
                final_output = f'\nProject does not exist, cloning {full_name}\n'
                print(final_output)
                os.system(f'cd {Global.PROJECTS_PATH} && mkdir {owner_name} \
                    && cd {owner_name} && git clone {url}')
            except:
                final_output = 'Error: Harvey could not clone project'
                Utils.logs(final_output)
                Message.slack(final_output)
                sys.exit()
        else:
            try:
                final_output = f'\nFetching and pulling changes from {full_name}\n'
                print(final_output)
                os.system(f'cd {Global.PROJECTS_PATH}/{full_name} && git fetch && git pull')
            except:
                final_output = 'Error: Harvey could not pull project'
                Utils.logs(final_output)
                Message.slack(final_output)
                sys.exit()

        return final_output

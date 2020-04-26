"""Import git modules"""
# pylint: disable=R0903
import os
import sys

class Git():
    """Git methods"""
    @classmethod
    def pull(cls, webhook):
        """Pull/clone changes from git"""
        full_name = webhook["repository"]["full_name"].lower()
        owner_name = webhook["repository"]["owner"]["name"].lower()
        url = webhook["repository"]["url"]
        if not os.path.exists(f'docker/projects/{full_name}'):
            try:
                command = os.system(f'cd docker/projects && mkdir {owner_name} \
                    && cd {owner_name} && git clone {url}')
            except:
                sys.exit("Error: Harvey could not clone project")
        else:
            try:
                command = os.system(f'cd docker/projects/{full_name} && git pull')
            except:
                sys.exit("Error: Harvey could not pull project")

        return command

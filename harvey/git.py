import os
import sys

class Git():
    @classmethod
    def pull(cls, webhook):
        # Pull in changes from git
        if not os.path.exists(f'docker/projects/{webhook["repository"]["full_name"].lower()}'):
            try:
                command = os.system(f'cd docker/projects && mkdir {webhook["repository"]["owner"]["name"].lower()} && cd {webhook["repository"]["owner"]["name"].lower()} && git clone {webhook["repository"]["url"]}')
            except:
                sys.exit("Error: Harvey could not clone project")
        else:
            try:
                command = os.system(f'cd docker/projects/{webhook["repository"]["full_name"].lower()} && git pull')
            except:
                sys.exit("Error: Harvey could not pull project")

        return command

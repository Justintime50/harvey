import os

class Git():
    @classmethod
    def pull(cls, webhook):
        # Pull in changes from git
        # TODO: Add logic to catch if we cannot connect to GitHub/internet
        if not os.path.exists(f'docker/projects/{webhook["repository"]["full_name"].lower()}'):
            command = os.system(f'cd docker/projects && mkdir {webhook["repository"]["owner"]["name"].lower()} && cd {webhook["repository"]["owner"]["name"].lower()} && git clone {webhook["repository"]["url"]}')
        else:
            command = os.system(f'cd docker/projects/{webhook["repository"]["full_name"].lower()} && git pull')

        return command

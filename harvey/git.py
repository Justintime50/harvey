import os

class Git():
    @classmethod
    def pull(cls, data):
        # Pull in changes from git
        # TODO: Add logic to catch if we cannot connect to GitHub/internet
        if not os.path.exists(f'docker/projects/{data["repository"]["name"]}'):
            command = os.system(f'cd docker/projects && git clone {data["repository"]["url"]}')
        else:
            command = os.system(f'cd docker/projects/{data["repository"]["name"]} && git pull')

        return command

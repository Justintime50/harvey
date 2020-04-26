"""Import modules for containers"""
#pylint: disable=W0511
import json
import sys
import os
from datetime import datetime
import requests
import requests_unixsocket
from .client import Client

requests_unixsocket.monkeypatch() # allows us to use requests_unixsocker via requests

class Container(Client):
    """Docker container methods"""
    @classmethod
    def create(cls, tag):
        """Create a Docker container"""
        data = requests.post(Client.BASE_URL + f'containers/create?name={tag}', \
            data=json.dumps({'Image': tag}), headers=Client.JSON_HEADERS)
        return data.json()

    @classmethod
    def start(cls, container_id):
        """Start a Docker container"""
        data = requests.post(Client.BASE_URL + f'containers/{container_id}/start')
        return data

    @classmethod
    def stop(cls, container_id):
        """Stop a Docker container"""
        data = requests.post(Client.BASE_URL + f'containers/{container_id}/stop')
        return data

    @classmethod
    def retrieve(cls, container_id):
        """Retrieve a Docker container"""
        data = requests.get(Client.BASE_URL + f'containers/{container_id}/json')
        return data.json()

    @classmethod
    def all(cls):
        """List all Docker containers"""
        data = requests.get(Client.BASE_URL + f'containers/json')
        return data.json()

    @classmethod
    def logs(cls, container_id):
        """Retrieve logs (and write to file) of a Docker container"""
        # TODO: Use attach endpoint instead of live log reloading
        # data = requests.post(Client.BASE_URL + f'containers/{id}/attach',
        #   data=json.dumps({
        #     'logs': True,
        #     'stream': True,
        #     'stdin': True,
        #     'stdout': True,
        #     'stderr': True
        # }), headers=Client.ATTACH_HEADERS)
        data = requests.get(Client.BASE_URL + f'containers/{container_id}/logs', \
            params={'stdout': True, 'stderr': True})
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            with open(f'logs/{datetime.today()}.txt', 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(str(data.content.decode('latin1')))
        except:
            sys.exit("Error: Harvey could not save log file")
        return data.content.decode('latin1')

    @classmethod
    def wait(cls, container_id):
        """Wait for a Docker container to exit"""
        data = requests.post(Client.BASE_URL + f'containers/{container_id}/wait')
        return data.json()

    @classmethod
    def remove(cls, container_id):
        """Remove (delete) a Docker container"""
        data = requests.delete(Client.BASE_URL + f'containers/{container_id}', \
            data=json.dumps({'force': True}), headers=Client.JSON_HEADERS)
        # TODO: Do we want to also remove links and volumes?
        return data

"""Import modules for containers"""
#pylint: disable=W0511
import json
import requests
import requests_unixsocket
from .globals import Global

# allows us to use requests_unixsocker via requests
requests_unixsocket.monkeypatch()


class Container():
    """Docker container methods"""
    @classmethod
    def create(cls, tag):
        """Create a Docker container"""
        data = requests.post(Global.BASE_URL + 'containers/create',
                             params=json.dumps({'name': tag}), data=json.dumps({'Image': tag}),
                             headers=Global.JSON_HEADERS)
        if data.status_code == 200 or data.status_code == 201 or data.status_code == 204:
            response = data.json()
        else:
            response = False
        return response

    @classmethod
    def start(cls, container_id):
        """Start a Docker container"""
        data = requests.post(
            Global.BASE_URL + f'containers/{container_id}/start')
        if data.status_code == 200 or data.status_code == 201 or data.status_code == 204:
            response = data
        else:
            response = False
        return response

    @classmethod
    def stop(cls, container_id):
        """Stop a Docker container"""
        data = requests.post(
            Global.BASE_URL + f'containers/{container_id}/stop')
        return data

    @classmethod
    def retrieve(cls, container_id):
        """Retrieve a Docker container"""
        data = requests.get(
            Global.BASE_URL + f'containers/{container_id}/json')
        return data.json()

    @classmethod
    def all(cls):
        """List all Docker containers"""
        data = requests.get(Global.BASE_URL + 'containers/json')
        return data.json()

    @classmethod
    def logs(cls, container_id):
        """Retrieve logs (and write to file) of a Docker container"""
        # TODO: Use attach endpoint instead of live log reloading
        # data = requests.post(Global.BASE_URL + f'containers/{id}/attach',
        #   data=json.dumps({
        #     'logs': True,
        #     'stream': True,
        #     'stdin': True,
        #     'stdout': True,
        #     'stderr': True
        # }), headers=Global.ATTACH_HEADERS)
        data = requests.get(Global.BASE_URL + f'containers/{container_id}/logs',
                            params={'stdout': True, 'stderr': True})
        return data.content.decode('latin1')

    @classmethod
    def wait(cls, container_id):
        """Wait for a Docker container to exit"""
        data = requests.post(
            Global.BASE_URL + f'containers/{container_id}/wait')
        if data.status_code == 200 or data.status_code == 201 or data.status_code == 204:
            response = data.json()
        else:
            response = False
        return response

    @classmethod
    def remove(cls, container_id):
        """Remove (delete) a Docker container"""
        data = requests.delete(Global.BASE_URL + f'containers/{container_id}',
                               data=json.dumps({'force': True}), headers=Global.JSON_HEADERS)
        return data

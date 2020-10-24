import requests
from harvey.globals import Global


class Container():
    @classmethod
    def create_container(cls, tag):
        """Create a Docker container
        """
        response = requests.post(
            Global.BASE_URL + 'containers/create',
            params={'name': tag},
            json={'Image': tag},
            headers=Global.JSON_HEADERS
        )
        if (
            response.status_code == 200
            or response.status_code == 201
            or response.status_code == 204
        ):
            data = response.json()
        else:
            data = False
        return data

    @classmethod
    def start_container(cls, container_id):
        """Start a Docker container
        """
        response = requests.post(
            Global.BASE_URL + f'containers/{container_id}/start')
        if (
            response.status_code == 200
            or response.status_code == 201
            or response.status_code == 204
        ):
            data = response
        else:
            data = False
        return data

    @classmethod
    def stop_container(cls, container_id):
        """Stop a Docker container
        """
        response = requests.post(
            Global.BASE_URL + f'containers/{container_id}/stop')
        return response

    @classmethod
    def inspect_container(cls, container_id):
        """Inspect the details of a Docker container
        """
        response = requests.get(
            Global.BASE_URL + f'containers/{container_id}/json')
        return response.json()

    @classmethod
    def list_containers(cls):
        """List all Docker containers
        """
        response = requests.get(Global.BASE_URL + 'containers/json')
        return response.json()

    @classmethod
    def inspect_container_logs(cls, container_id):
        """Retrieve logs (and write to file) of a Docker container
        """
        # TODO: Use attach endpoint instead of live log reloading
        # response = requests.post(Global.BASE_URL + f'containers/{id}/attach',
        #   json={
        #     'logs': True,
        #     'stream': True,
        #     'stdin': True,
        #     'stdout': True,
        #     'stderr': True
        # }, headers=Global.ATTACH_HEADERS)
        response = requests.get(
            Global.BASE_URL + f'containers/{container_id}/logs',
            params={'stdout': True, 'stderr': True}
        )
        return response.content.decode('latin1')

    @classmethod
    def wait_container(cls, container_id):
        """Wait for a Docker container to exit
        """
        response = requests.post(
            Global.BASE_URL + f'containers/{container_id}/wait')
        if (
            response.status_code == 200
            or response.status_code == 201
            or response.status_code == 204
        ):
            data = response.json()
        else:
            data = False
        return data

    @classmethod
    def remove_container(cls, container_id):
        """Remove (delete) a Docker container
        """
        response = requests.delete(
            Global.BASE_URL + f'containers/{container_id}',
            json={'force': True},
            headers=Global.JSON_HEADERS
        )
        return response

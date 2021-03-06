import requests

from harvey.globals import Global


class Container():
    @classmethod
    def create_container(cls, container_id):
        """Create a Docker container.
        Requires an image tag and container name
        """
        response = requests.post(
            f'{Global.BASE_URL}containers/create',
            params={'name': container_id},
            json={'Image': container_id},
            headers=Global.JSON_HEADERS
        )
        return response

    @classmethod
    def start_container(cls, container_id):
        """Start a Docker container
        """
        response = requests.post(
            f'{Global.BASE_URL}containers/{container_id}/start'
        )
        return response

    @classmethod
    def stop_container(cls, container_id):
        """Stop a Docker container
        """
        response = requests.post(
            f'{Global.BASE_URL}containers/{container_id}/stop'
        )
        return response

    @classmethod
    def inspect_container(cls, container_id):
        """Inspect the details of a Docker container
        """
        response = requests.get(
            f'{Global.BASE_URL}containers/{container_id}/json'
        )
        return response

    @classmethod
    def list_containers(cls):
        """List all Docker containers
        """
        response = requests.get(f'{Global.BASE_URL}containers/json')
        return response

    @classmethod
    def inspect_container_logs(cls, container_id):
        """Retrieve logs (and write to file) of a Docker container
        """
        response = requests.get(
            f'{Global.BASE_URL}containers/{container_id}/logs',
            params={'stdout': True, 'stderr': True}
        )
        # TODO: Fix encoding here (test output for instance)
        # TODO: Returning the content like this doesn't allow us to use a status_code
        return response.content.decode('latin1')

    @classmethod
    def wait_container(cls, container_id):
        """Wait for a Docker container to exit
        """
        response = requests.post(
            f'{Global.BASE_URL}containers/{container_id}/wait'
        )
        return response

    @classmethod
    def remove_container(cls, container_id):
        """Remove (delete) a Docker container
        """
        response = requests.delete(
            f'{Global.BASE_URL}containers/{container_id}',
            json={'force': True},
            headers=Global.JSON_HEADERS
        )
        return response

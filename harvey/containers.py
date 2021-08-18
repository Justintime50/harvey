import requests

from harvey.globals import Global


class Container:
    @staticmethod
    def create_container(container_id):
        """Create a Docker container. Requires an image tag and container name."""
        response = requests.post(
            f'{Global.BASE_URL}containers/create',
            params={'name': container_id},
            json={'Image': container_id},
            headers=Global.JSON_HEADERS,
        )
        return response

    @staticmethod
    def start_container(container_id):
        """Start a Docker container."""
        response = requests.post(f'{Global.BASE_URL}containers/{container_id}/start')
        return response

    @staticmethod
    def stop_container(container_id):
        """Stop a Docker container."""
        response = requests.post(f'{Global.BASE_URL}containers/{container_id}/stop')
        return response

    @staticmethod
    def inspect_container(container_id):
        """Inspect the details of a Docker container."""
        response = requests.get(f'{Global.BASE_URL}containers/{container_id}/json')
        return response

    @staticmethod
    def list_containers():
        """List all Docker containers."""
        response = requests.get(f'{Global.BASE_URL}containers/json')
        return response

    @staticmethod
    def inspect_container_logs(container_id):
        """Retrieve logs (and write to file) of a Docker container."""
        response = requests.get(
            f'{Global.BASE_URL}containers/{container_id}/logs',
            params={
                'stdout': True,
                'stderr': True,
            },
        )
        # TODO: Fix encoding here (test output for instance)
        # TODO: Returning the content like this doesn't allow us to use a status_code
        return response.content.decode('latin1')

    @staticmethod
    def wait_container(container_id):
        """Wait for a Docker container to exit."""
        response = requests.post(f'{Global.BASE_URL}containers/{container_id}/wait')
        return response

    @staticmethod
    def remove_container(container_id):
        """Remove (delete) a Docker container."""
        response = requests.delete(
            f'{Global.BASE_URL}containers/{container_id}',
            json={
                'force': True,
            },
            headers=Global.JSON_HEADERS,
        )
        return response

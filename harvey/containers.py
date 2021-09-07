import requests

from harvey.globals import Global


class Container:
    @staticmethod
    def inspect_container(container_id):
        """Inspect the details of a Docker container."""
        # TODO: This could be where we use the docker package
        # TODO: Down the road, create an endpoint that can take advantage of this
        response = requests.get(f'{Global.BASE_URL}containers/{container_id}/json')

        return response

    @staticmethod
    def list_containers():
        """List all Docker containers."""
        # TODO: This could be where we use the docker package
        # TODO: Down the road, create an endpoint that can take advantage of this
        response = requests.get(f'{Global.BASE_URL}containers/json')

        return response

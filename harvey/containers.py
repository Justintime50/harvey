import time

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

    @staticmethod
    def run_container_healthcheck(webhook, retry_attempt=0):
        """Run a healthcheck to ensure the container is running and not in a transitory state.
        Not to be confused with the "Docker Healthcheck" functionality which is different.

        If we cannot inspect a container, it may not be up and running yet, we'll retry
        a few times before abandoning the healthcheck.
        """
        container_healthy = False
        max_retries = 5
        container = Container.inspect_container(Global.repo_name(webhook))
        container_json = container.json()
        container_state = container_json.get('State')

        # We need to explicitly check for a state and a running key here
        if container_state and container_state['Running'] is True:
            container_healthy = True
        elif retry_attempt < max_retries:
            # TODO: This is a great spot for logging what container is failing, what attempt it's on,
            # and why it's failing with some helpful data
            retry_attempt += 1
            time.sleep(3)
            Container.run_container_healthcheck(webhook, retry_attempt)

        return container_healthy

import time

import docker


class Container:
    @staticmethod
    def create_client():
        """Creates a Docker client to use for connections.

        Be aware that invoking this multiple times for different processes will open multiple
        connections at once, there is probably some optimizations we can/should make with this.
        """
        client = docker.from_env(timeout=30)  # TODO: Allow this to be configurable

        return client

    @staticmethod
    def get_container(container_id):
        """Get the details of a Docker container."""
        client = Container.create_client()
        container = client.containers.get(container_id)

        return container

    @staticmethod
    def list_containers():
        """Return a list of all Docker containers.

        To grab details of a single record, use something like `container.attrs['Name']`.
        """
        client = Container.create_client()
        containers = client.containers.list(limit=100)  # TODO: Allow this to be configurable

        return containers

    @staticmethod
    def run_container_healthcheck(container_name, retry_attempt=0):
        """Run a healthcheck to ensure the container is running and not in a transitory state.
        Not to be confused with the "Docker Healthcheck" functionality which is different.

        If we cannot inspect a container, it may not be up and running yet, we'll retry
        a few times before abandoning the healthcheck.
        """
        container_healthy = False
        max_retries = 4
        container = Container.get_container(container_name)

        if container.status.lower() == 'running':
            container_healthy = True
        elif retry_attempt < max_retries:
            # TODO: This is a great spot for logging what container is failing, what attempt it's on,
            # and why it's failing with some helpful data
            retry_attempt += 1
            time.sleep(3)
            Container.run_container_healthcheck(container_name, retry_attempt)

        return container_healthy

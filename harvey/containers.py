import time

import docker

from harvey.globals import Global


class Container:
    @staticmethod
    def create_client():
        """Creates a Docker client to use for connections.

        Be aware that invoking this multiple times for different processes will open multiple
        connections at once, there is probably some optimizations we can/should make with this.
        """
        Global.LOGGER.debug('Setting up Docker client...')
        client = docker.from_env(timeout=30)  # TODO: Allow this to be configurable

        return client

    @staticmethod
    def get_container(container_id):
        """Get the details of a Docker container."""
        Global.LOGGER.debug(f'Getting details from {container_id}')
        client = Container.create_client()
        container = client.containers.get(container_id)

        return container

    @staticmethod
    def list_containers():
        """Return a list of all Docker containers.

        To grab details of a single record, use something like `container.attrs['Name']`.
        """
        Global.LOGGER.debug('Listing containers...')
        client = Container.create_client()
        containers = client.containers.list(limit=100)  # TODO: Allow this to be configurable

        return containers

    @staticmethod
    def run_container_healthcheck(container_name, retry_attempt=1):
        """Run a healthcheck to ensure the container is running and not in a transitory state.
        Not to be confused with the "Docker Healthcheck" functionality which is different.

        If we cannot inspect a container, it may not be up and running yet, we'll retry
        a few times before abandoning the healthcheck.
        """
        Global.LOGGER.info(f'Running healthcheck attempt #{retry_attempt} for {container_name}...')
        container_healthy = False
        max_retries = 5
        container = Container.get_container(container_name)

        if container.status.lower() == 'running':
            container_healthy = True
            Global.LOGGER.info(f'{container_name} healthcheck passed!')
        elif retry_attempt < max_retries:
            Global.LOGGER.warning(f'{container_name} healthcheck failed, retrying...')
            retry_attempt += 1
            time.sleep(3)
            Container.run_container_healthcheck(container_name, retry_attempt)

        return container_healthy

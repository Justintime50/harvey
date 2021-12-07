import time
from typing import List

import docker  # type: ignore
import woodchips

from harvey.utils import LOGGER_NAME


class Container:
    @staticmethod
    def create_client():
        """Creates a Docker client to use for connections.

        TODO: Be aware that invoking this multiple times for different processes will open multiple
        connections at once, there is probably some optimizations we can/should make with this.
        """
        logger = woodchips.get(LOGGER_NAME)

        logger.debug('Setting up Docker client...')
        client = docker.from_env(timeout=30)  # TODO: Allow this to be configurable

        return client

    @staticmethod
    def get_container(container_id: str):
        """Get the details of a Docker container."""
        logger = woodchips.get(LOGGER_NAME)

        logger.debug(f'Getting details from {container_id}')
        client = Container.create_client()
        container = client.containers.get(container_id)

        return container

    @staticmethod
    def list_containers() -> List:
        """Return a list of all Docker containers.

        To grab details of a single record, use something like `container.attrs['Name']`.
        """
        logger = woodchips.get(LOGGER_NAME)

        logger.debug('Listing containers...')
        client = Container.create_client()
        containers = client.containers.list(limit=100)  # TODO: Allow this to be configurable

        return containers

    @staticmethod
    def run_container_healthcheck(container_name: str, retry_attempt: int = 1) -> bool:
        """Run a healthcheck to ensure the container is running and not in a transitory state.
        Not to be confused with the "Docker Healthcheck" functionality which is different.

        If we cannot inspect a container, it may not be up and running yet, we'll retry
        a few times before abandoning the healthcheck.
        """
        logger = woodchips.get(LOGGER_NAME)

        logger.info(f'Running healthcheck attempt #{retry_attempt} for {container_name}...')
        container_healthy = False
        max_retries = 5
        container = Container.get_container(container_name)

        if container.status.lower() == 'running':
            container_healthy = True
            logger.info(f'{container_name} healthcheck passed!')
        elif retry_attempt < max_retries:
            logger.warning(f'{container_name} healthcheck failed, retrying...')
            retry_attempt += 1
            time.sleep(3)
            Container.run_container_healthcheck(container_name, retry_attempt)

        return container_healthy

import time
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import docker  # type: ignore
import woodchips

from harvey.config import Config
from harvey.utils import Utils


class Container:
    @staticmethod
    def create_client():
        """Creates a Docker client to use for connections."""
        logger = woodchips.get(Config.logger_name)

        logger.debug('Setting up Docker client...')
        client = docker.from_env(timeout=30)

        return client

    @staticmethod
    def get_container(client, container_id: str) -> Optional[Any]:
        """Get the details of a Docker container."""
        logger = woodchips.get(Config.logger_name)

        logger.debug(f'Getting details from {container_id}...')

        try:
            container = client.containers.get(container_id)
        except (docker.errors.NotFound, docker.errors.APIError):
            # If the Docker API errors or the image doesn't exist, fail gracefully by returning `None`
            container = None

        return container

    @staticmethod
    def list_containers(client) -> List[Any]:
        """Return a list of all Docker containers.

        To grab details of a single record, use something like `container.attrs['Name']`.
        """
        logger = woodchips.get(Config.logger_name)

        logger.debug('Listing containers...')

        try:
            containers = client.containers.list(limit=100)
        except docker.errors.APIError:
            # If the Docker API errors, fail gracefully with an empty list
            containers = []

        return containers

    @staticmethod
    def run_container_healthcheck(docker_client, container_name: str, webhook: Dict[str, Any]) -> bool:
        """Run a healthcheck to ensure the container is running and not in a transitory state.
        Not to be confused with the "Docker Healthcheck" functionality which is different.

        If we cannot inspect a container, it may not be up and running yet, we'll retry
        a few times before abandoning the healthcheck.
        """
        logger = woodchips.get(Config.logger_name)

        container_healthy = False
        max_retries = 5
        retry_delay_seconds = 3

        for attempt in range(1, max_retries + 1):
            logger.info(f'Running healthcheck attempt #{attempt} for {container_name}...')

            # TODO: This function should check if the container uptime is under say 30 seconds to ensure
            # it got restarted instead of failing silently and remaining on the old deploy
            container = Container.get_container(docker_client, container_name)

            if container is None:
                message = (
                    f'Harvey could not get container details for {container_name} during Healthcheck.'
                    ' As such, Harvey could not determine if the deployment was successful or not.'
                )
                logger.warning(message)
                Utils.kill(message, webhook)
            elif container.status.lower() == 'running':
                container_healthy = True
                logger.info(f'{container_name} healthcheck passed!')
                break
            else:
                logger.warning(f'{container_name} healthcheck failed, retrying...')
                time.sleep(retry_delay_seconds)

        return container_healthy

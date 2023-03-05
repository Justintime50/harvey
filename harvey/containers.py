import datetime
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
from harvey.errors import HarveyError
from harvey.utils.deployments import kill_deployment


class Container:
    @staticmethod
    def create_client():
        """Creates a Docker client to use for connections."""
        logger = woodchips.get(Config.logger_name)

        logger.debug('Setting up Docker client...')
        client = docker.from_env(timeout=10)

        return client

    @staticmethod
    def get_container(client, container_id: str) -> Optional[Any]:
        """Get the details of a Docker container."""
        logger = woodchips.get(Config.logger_name)

        logger.debug(f'Getting details from {container_id}...')

        try:
            container = client.containers.get(container_id)
        except docker.errors.NotFound:
            # If the Docker API errors or the image doesn't exist, fail gracefully by returning `None`
            container = None
        except (docker.errors.APIError, Exception):
            error_message = 'Could not communicate with Docker!'
            logger.critical(error_message)
            raise HarveyError(error_message)

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
        except (docker.errors.APIError, Exception):
            error_message = 'Could not communicate with Docker!'
            logger.critical(error_message)
            raise HarveyError(error_message)

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

            container = Container.get_container(docker_client, container_name)

            if container is None:
                message = f'Harvey did not get container details from Docker for {container_name} during Healthcheck.'
                logger.error(message)
                kill_deployment(message, webhook)
            elif container.status.lower() == 'running' and Container.container_recently_restarted(container.__dict__):
                container_healthy = True
                logger.info(f'{container_name} healthcheck passed!')
                break
            elif container.status.lower() != 'running':
                logger.warning(f'{container_name} healthcheck failed due to current container status, retrying...')
                time.sleep(retry_delay_seconds)
            elif container.status.lower() == 'running' and not Container.container_recently_restarted(
                container.__dict__
            ):
                message = f'{container_name} healthcheck failed due to container not restarting on deploy.'
                logger.error(message)
                kill_deployment(
                    message=message,
                    webhook=webhook,
                    raise_error=True,
                )

        return container_healthy

    @staticmethod
    def container_recently_restarted(container_dictionary: Dict[str, Any]):
        """Determines if the container was recently restarted or not within the last minute by getting the
        difference of datetimes between now and the container's start time. If it's greater than 60 seconds,
        we know the container didn't restart with this deploy.

        Docker appears to store dates in RFC 3339 Nano and UTC time so we chop off the ending digits and
        convert to a Python datetime here for comparison.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        container_start_datetime = datetime.datetime.strptime(
            container_dictionary['attrs']['State'].get('StartedAt', '')[:-4], '%Y-%m-%dT%H:%M:%S.%f'
        ).replace(tzinfo=datetime.timezone.utc)
        container_age_difference = now - container_start_datetime

        grace_period_seconds = 60.0
        container_restarted_recently = container_age_difference.total_seconds() <= grace_period_seconds

        return container_restarted_recently

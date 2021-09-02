import os
import subprocess
import time
from datetime import datetime

from harvey.containers import Container
from harvey.globals import Global
from harvey.utils import Utils

# TODO: We may now be able to consolidate the `pipeline` and `stage` namespaces and verbage


class Deploy:
    @staticmethod
    def run(config, webhook, output):
        """Build Stage, used for `deploy` pipelines that hit the `compose` endpoint.

        This flow doesn't use the standard Docker API and instead shells out to run
        `docker-compose` commands, perfect for projects with docker-compose.yml files.
        """
        start_time = datetime.now()
        compose_file_flag = f'-f {config["compose"]}' if config.get('compose') else None

        try:
            compose_command = subprocess.check_output(
                f'cd {os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))}'
                f' && docker-compose {compose_file_flag} up -d --build',
                stdin=None,
                stderr=None,
                shell=True,
                timeout=Global.DEPLOY_TIMEOUT,
            )
            compose_output = compose_command.decode('UTF-8')
            execution_time = f'Deploy stage execution time: {datetime.now() - start_time}'
            final_output = f'{compose_output}\n{execution_time}'
            print(final_output)  # TODO: Replace with logging
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out deploying.'
            print(final_output)  # TODO: Replace with logging
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'{output}\nError: Harvey could not finish the deploy.'
            Utils.kill(final_output, webhook)

        return final_output

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
            Deploy.run_container_healthcheck(webhook, retry_attempt)

        return container_healthy

import os
import subprocess
import time
from datetime import datetime

from harvey.containers import Container
from harvey.globals import Global
from harvey.images import Image
from harvey.utils import Utils


class TestStage:
    @staticmethod
    def run(config, webhook, output):
        """Test Stage, used in "test" and "full" pipelines.

        1. Build an image
        2. Create a container
        3. Run your tests in a contained environment and wait for it to complete
        4. Grab the logs from the container after exiting
        5. Tear down the test env

        This function is intentionally long as everything it tightly coupled and cascades
        requiring that each step receive info from the last step in the process.
        """
        start_time = datetime.now()
        test_project_name = f'test-{Global.docker_project_name(webhook)}-{config["language"]}-{config["version"]}'
        context = 'test'

        # Build the image
        try:
            image = Image.build_image(config, webhook, context)
            image_output = f'Test image created.\n{image}'
            print(image_output)
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out building the Test image.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError as error:
            final_output = f'{output}\nError: Harvey could not build the Test image.\n{error.output}'
            print(final_output)
            Utils.kill(final_output, webhook)

        # Create a container
        container = Container.create_container(test_project_name)
        if container:
            container_output = 'Test container created.'
            print(container_output)
        else:
            final_output = f'{output}\n{image_output}\nError: Harvey could not create the Test container.'
            # Cleanup items as a result of failure so we don't leave orphaned images/containers
            Image.remove_image(test_project_name)
            Utils.kill(final_output, webhook)

        # Start the container
        start = Container.start_container(test_project_name)
        if start:
            start_output = 'Test container started.'
            print(start_output)
        else:
            final_output = f'{output}\n{image_output}\n{container_output}\nError: Harvey could not start the container.'
            # Cleanup items as a result of failure so we don't leave orphaned images/containers
            Image.remove_image(image[0])
            Container.remove_container(test_project_name)
            Utils.kill(final_output, webhook)

        # Wait for container to exit
        wait = Container.wait_container(test_project_name)
        if wait:
            wait_output = 'Waiting for Test container to exit.'
            print(wait_output)
        else:
            final_output = (
                f'{output}'
                f'\n{image_output}'
                f'\n{container_output}'
                f'\n{start_output}'
                '\nError: Harvey could not wait for the container.'
            )
            # Cleanup items as a result of failure so we don't leave orphaned images/containers
            Image.remove_image(image[0])
            Container.remove_container(test_project_name)
            Utils.kill(final_output, webhook)

        # Return logs
        logs = Container.inspect_container_logs(test_project_name)
        if logs:
            logs_output = (
                '\nTest logs:\n'
                '============================================================\n'
                f'{logs.text}'
                '============================================================\n'
            )
            print(logs_output)
        else:
            final_output = (
                f'{output}'
                f'\n{image_output}'
                f'\n{container_output}'
                f'\n{start_output}'
                f'\n{wait_output}'
                '\nError: Harvey could not create the container logs.'
            )
            # Cleanup items as a result of failure so we don't leave orphaned images/containers
            Image.remove_image(image[0])
            Container.remove_container(test_project_name)
            Utils.kill(final_output, webhook)

        # Remove container and image after it's done
        remove = Container.remove_container(test_project_name)
        if remove:
            Image.remove_image(image[0])
            remove_output = 'Test container and image removed.'
            print(remove_output)
        else:
            final_output = (
                f'{output}'
                f'\n{image_output}'
                f'\n{container_output}'
                f'\n{start_output}'
                f'\n{wait_output}'
                f'\n{logs_output}'
                '\nError: Harvey could not remove the container and/or image.'
            )
            # Cleanup items as a result of failure so we don't leave orphaned images/containers
            Image.remove_image(image[0])
            Container.remove_container(test_project_name)
            Utils.kill(final_output, webhook)

        execution_time = f'\nTest stage execution time: {datetime.now() - start_time}'
        final_output = (
            f'{image_output}'
            f'\n{container_output}'
            f'\n{start_output}'
            f'\n{wait_output}'
            f'\n{logs_output}'
            f'\n{remove_output}'
            f'\n{execution_time}'
        )
        print(execution_time)

        return final_output


class BuildStage:
    @staticmethod
    def run(config, webhook, output):
        """Build Stage, used in "deploy" and "full" pipelines.

        1. Remove the image if it already exists to ensure a clean start
        1. Build the image
        """
        start_time = datetime.now()

        # Build the image
        try:
            Image.remove_image(Global.docker_project_name(webhook))
            image = Image.build_image(config, webhook)
            image_output = f'Project image created\n{image}'
            execution_time = f'Build stage execution time: {datetime.now() - start_time}'
            final_output = f'{image_output}\n{execution_time}\n'
            print(final_output)
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out during the build stage.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = output + '\nError: Harvey could not finish the build stage.'
            Utils.kill(final_output, webhook)

        return final_output


class DeployStage:
    @staticmethod
    def run(webhook, output):
        """Deploy Stage, used in "deploy" and "full" pipelines.

        1. Stop a container by the same name as the one we want to deploy
        2. Wait for the container to stop
        3. Delete the old container
        4. Create a new container
        5. Start the new container
        """
        start_time = datetime.now()

        # Tear down the old container if one exists, this ensures a fresh container
        # is used for each deploy and is required to flush out stopped containers
        # for example
        #
        # TODO: Determine what the best method for tearing down old containers is
        # For instance, what if the user stopped a container explicitly and now it
        # will be overriden? What about volume persistence?

        # Stop the old container
        stop_container = Container.stop_container(Global.docker_project_name(webhook))
        if stop_container.status_code == 204:
            stop_output = f'Stopping old {Global.docker_project_name(webhook)} container.'
            print(stop_output)
        elif stop_container.status_code == 304:
            stop_output = ''
        elif stop_container.status_code == 404:
            stop_output = ''
        else:
            stop_output = 'Error: Harvey could not stop the container.'
            print(stop_output)

        # Wait for the container to stop
        wait_container = Container.wait_container(Global.docker_project_name(webhook))
        if wait_container.status_code == 200:
            wait_output = f'Waiting for old {Global.docker_project_name(webhook)} container to exit...'
            print(wait_output)
        elif wait_container.status_code == 404:
            wait_output = ''
        else:
            print(
                f'Error: Harvey could not wait for the {Global.docker_project_name(webhook)} container: {wait_container.json()}'  # noqa
            )

        # Remove the old container
        remove_container = Container.remove_container(Global.docker_project_name(webhook))
        if remove_container.status_code == 204:
            remove_output = f'Removing old {Global.docker_project_name(webhook)} container.'
            print(remove_output)
        elif remove_container.status_code == 404:
            remove_output = ''
        else:
            print(
                f'Error: Harvey could not remove the {Global.docker_project_name(webhook)} container: {remove_container.json()}'  # noqa
            )

        # Create a container
        create_container = Container.create_container(Global.docker_project_name(webhook))
        if create_container.status_code == 201:
            create_output = f'{Global.docker_project_name(webhook)} container created.'
            print(create_output)
        else:
            final_output = (
                f'{output}'
                f'\n{stop_output}'
                f'\n{wait_output}'
                f'\n{remove_output}'
                f'\nError: Harvey could not create the container in the deploy stage: {create_container.json()}'
            )
            Utils.kill(final_output, webhook)

        # Start the container
        start_container = Container.start_container(Global.docker_project_name(webhook))
        if start_container.status_code == 204:
            start_output = f'{Global.docker_project_name(webhook)} container started.'
            print(start_output)
        else:
            final_output = (
                f'{output}'
                f'\n{stop_output}'
                f'\n{wait_output}'
                f'\n{remove_output}'
                f'\n{create_output}'
                f'\nError: Harvey could not start the container in the deploy stage: {start_container.json()}'
            )
            Utils.kill(final_output, webhook)

        execution_time = f'\nDeploy stage execution time: {datetime.now() - start_time}'
        final_output = (
            f'{stop_output}\n{wait_output}\n{remove_output}\n{create_output}\n{start_output}\n{execution_time}'
        )
        print(execution_time)

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
        container = Container.inspect_container(Global.docker_project_name(webhook))
        container_json = container.json()
        container_state = container_json.get('State')

        # We need to explicitly check for a state and a running key here
        if container_state and container_state['Running'] is True:
            container_healthy = True
        elif retry_attempt < max_retries:
            # TODO: This is a great spot for logging what container is failing and what attempt it is
            retry_attempt += 1
            time.sleep(5)
            DeployStage.run_container_healthcheck(webhook, retry_attempt)

        return container_healthy


class DeployComposeStage:
    @staticmethod
    def run(config, webhook, output):
        """Build Stage, used for `deploy` pipelines that hit the `compose` endpoint.

        This flow doesn't use the standard Docker API and instead shells out to run
        `docker-compose` commands, perfect for projects with docker-compose.yml files.
        """
        start_time = datetime.now()
        compose = f'-f {config["compose"]}' if config.get('compose') else None
        # Docker will complete the project name by appending the container_name field and a 1
        # A full example is something like `harvey_ownername_reponame_1`
        project_name = f'harvey_{Global.repo_owner_name(webhook)}'

        # Build the image and container from the docker-compose file
        try:
            compose_command = subprocess.check_output(
                f'cd {os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))}'
                f' && docker-compose {compose} --project-name {project_name} up -d --build',
                stdin=None,
                stderr=None,
                shell=True,
                timeout=Global.BUILD_TIMEOUT,
            )
            compose_output = compose_command.decode('UTF-8')
            execution_time = f'Build/Deploy stage execution time: {datetime.now() - start_time}'
            final_output = f'{compose_output}\n{execution_time}'
            print(final_output)
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out during the docker compose build/deploy stage.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'{output}\nError: Harvey could not finish the build/deploy compose stage.'
            Utils.kill(final_output, webhook)

        return final_output

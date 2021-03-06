import os
import subprocess
import time
from datetime import datetime

from harvey.container import Container
from harvey.globals import Global
from harvey.image import Image
from harvey.utils import Utils


# TODO: Break up each Stage into a separate class, practice DRY
class Stage():
    @classmethod
    def test(cls, config, webhook, output):
        """Test Stage
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
        except subprocess.CalledProcessError:
            # TODO: Figure out how to send docker build output if this fails
            final_output = output + '\nError: Harvey could not build the Test image.'
            print(final_output)
            Utils.kill(final_output, webhook)

        # Create a container
        container = Container.create_container(test_project_name)
        if container:
            container_output = 'Test container created.'
            print(container_output)
        else:
            final_output = output + image_output + \
                '\nError: Harvey could not create the Test container.'
            Image.remove_image(test_project_name)
            Utils.kill(final_output, webhook)

        # Start the container
        start = Container.start_container(test_project_name)
        if start:
            start_output = 'Test container started.'
            print(start_output)
        else:
            final_output = output + image_output + container_output + \
                '\nError: Harvey could not start the container.'
            Image.remove_image(image[0])
            Container.remove_container(test_project_name)
            Utils.kill(final_output, webhook)

        # Wait for container to exit
        wait = Container.wait_container(test_project_name)
        if wait:
            wait_output = 'Waiting for Test container to exit.'
            print(wait_output)
        else:
            final_output = output + image_output + container_output + start_output + \
                '\nError: Harvey could not wait for the container.'
            Image.remove_image(image[0])
            Container.remove_container(test_project_name)
            Utils.kill(final_output, webhook)

        # Return logs
        logs = Container.inspect_container_logs(test_project_name)
        if logs:
            logs_output = '\nTest logs:\n' + \
                '============================================================\n' \
                + logs + '============================================================\n'
            print(logs_output)
        else:
            final_output = output + image_output + container_output + start_output + wait_output + \
                '\nError: Harvey could not create the container logs.'
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
            final_output = output + image_output + container_output + start_output + \
                wait_output + logs_output + \
                '\nError: Harvey could not remove the container and/or image.'
            Image.remove_image(image[0])
            Container.remove_container(test_project_name)
            Utils.kill(final_output, webhook)

        execution_time = f'\nTest stage execution time: {datetime.now() - start_time}'
        final_output = f'{image_output}\n{container_output}\n{start_output}\n{wait_output}\n\
            {logs_output}\n{remove_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def build(cls, config, webhook, output):
        """Build Stage
        """
        start_time = datetime.now()

        # Build the image
        try:
            Image.remove_image(Global.docker_project_name(webhook))
            image = Image.build_image(config, webhook)
            image_output = f'Project image created\n{image}'
            print(image_output)
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out during the build stage.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = output + '\nError: Harvey could not finish the build stage.'
            Utils.kill(final_output, webhook)

        execution_time = f'Build stage execution time: {datetime.now() - start_time}'
        final_output = f'{image_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def deploy(cls, webhook, output):
        """Deploy Stage
        """
        start_time = datetime.now()

        # Tear down the old container if one exists, this ensures a fresh container
        # is used for each deploy and is required to flush out stopped containers
        # for example
        #
        # TODO: Determine what the best method for tearing down old containers is
        # For instance, what if the user stopped a container explicitly and now it
        # will be overriden? What about volume persistence?
        stop_container = Container.stop_container(Global.docker_project_name(webhook))
        if stop_container.status_code == 204:
            stop_output = f'Stopping old {Global.docker_project_name(webhook)} container.'
            print(stop_output)
        elif stop_container.status_code == 304:
            stop_output = ''
        elif stop_container.status_code == 404:
            stop_output = ''
        else:
            # TODO: Add missing logic here
            stop_output = 'Error: Harvey could not stop the container.'
            print(stop_output)
        wait_container = Container.wait_container(Global.docker_project_name(webhook))
        if wait_container.status_code == 200:
            wait_output = f'Waiting for old {Global.docker_project_name(webhook)} container to exit...'
            print(wait_output)
        elif wait_container.status_code == 404:
            wait_output = ''
        else:
            # TODO: Add missing logic here
            print(
                f'Error: Harvey could not wait for the {Global.docker_project_name(webhook)} container: {wait_container.json()}'  # noqa
            )
        remove_container = Container.remove_container(Global.docker_project_name(webhook))
        if remove_container.status_code == 204:
            remove_output = f'Removing old {Global.docker_project_name(webhook)} container.'
            print(remove_output)
        elif remove_container.status_code == 404:
            remove_output = ''
        else:
            # TODO: Add missing logic here
            print(
                f'Error: Harvey could not remove the {Global.docker_project_name(webhook)} container: {remove_container.json()}'  # noqa
            )

        # Create a container
        create_container = Container.create_container(Global.docker_project_name(webhook))
        if create_container.status_code == 201:
            create_output = f'{Global.docker_project_name(webhook)} container created.'
            print(create_output)
        else:
            final_output = output + stop_output + wait_output + remove_output + \
                f'\nError: Harvey could not create the container in the deploy stage: {create_container.json()}'
            Utils.kill(final_output, webhook)

        # Start the container
        start_container = Container.start_container(Global.docker_project_name(webhook))
        if start_container.status_code == 204:
            start_output = f'{Global.docker_project_name(webhook)} container started.'
            print(start_output)
        else:
            final_output = output + stop_output + wait_output + remove_output + \
                create_output + \
                f'\nError: Harvey could not start the container in the deploy stage: {start_container.json()}'
            Utils.kill(final_output, webhook)

        execution_time = f'\nDeploy stage execution time: {datetime.now() - start_time}'
        final_output = f'{stop_output}\n{wait_output}\n{remove_output}\n{create_output}\n' + \
            f'{start_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def build_deploy_compose(cls, config, webhook, output):
        """Build Stage - USING A DOCKER COMPOSE FILE
        """
        start_time = datetime.now()
        if "compose" in config:
            compose = f'-f {config["compose"]}'
        else:
            compose = ''

        # Build the image and container from the docker-compose file
        try:
            compose = subprocess.check_output(
                f'cd {os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))} \
                && docker-compose {compose} up -d --build',
                stdin=None, stderr=None, shell=True, timeout=Global.BUILD_TIMEOUT)
            compose_output = compose.decode('UTF-8')
            print(compose_output)
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out during the docker compose build/deploy stage.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = output + '\nError: Harvey could not finish the' + \
                'build/deploy compose stage.'
            Utils.kill(final_output, webhook)

        execution_time = f'Build/Deploy stage execution time: {datetime.now() - start_time}'
        final_output = f'{compose_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def run_container_healthcheck(cls, webhook, retry_attempt=0):
        """Run a healthcheck to ensure the container is running and not in a transitory state.
        Not to be confused with the Docker Healthcheck functionality which is different
        """
        print('Running container healthcheck...')  # TODO: Attach project name to this line

        # If we cannot inspect a container, it may not be up and running yet, retry
        container = Container.inspect_container(Global.docker_project_name(webhook))
        container_json = container.json()
        state = container_json.get('State')
        if not state and retry_attempt <= 5:
            retry_attempt += 1
            time.sleep(5)
            cls.run_container_healthcheck(webhook, retry_attempt)
        elif state['Running'] is True:
            healthcheck = True
            output = 'Project healthcheck succeeded!'
        else:
            healthcheck = False
            output = 'Project healthcheck failed.'

        print(output)
        return healthcheck, output

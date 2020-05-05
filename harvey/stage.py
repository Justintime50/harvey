"""Import stage modules"""
# pylint: disable=W0511,R0914,R0915
from datetime import datetime
import subprocess
import os
from .globals import Global
from .container import Container
from .image import Image
from .utils import Utils

class Stage():
    """Stage methods"""
    @classmethod
    def test(cls, config, webhook, output):
        """Test Stage"""
        start_time = datetime.now()
        context = 'test'

        # Build the image
        try:
            image = Image.build(config, webhook, context)
            image_output = f'Test image created.\n{image[1]}'
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
        container = Container.create(image[0])
        if container is not False:
            container_output = 'Test container created.'
            print(container_output)
        else:
            final_output = output + image_output + \
                '\nError: Harvey could not create the Test container.'
            Image.remove(image[0])
            Utils.kill(final_output, webhook)

        # Start the container
        start = Container.start(container['Id'])
        if start is not False:
            start_output = 'Test container started.'
            print(start_output)
        else:
            final_output = output + image_output + container_output + \
                '\nError: Harvey could not start the container.'
            Image.remove(image[0])
            Container.remove(container)
            Utils.kill(final_output, webhook)

        # Wait for container to exit
        wait = Container.wait(container['Id'])
        if wait is not False:
            wait_output = 'Waiting for Test container to exit.'
            print(wait_output)
        else:
            final_output = output + image_output + container_output + start_output + \
                '\nError: Harvey could not wait for the container.'
            Image.remove(image[0])
            Container.remove(container)
            Utils.kill(final_output, webhook)

        # Return logs
        logs = Container.logs(container['Id'])
        if logs is not False:
            logs_output = '\nTest logs:\n' + \
                '============================================================\n' \
                + logs + '============================================================\n'
            print(logs_output)
        else:
            final_output = output + image_output + container_output + start_output + wait_output + \
                '\nError: Harvey could not create the container logs.'
            Image.remove(image[0])
            Container.remove(container)
            Utils.kill(final_output, webhook)

        # Remove container and image after it's done
        remove = Container.remove(container['Id'])
        if remove is not False:
            Image.remove(image[0])
            remove_output = 'Test container and image removed.'
            print(remove_output)
        else:
            final_output = output + image_output + container_output + start_output + \
                wait_output + logs_output + \
                '\nError: Harvey could not remove the container and/or image.'
            Image.remove(image[0])
            Container.remove(container)
            Utils.kill(final_output, webhook)

        execution_time = f'\nTest stage execution time: {datetime.now() - start_time}'
        final_output = f'{image_output}\n{container_output}\n{start_output}\n{wait_output}\n\
            {logs_output}\n{remove_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def build(cls, config, webhook, output):
        """Build Stage"""
        start_time = datetime.now()

        # Build the image
        try:
            Image.remove(f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}')
            image = Image.build(config, webhook)
            image_output = f'Project image created\n{image[1]}'
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
        """Deploy Stage"""
        start_time = datetime.now()

        # Tear down the old container if one exists
        # TODO: Add logic that checks if a container exists and skips these if not
        Container.stop(f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}')
        stop_output = 'Attempting to stop old project container.'
        print(stop_output)
        Container.wait(f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}')
        wait_output = 'Attempting to wait on old project container to exit.'
        print(wait_output)
        Container.remove(f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}')
        remove_output = 'Attempting to remove old project container.'
        print(remove_output)

        # Create a container
        container = Container.create( \
            f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}')
        if container is not False:
            create_output = 'Project container created.'
            print(create_output)
        else:
            final_output = output + stop_output + wait_output + remove_output + \
                '\nError: Harvey could not create the container in the deploy stage.'
            Utils.kill(final_output, webhook)

        # Start the container
        start = Container.start(container['Id'])
        if start is not False:
            start_output = 'Project container started.'
            print(start_output)
        else:
            final_output = output + stop_output + wait_output + remove_output + \
                create_output + '\nError: Harvey could not start the container in the deploy stage.'
            Utils.kill(final_output, webhook)

        execution_time = f'\nDeploy stage execution time: {datetime.now() - start_time}'
        final_output = f'{stop_output}\n{wait_output}\n{remove_output}\n{create_output}\n' + \
            f'{start_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def build_deploy_compose(cls, config, webhook, output):
        """Build Stage - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        if "compose" in config:
            compose = f'-f {config["compose"]}'
        else:
            compose = ''

        # Build the image and container from the docker-compose file
        try:
            compose = subprocess.check_output(f'cd \
                {os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))} \
                && docker-compose {compose} up -d --build', \
                stdin=None, stderr=None, shell=True, timeout=Global.BUILD_TIMEOUT)
            compose_output = compose.decode('UTF-8')
            print(compose_output)
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out during the docker compose build/deploy stage.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = output + '\nError: Harvey could not finish the \
                build/deploy compose stage.'
            Utils.kill(final_output, webhook)

        execution_time = f'Build/Deploy stage execution time: {datetime.now() - start_time}'
        final_output = f'{compose_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

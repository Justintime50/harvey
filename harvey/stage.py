"""Import stage modules"""
# pylint: disable=W0511
from datetime import datetime
import subprocess
import requests_unixsocket
from .globals import Global
from .container import Container
from .image import Image
from .utils import Utils

requests_unixsocket.monkeypatch() # allows us to use requests_unixsocker via requests

class Stage(Global):
    """Stage methods"""
    @classmethod
    def test(cls, config, webhook, output):
        """Test Stage"""
        start_time = datetime.now()
        context = 'test'

        # Build the image
        try:
            image = Image.build(config, webhook, context)
            image_output = f'Test image created\n{image[1]}'
            print(image_output)
        except:
            # TODO: Does not catch if image isn't built
            final_output = output + '\nError: Harvey could not build the image'
            Utils.kill(final_output, image[0])

        # Create a container
        try:
            container = Container.create(image[0])
            container_output = 'Test container created'
            print(container_output)
        except:
            # TODO: Does not catch if image does not exist
            final_output = output + image_output + '\nError: Harvey could not create the container'
            Utils.kill(final_output, image[0])

        # Start the container
        try:
            Container.start(container['Id'])
            start_output = 'Test container started'
            print(start_output)
        except:
            final_output = output + image_output + container_output + '\nError: Harvey could not start the container'
            Utils.kill(final_output, image[0], container)

        # Wait for container to exit
        try:
            Container.wait(container['Id'])
            wait_output = 'Waiting for Test container to exit'
            print(wait_output)
        except:
            final_output = output + image_output + container_output + start_output + '\nError: Harvey could not wait for the container'
            Utils.kill(final_output, image[0], container)

        # Return logs
        try:
            logs = Container.logs(container['Id'])
            logs_output = '\nTest logs:\n============================================================\n\n' \
                + logs + '============================================================\n'
            print(logs_output)
        except:
            final_output = output + image_output + container_output + start_output + wait_output + '\nError: Harvey could not create the container logs'
            Utils.kill(final_output, image[0], container)

        # Remove container and image after it's done
        try:
            Container.remove(container['Id'])
            Image.remove(image[0])
            remove_output = 'Test container and image removed'
            print(remove_output)
        except:
            final_output = output + image_output + container_output + start_output + wait_output + logs_output + '\nError: Harvey could not remove the container and/or image'
            Utils.kill(final_output, image[0], container)

        execution_time = f'Test stage execution time: {datetime.now() - start_time}'
        final_output = f'{image_output}\n{container_output}\n{start_output}\n{wait_output}\n\
            {logs_output}\n{remove_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def build(cls, config, webhook, output):
        """Build Stage"""
        start_time = datetime.now()
        repo_name = webhook["repository"]["name"].lower()
        owner_name = webhook["repository"]["owner"]["name"].lower()
        # Build the image
        try:
            Image.remove(f'{owner_name}-{repo_name}')
            image = Image.build(config, webhook)
            image_output = f'Project image created\n{image[1]}'
            print(image_output)
        except:
            final_output = output + '\nError: Harvey could not finish the build stage'
            Utils.kill(final_output)

        execution_time = f'Build stage execution time: {datetime.now() - start_time}'
        final_output = f'{image_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def deploy(cls, webhook, output):
        """Deploy Stage"""
        start_time = datetime.now()
        repo_name = webhook["repository"]["name"].lower()
        owner_name = webhook["repository"]["owner"]["name"].lower()
        # Tear down the old container if one exists
        # TODO: Add logic that checks if a container exists and skips these if not
        Container.stop(f'{owner_name}-{repo_name}')
        stop_output = 'Attempting to stop old project container'
        print(stop_output)
        Container.wait(f'{owner_name}-{repo_name}')
        wait_output = 'Attempting to wait on old project container to exit'
        print(wait_output)
        Container.remove(f'{owner_name}-{repo_name}')
        remove_output = 'Attempting to remove old project container'
        print(remove_output)

        # Create a container
        try:
            container = Container.create(f'{owner_name}-{repo_name}')
            create_output = 'Project container created'
            print(create_output)
        except:
            final_output = output + stop_output + wait_output + remove_output + '\nError: Harvey could not create the container in the deploy stage'
            Utils.kill(final_output)

        # Start the container
        try:
            Container.start(container['Id'])
            start_output = 'Project container started'
            print(start_output)
        except:
            final_output = output + stop_output + wait_output + remove_output + create_output + '\nError: Harvey could not start the container in the deploy stage'
            Utils.kill(final_output)

        execution_time = f'Deploy stage execution time: {datetime.now() - start_time}'
        final_output = f'{stop_output}\n{wait_output}\n{remove_output}\n{create_output}\n{start_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

    @classmethod
    def build_deploy_compose(cls, config, webhook, output):
        """Build Stage - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        full_name = webhook["repository"]["full_name"].lower()
        if "compose" in config:
            compose = f'-f {config["compose"]}'
        else:
            compose = ''

        # Build the image and container from the docker-compose file
        try:
            compose = subprocess.call(f'cd {Global.PROJECTS_PATH}/{full_name} && docker-compose {compose} up -d --build', stdin=None, stdout=None, stderr=None, shell=True)
            compose_output = compose
            print(compose_output)
        except:
            final_output = output + '\nError: Harvey could not finish the build/deploy compose stage'
            Utils.kill(final_output)

        execution_time = f'Build/Deploy stage execution time: {datetime.now() - start_time}'
        final_output = f'{compose_output}\n{execution_time}\n'
        print(execution_time)

        return final_output

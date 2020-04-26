"""Import stage modules"""
# pylint: disable=W0511
import sys
import requests
import requests_unixsocket
from .client import Client
from .container import Container
from .image import Image

requests_unixsocket.monkeypatch() # allows us to use requests_unixsocker via requests

class Stage(Client):
    """Stage methods"""
    @classmethod
    def test(cls, config, webhook):
        """Test Stage"""
        context = 'test'

        # Build the image
        try:
            image = Image.build(config, webhook, context)
            print(image, "\nImage created")
        except:
            # TODO: Does not catch if image isn't built
            sys.exit('Error: Harvey could not build image')

        # Create a container
        try:
            container = Container.create(image)
            print(container, "\nContainer created")
        except:
            # TODO: Does not catch if image does not exist
            sys.exit("Error: Harvey could not create container")

        # Start the container
        try:
            start = Container.start(container['Id'])
            print(start, "\nContainer started")
        except:
            sys.exit("Error: Harvey could not start container")

        # Wait for container to exit
        try:
            Container.wait(container['Id'])
        except:
            sys.exit("Error: Harvey could not wait for container")

        # Return logs
        try:
            logs = Container.logs(container['Id'])
            print("Logs created")
        except:
            sys.exit("Error: Harvey could not create container logs")

        # Remove container and image after it's done
        try:
            Container.remove(container['Id'])
            Image.remove(image)
            print("Container and image removed")
        except:
            print("Error: Harvey could not remove container and/or image")

        test = image + logs
        return test

    @classmethod
    def build(cls, config, webhook):
        """Build Stage"""
        repo_name = webhook["repository"]["name"].lower()
        owner_name = webhook["repository"]["owner"]["name"].lower()
        # Build the image
        try:
            Image.remove(f'{owner_name}-{repo_name}')
            image = Image.build(config, webhook)
            print(image, "\nImage created")
        except:
            sys.exit("Error: Harvey could not finish the build stage")

        return image

    @classmethod
    def deploy(cls, webhook):
        """Deploy Stage"""
        repo_name = webhook["repository"]["name"].lower()
        owner_name = webhook["repository"]["owner"]["name"].lower()
        # Tear down the old container if one exists
        try:
            resp = requests.get(Client.BASE_URL + f'containers/{owner_name}-{repo_name}/json')
            resp.raise_for_status()
            try:
                Container.stop(f'{owner_name}-{repo_name}')
                print("Container stopping")
                Container.wait(f'{owner_name}-{repo_name}')
                print("Container waiting")
                remove = Container.remove(f'{owner_name}-{repo_name}')
                print(remove, "\nOld container removed")
            except:
                sys.exit("Error: Harvey failed during old/new container swap")
        except requests.exceptions.HTTPError as err:
            print(err)

        # Create a container
        try:
            container = Container.create(f'{owner_name}-{repo_name}')
            print(container, "\nContainer created")
        except:
            sys.exit("Error: Harvey could not create the container in the deploy stage")

        # Start the container
        try:
            start = Container.start(container['Id'])
            print(start, "\nContainer started")
        except:
            sys.exit("Error: Harvey could not start the container in the deploy stage")

        return start

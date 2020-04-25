import requests
import json
import uuid
import sys
from datetime import datetime
from .client import Client
from .container import Container
from .image import Image
from .stage import Stage
from .git import Git

# TODO: Add logic to check that tests pass before moving to build
# TODO: Add logic to check that build passes before moving to deploy

class Pipeline(Client):
    @classmethod
    def test(cls, config, webhook):
        # Pull changes and run tests (no deploy)
        startTime = datetime.now()
        test = Stage.test(config, webhook)

        print(f'Execution time: {datetime.now() - startTime}')
        return test

    @classmethod
    def deploy(cls, config, webhook):
        # Pull changes and build/deploy (no tests)
        startTime = datetime.now()
        Stage.build(config, webhook)
        deploy = Stage.deploy(config, webhook)

        print(f'Execution time: {datetime.now() - startTime}')
        return deploy

    @classmethod
    def full(cls, config, webhook):
        # Pull changes, run tests, build image, start container
        startTime = datetime.now()
        Stage.test(config, webhook)
        Stage.build(config, webhook)
        deploy = Stage.deploy(config, webhook)

        print(f'Execution time: {datetime.now() - startTime}')
        return deploy

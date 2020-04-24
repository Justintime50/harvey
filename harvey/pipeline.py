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
    def test(cls, data):
        # Pull changes and run tests (no deploy)
        startTime = datetime.now()
        Git.pull(data)

        test = Stage.test(data)

        print(f'Execution time: {datetime.now() - startTime}')
        return test

    @classmethod
    def deploy(cls, data, tag):
        # Pull changes and build/deploy (no tests)
        startTime = datetime.now()
        Git.pull(data)

        Stage.build(data, tag)
        deploy = Stage.deploy(data)

        print(f'Execution time: {datetime.now() - startTime}')
        return deploy

    @classmethod
    def full(cls, data, tag):
        # Pull changes, run tests, build image, start container
        startTime = datetime.now()
        Git.pull(data)

        Stage.test(data)

        Stage.build(data, tag)

        deploy = Stage.deploy(tag)

        print(f'Execution time: {datetime.now() - startTime}')
        return deploy

"""Import Pipeline modules"""
# pylint: disable=W0511
from datetime import datetime
from .client import Client
from .stage import Stage

# TODO: Add logic to check that tests pass before moving to build
# TODO: Add logic to check that build passes before moving to deploy

class Pipeline(Client):
    """Pipeline methods"""
    @classmethod
    def test(cls, config, webhook):
        """Pull changes and run tests (no deploy)"""
        start_time = datetime.now()
        test = Stage.test(config, webhook)

        print(f'Execution time: {datetime.now() - start_time}')
        return test

    @classmethod
    def deploy(cls, config, webhook):
        """Pull changes and build/deploy (no tests)"""
        start_time = datetime.now()
        Stage.build(config, webhook)
        deploy = Stage.deploy(webhook)

        print(f'Execution time: {datetime.now() - start_time}')
        return deploy

    @classmethod
    def full(cls, config, webhook):
        """Pull changes, run tests, build image, start container"""
        start_time = datetime.now()
        Stage.test(config, webhook)
        Stage.build(config, webhook)
        deploy = Stage.deploy(webhook)

        print(f'Execution time: {datetime.now() - start_time}')
        return deploy

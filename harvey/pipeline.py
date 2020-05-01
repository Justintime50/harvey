"""Import Pipeline modules"""
# pylint: disable=W0511
from datetime import datetime
from .globals import Global
from .stage import Stage
from .utils import Utils

# TODO: Add logic to check that tests pass before moving to build
# TODO: Add logic to check that build passes before moving to deploy

class Pipeline(Global):
    """Pipeline methods"""
    @classmethod
    def test(cls, config, webhook, output):
        """Pull changes and run tests (no deploy)"""
        start_time = datetime.now()
        test = Stage.test(config, webhook, output)
        execution_time = f'Test pipeline execution time: {datetime.now() - start_time}'
        success = f'Test pipeline succeeded!'
        final_output = f'{output}\n{test}\n{execution_time}\n{success}'

        Utils.success(final_output)

        return test

    @classmethod
    def deploy(cls, config, webhook, output):
        """Pull changes and build/deploy (no tests)"""
        start_time = datetime.now()
        build = Stage.build(config, webhook, output)
        deploy = Stage.deploy(webhook, output)
        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        success = f'Deploy pipeline succeeded!'
        final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output)

        return deploy

    @classmethod
    def full(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container"""
        start_time = datetime.now()
        test = Stage.test(config, webhook, output)
        build = Stage.build(config, webhook, output)
        deploy = Stage.deploy(webhook, output)
        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        success = f'Full pipeline succeeded!'
        final_output = f'{output}\n{test}\n{build}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output)

        return deploy

    @classmethod
    def deploy_compose(cls, config, webhook, output):
        """Pull changes and build/deploy (no tests) - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        deploy = Stage.build_deploy_compose(config, webhook, output)
        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        success = f'Deploy pipeline succeeded!'
        final_output = f'{output}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output)

        return deploy

    @classmethod
    def full_compose(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        test = Stage.test(config, webhook, output)
        deploy = Stage.build_deploy_compose(config, webhook, output)
        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        success = f'Full pipeline succeeded!'
        final_output = f'{output}\n{test}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output)

        return deploy

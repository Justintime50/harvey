"""Import Pipeline modules"""
# pylint: disable=W0511
from datetime import datetime
from .stage import Stage
from .utils import Utils

# TODO: Add logic to check that tests pass before moving to build


class Pipeline():
    """Pipeline methods"""
    @classmethod
    def test(cls, config, webhook, output):
        """Pull changes and run tests (no deploy)"""
        start_time = datetime.now()
        test = Stage.test(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            execution_time = f'Test pipeline execution time: {datetime.now() - start_time}'
            failed = 'Test pipeline failed!'
            final_output = f'{output}\n{test}\n{execution_time}\n{failed}'
            Utils.kill(final_output, webhook)
        execution_time = f'Test pipeline execution time: {datetime.now() - start_time}'
        success = 'Test pipeline succeeded!'
        final_output = f'{output}\n{test}\n{execution_time}\n{success}'

        Utils.success(final_output, webhook)

        return test

    @classmethod
    def deploy(cls, config, webhook, output):
        """Pull changes and build/deploy (no tests)"""
        start_time = datetime.now()
        build = Stage.build(config, webhook, output)
        deploy = Stage.deploy(webhook, output)
        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        success = 'Deploy pipeline succeeded!'
        final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output, webhook)

        return deploy

    @classmethod
    def full(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container"""
        start_time = datetime.now()
        test = Stage.test(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
            failed = 'Full pipeline failed!'
            final_output = f'{output}\n{test}\n{execution_time}\n{failed}'
            Utils.kill(final_output, webhook)
        build = Stage.build(config, webhook, output)
        deploy = Stage.deploy(webhook, output)
        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        success = 'Full pipeline succeeded!'
        final_output = f'{output}\n{test}\n{build}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output, webhook)

        return deploy

    @classmethod
    def deploy_compose(cls, config, webhook, output):
        """Pull changes and build/deploy (no tests) - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        deploy = Stage.build_deploy_compose(config, webhook, output)
        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        success = 'Deploy pipeline succeeded!'
        final_output = f'{output}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output, webhook)

        return deploy

    @classmethod
    def full_compose(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        test = Stage.test(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
            failed = 'Full pipeline failed!'
            final_output = f'{output}\n{test}\n{execution_time}\n{failed}'
            Utils.kill(final_output, webhook)
        deploy = Stage.build_deploy_compose(config, webhook, output)
        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        success = 'Full pipeline succeeded!'
        final_output = f'{output}\n{test}\n{deploy}\n{execution_time}\n{success}'

        Utils.success(final_output, webhook)

        return deploy

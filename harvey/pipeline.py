"""Import Pipeline modules"""
# pylint: disable=W0511
from datetime import datetime
import sys
import os
from .globals import Global
from .stage import Stage

# TODO: Add logic to check that tests pass before moving to build
# TODO: Add logic to check that build passes before moving to deploy

class Pipeline(Global):
    """Pipeline methods"""
    @classmethod
    def test(cls, config, webhook, output):
        """Pull changes and run tests (no deploy)"""
        start_time = datetime.now()
        test = Stage.test(config, webhook)
        execution_time = f'Test pipeline execution time: {datetime.now() - start_time}'
        success = f'Test pipeline succeeded!'
        test_output = f'{output}\n{test}\n{execution_time}\n{success}'

        # Generate log file with all output
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            with open(f'logs/{datetime.today()}.txt', 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(test_output)
        except:
            sys.exit("Error: Harvey could not save log file")

        return test

    @classmethod
    def deploy(cls, config, webhook, output):
        """Pull changes and build/deploy (no tests)"""
        start_time = datetime.now()
        build = Stage.build(config, webhook)
        deploy = Stage.deploy(webhook)
        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        success = f'Deploy pipeline succeeded!'
        deploy_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{success}'

        # Generate log file with all output
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            with open(f'logs/{datetime.today()}.txt', 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(deploy_output)
        except:
            sys.exit("Error: Harvey could not save log file")

        return deploy

    @classmethod
    def full(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container"""
        start_time = datetime.now()
        test = Stage.test(config, webhook)
        build = Stage.build(config, webhook)
        deploy = Stage.deploy(webhook)
        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        success = f'Full pipeline succeeded!'
        full_output = f'{output}\n{test}\n{build}\n{deploy}\n{execution_time}\n{success}'

        # Generate log file with all output
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            with open(f'logs/{datetime.today()}.txt', 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(full_output)
        except:
            sys.exit("Error: Harvey could not save log file")

        return deploy

    @classmethod
    def deploy_compose(cls, config, webhook, output):
        """Pull changes and build/deploy (no tests) - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        deploy = Stage.build_deploy_compose(config, webhook)
        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        success = f'Deploy pipeline succeeded!'
        deploy_output = f'{output}\n{deploy}\n{execution_time}\n{success}'

        # Generate log file with all output
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            with open(f'logs/{datetime.today()}.txt', 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(deploy_output)
        except:
            sys.exit("Error: Harvey could not save log file")

        return deploy

    @classmethod
    def full_compose(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container - USING A DOCKER COMPOSE FILE"""
        start_time = datetime.now()
        test = Stage.test(config, webhook)
        deploy = Stage.build_deploy_compose(config, webhook)
        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        success = f'Full pipeline succeeded!'
        full_output = f'{output}\n{test}\n{deploy}\n{execution_time}\n{success}'

        # Generate log file with all output
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            with open(f'logs/{datetime.today()}.txt', 'w+') as log:
                # TODO: We may want to save project name in filename as well
                log.write(full_output)
        except:
            sys.exit("Error: Harvey could not save log file")

        return deploy

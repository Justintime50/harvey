import os
from datetime import datetime

from harvey.globals import Global
from harvey.message import Message
from harvey.stage import Stage
from harvey.utils import Utils


# TODO: Break up each pipeline into a separate class, practice DRY
class Pipeline():
    @classmethod
    def test(cls, config, webhook, output):
        """Pull changes and run tests (will not deploy code)
        """
        start_time = datetime.now()

        if os.getenv('SLACK'):
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

        test = Stage.test(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            # TODO: Ensure this works, it may be broken
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
        """Pull changes and build/deploy (no tests)
        """
        start_time = datetime.now()

        if os.getenv('SLACK'):
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

        build = Stage.build(config, webhook, output)
        deploy = Stage.deploy(webhook, output)
        healthcheck, healthcheck_message = Stage.run_container_healthcheck(webhook)

        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        if healthcheck is True:
            success = 'Deploy pipeline succeeded!'
            final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{success}'
            Utils.success(final_output, webhook)
        else:
            fail = 'Deploy pipeline failed due to bad healthcheck.'
            final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{fail}'
            Utils.kill(final_output, webhook)

        return deploy

    @classmethod
    def full(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container
        """
        start_time = datetime.now()

        if os.getenv('SLACK'):
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

        test = Stage.test(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
            failed = 'Full pipeline failed!'
            final_output = f'{output}\n{test}\n{execution_time}\n{failed}'
            Utils.kill(final_output, webhook)

        build = Stage.build(config, webhook, output)
        deploy = Stage.deploy(webhook, output)
        healthcheck, healthcheck_message = Stage.run_container_healthcheck(webhook)

        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        if healthcheck is True:
            success = 'Deploy pipeline succeeded!'
            final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{success}'
            Utils.success(final_output, webhook)
        else:
            fail = 'Deploy pipeline failed due to bad healthcheck.'
            final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{fail}'
            Utils.kill(final_output, webhook)

        return deploy

    @classmethod
    def deploy_compose(cls, config, webhook, output):
        """Pull changes and build/deploy (no tests) - USING A DOCKER COMPOSE FILE
        """
        start_time = datetime.now()

        if os.getenv('SLACK'):
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

        deploy = Stage.build_deploy_compose(config, webhook, output)
        healthcheck, healthcheck_message = Stage.run_container_healthcheck(webhook)

        execution_time = f'Deploy pipeline execution time: {datetime.now() - start_time}'
        if healthcheck is True:
            success = 'Deploy pipeline succeeded!'
            final_output = f'{output}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{success}'
            Utils.success(final_output, webhook)
        else:
            fail = 'Deploy pipeline failed due to bad healthcheck.'
            final_output = f'{output}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{fail}'
            Utils.kill(final_output, webhook)

        return deploy

    @classmethod
    def full_compose(cls, config, webhook, output):
        """Pull changes, run tests, build image, start container - USING A DOCKER COMPOSE FILE
        """
        start_time = datetime.now()

        if os.getenv('SLACK'):
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

        test = Stage.test(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
            failed = 'Full pipeline failed!'
            final_output = f'{output}\n{test}\n{execution_time}\n{failed}'
            Utils.kill(final_output, webhook)

        deploy = Stage.build_deploy_compose(config, webhook, output)
        healthcheck, healthcheck_message = Stage.run_container_healthcheck(webhook)

        execution_time = f'Full pipeline execution time: {datetime.now() - start_time}'
        if healthcheck is True:
            success = 'Deploy pipeline succeeded!'
            final_output = f'{output}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{success}'
            Utils.success(final_output, webhook)
        else:
            fail = 'Deploy pipeline failed due to bad healthcheck.'
            final_output = f'{output}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{fail}'
            Utils.kill(final_output, webhook)

        return deploy

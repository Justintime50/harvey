import json
import os
from datetime import datetime

from harvey.git import Git
from harvey.globals import Global
from harvey.messages import Message
from harvey.stages import Stage
from harvey.utils import Utils

SLACK = os.getenv('SLACK')


class Pipeline():
    @classmethod
    def initialize_pipeline(cls, webhook):
        """Initialize the setup for a pipeline by cloning/pulling the project
        and setting up standard logging info
        """
        start_time = datetime.now()
        config = cls.open_project_config(webhook)

        if SLACK:
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

        preamble = f'Running Harvey v{Global.HARVEY_VERSION}\n{config["pipeline"].title()} Pipeline Started: {start_time}'  # noqa
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}\n'
        print(preamble)
        git_message = (f'New commit by: {Global.repo_commit_author(webhook)}.'
                       f'\nCommit made on repo: {Global.repo_full_name(webhook)}.')

        git = Git.update_git_repo(webhook)

        execution_time = f'Startup execution time: {datetime.now() - start_time}\n'
        output = (f'{preamble}\n{pipeline_id}Configuration:\n{json.dumps(config, indent=4)}'
                  f'\n\n{git_message}\n{git}\n{execution_time}')
        print(execution_time)

        return config, output, start_time

    @classmethod
    def start_pipeline(cls, webhook, use_compose=False):
        """After receiving a webhook, spin up a pipeline based on the config
        If a Pipeline fails, it fails early in the individual functions being called
        """
        webhook_config, webhook_output, start_time = cls.initialize_pipeline(webhook)
        pipeline = webhook_config.get('pipeline').lower()

        if pipeline in Global.SUPPORTED_PIPELINES:
            if pipeline == 'pull':
                Utils.success(webhook_output, webhook)
            if pipeline in ['test', 'full']:
                test = cls.test(webhook_config, webhook, webhook_output, start_time)
            if pipeline in ['deploy', 'full']:
                build, deploy, healthcheck = cls.deploy(webhook_config, webhook, webhook_output, start_time, use_compose)  # noqa
        else:
            final_output = webhook_output + '\nError: Harvey could not run, there was no acceptable pipeline specified.'
            pipeline = Utils.kill(final_output, webhook)

        end_time = datetime.now()
        execution_time = f'Pipeline execution time: {end_time - start_time}'
        pipeline_status = 'Pipeline succeeded!'
        healthcheck_message = f'Project passed healthcheck: {healthcheck}'

        output_options = {
            'test': f'{webhook_output}\n{test}\n{execution_time}\n{pipeline_status}',
            'deploy': f'{webhook_output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}',  # noqa
            'full': f'{webhook_output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}',
        }
        final_output = output_options[pipeline]

        Utils.success(final_output, webhook)

        return final_output

    @classmethod
    def open_project_config(cls, webhook):
        """Open the project's config file to assign pipeline variables.

        Project configs look like the following:
        {
            "pipeline": "full",
            "language": "php",
            "version": "7.4"
        }
        """
        # TODO: Add the ability to configure projects on the Harvey side
        # (eg: save values to a database via a UI) instead of only from
        # within a JSON file in the repo
        try:
            filename = os.path.join(
                Global.PROJECTS_PATH, Global.repo_full_name(webhook), 'harvey.json'
            )
            with open(filename, 'r') as file:
                config = json.loads(file.read())
                print(json.dumps(config, indent=4))
            return config
        except FileNotFoundError:
            final_output = f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

    @classmethod
    def test(cls, config, webhook, output, start_time):
        """Run the test stage in a pipeline
        """
        test = Stage.test(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            # TODO: Ensure this works, it may be broken
            end_time = datetime.now()
            pipeline_status = 'Pipeline failed!'
            execution_time = f'Pipeline execution time: {end_time - start_time}'
            final_output = f'{output}\n{test}\n{execution_time}\n{pipeline_status}'
            Utils.kill(final_output, webhook)

        return test

    @classmethod
    def deploy(cls, config, webhook, output, start_time, use_compose):
        """Run the build and deploy stages in a pipeline
        """
        if use_compose:
            build = ''  # When using compose, there is no build step
            deploy = Stage.build_deploy_compose(config, webhook, output)
            healthcheck = True
            # healthcheck = Stage.run_container_healthcheck(webhook)  # TODO: Correct healthchecks for compose
        else:
            build = Stage.build(config, webhook, output)
            deploy = Stage.deploy(webhook, output)
            healthcheck = Stage.run_container_healthcheck(webhook)

        if healthcheck is False:
            end_time = datetime.now()
            pipeline_status = 'Pipeline failed due to a bad healthcheck.'
            execution_time = f'Pipeline execution time: {end_time - start_time}'
            healthcheck_message = f'Project passed healthcheck: {healthcheck}'
            final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}'
            Utils.kill(final_output, webhook)

        return build, deploy, healthcheck

import json
import os
import subprocess
from datetime import datetime

from harvey.containers import Container
from harvey.git import Git
from harvey.globals import Global
from harvey.messages import Message
from harvey.utils import Utils


class Pipeline:
    @staticmethod
    def initialize_pipeline(webhook):
        """Initialize the setup for a pipeline by cloning/pulling the project
        and setting up standard logging info.
        """
        start_time = datetime.now()
        # Run git operation first to ensure the config is present and up-to-date
        git = Git.update_git_repo(webhook)

        webhook_data_key = webhook.get('data')
        if webhook_data_key:
            config = webhook_data_key
            pipeline = webhook_data_key.get('pipeline')
        else:
            config = Pipeline.open_project_config(webhook)
            pipeline = config.get('pipeline')

        # TODO: We may want to setup a default pipeline of `deploy` or `pull` if none is specified
        if pipeline not in Global.SUPPORTED_PIPELINES:
            final_output = (
                f'Error: Harvey could not run for `{Global.repo_full_name(webhook)}`, there was no acceptable pipeline'
                ' specified.'
            )
            pipeline = Utils.kill(final_output, webhook)

        if Global.SLACK:
            Message.send_slack_message(
                f':hammer_and_wrench: Harvey has started a `{config["pipeline"]}` pipeline for'
                f' `{Global.repo_full_name(webhook)}`.'
            )

        # TODO: Rework the logs of a pipeline to be more informative and clean
        preamble = (
            f'Running Harvey v{Global.HARVEY_VERSION}\n{config["pipeline"].title()} Pipeline Started: {start_time}'
        )
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}'
        print(preamble)  # TODO: Replace with logging
        git_message = (
            f'New commit by: {Global.repo_commit_author(webhook)}.'
            f'\nCommit made on repo: {Global.repo_full_name(webhook)}.'
        )

        execution_time = f'Startup execution time: {datetime.now() - start_time}\n'
        output = (
            f'{preamble}'
            f'\n{pipeline_id}'
            f'\nConfiguration:\n{json.dumps(config, indent=4)}'
            f'\n\n{git_message}'
            f'\n{git}'
            f'\n{execution_time}'
        )
        print(execution_time)  # TODO: Replace with logging

        return config, output, start_time

    @staticmethod
    def run_pipeline(webhook):
        """After receiving a webhook, spin up a pipeline based on the config.
        If a Pipeline fails, it fails early in the individual functions being called.
        """
        webhook_config, webhook_output, start_time = Pipeline.initialize_pipeline(webhook)
        pipeline = webhook_config['pipeline'].lower()

        if pipeline == 'pull':
            # We simply assign the final message because if we got this far, the repo has already been pulled
            final_output = f'{webhook_output}\n:white_check_mark: Harvey pulled the project successfully.'
        elif pipeline == 'deploy':
            healthcheck = Container.run_container_healthcheck(webhook)
            deploy_output = Pipeline.deploy(webhook_config, webhook, webhook_output)

            # TODO: Can this be cleaned up a bit (DRY)
            if healthcheck is False:
                end_time = datetime.now()
                pipeline_status = 'Project Healthcheck: :skull_and_crossbones:'
                execution_time = f'Pipeline execution time: {end_time - start_time}'
                healthcheck_message = 'Pipeline failed!'

                final_output = (
                    f'{webhook_output}\n{deploy_output}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}'
                )

                Utils.kill(final_output, webhook)
            else:
                healthcheck_message = 'Project Healthcheck: :white_check_mark:'
                end_time = datetime.now()
                execution_time = f'Pipeline execution time: {end_time - start_time}'
                pipeline_status = 'Pipeline succeeded!'

                final_output = (
                    f'{webhook_output}\n{deploy_output}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}'
                )

        Utils.success(final_output, webhook)

    @staticmethod
    def open_project_config(webhook):
        """Open the project's config file to assign pipeline variables.

        Project configs look like the following:
        {
            "pipeline": "deploy",
            "compose": "some-name-compose.yml"
        }
        """
        try:
            # TODO: Long-term, turn `harvey.json` into a hidden file and make it yml: `.harvey.yml`
            filename = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook), 'harvey.json')
            with open(filename, 'r') as config_file:
                config = json.loads(config_file.read())
                print(json.dumps(config, indent=4))
            return config
        except FileNotFoundError:
            final_output = f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

    def deploy(config, webhook, output):
        """Build Stage, used for `deploy` pipelines that hit the `compose` endpoint.

        This flow doesn't use the standard Docker API and instead shells out to run
        `docker-compose` commands, perfect for projects with docker-compose.yml files.
        """
        start_time = datetime.now()
        compose_file_flag = f'-f {config["compose"]}' if config.get('compose') else ''

        try:
            compose_command = subprocess.check_output(
                f'cd {os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))}'
                f' && docker-compose {compose_file_flag} up -d --build',
                stdin=None,
                stderr=None,
                shell=True,
                timeout=Global.DEPLOY_TIMEOUT,
            )
            compose_output = compose_command.decode('UTF-8')
            execution_time = f'Deploy stage execution time: {datetime.now() - start_time}'
            final_output = f'{compose_output}\n{execution_time}'
            print(final_output)  # TODO: Replace with logging
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out deploying.'
            print(final_output)  # TODO: Replace with logging
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'{output}\nError: Harvey could not finish the deploy.'
            Utils.kill(final_output, webhook)

        return final_output

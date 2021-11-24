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
        """Initialize the setup for a pipeline by cloning or pulling the project
        and setting up standard logging info.
        """
        start_time = datetime.now()
        # Run git operation first to ensure the config is present and up-to-date
        git = Git.update_git_repo(webhook)

        webhook_data_key = webhook.get('data')
        if webhook_data_key:
            Global.LOGGER.debug(f'Pulling Harvey config for {Global.repo_full_name(webhook)} from webhook...')
            config = webhook_data_key
            pipeline = webhook_data_key.get('pipeline')
        else:
            Global.LOGGER.debug(f'Pulling Harvey config for {Global.repo_full_name(webhook)} from config file...')
            config = Pipeline.open_project_config(webhook)
            pipeline = config.get('pipeline')

        if pipeline not in Global.SUPPORTED_PIPELINES:
            final_output = (
                f'Harvey could not run for `{Global.repo_full_name(webhook)}`, there was no acceptable pipeline'
                ' specified.'
            )
            Global.LOGGER.error(final_output)
            pipeline = Utils.kill(final_output, webhook)

        pipeline_started_message = (
            f'{Global.WORK_EMOJI} Harvey has started a `{config["pipeline"]}` pipeline for'
            f' `{Global.repo_full_name(webhook)}`.'
        )
        if Global.SLACK:
            Message.send_slack_message(pipeline_started_message)

        # TODO: Rework the logs of a pipeline to be more informative and clean
        preamble = (
            f'Running Harvey v{Global.HARVEY_VERSION}\n{config["pipeline"].title()} Pipeline Started: {start_time}'
        )
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}'
        Global.LOGGER.info(preamble + ' | ' + pipeline_id)
        git_message = (
            f'New commit by: {Global.repo_commit_author(webhook)}.'
            f'\nCommit made on repo: {Global.repo_full_name(webhook)}.'
        )

        execution_time = f'{Global.repo_full_name(webhook)} startup execution time: {datetime.now() - start_time}'
        output = (
            f'{preamble}'
            f'\n{pipeline_id}'
            f'\nConfiguration:\n{json.dumps(config, indent=4)}'
            f'\n\n{git_message}'
            f'\n{git}'
            f'\n{execution_time}'
        )
        Global.LOGGER.info(execution_time)

        return config, output, start_time

    @staticmethod
    def run_pipeline(webhook):
        """After receiving a webhook, spin up a pipeline based on the config.
        If a Pipeline fails, it fails early in the individual functions being called.
        """
        webhook_config, webhook_output, start_time = Pipeline.initialize_pipeline(webhook)
        pipeline = webhook_config['pipeline'].lower()

        if pipeline == 'deploy':
            deploy_output = Pipeline.deploy(webhook_config, webhook, webhook_output)

            healthcheck = webhook_config.get('healthcheck')
            healthcheck_messages = ''

            if healthcheck:
                container_healthcheck_statuses = {}
                for container in healthcheck:
                    container_healthcheck = Container.run_container_healthcheck(container)
                    container_healthcheck_statuses[container] = container_healthcheck
                    if container_healthcheck is True:
                        healthcheck_message = f'\n{container} Healthcheck: {Global.SUCCESS_EMOJI}'
                    else:
                        container_healthcheck = f'\n{container} Healthcheck: {Global.FAILURE_EMOJI}'
                    healthcheck_messages += healthcheck_message

                healthcheck_values = container_healthcheck_statuses.values()
                all_healthchecks_passed = any(healthcheck_values) and list(healthcheck_values)[0] is True
            else:
                all_healthchecks_passed = True  # Set to true here since we cannot determine, won't kill the deploy

            end_time = datetime.now()
            execution_time = f'{Global.repo_full_name(webhook)} pipeline execution time: {end_time - start_time}'
            Global.LOGGER.info(execution_time)
            final_output = f'{webhook_output}\n{deploy_output}\n{execution_time}\n{healthcheck_messages}'

            if all_healthchecks_passed or not healthcheck:
                Utils.success(final_output, webhook)
            else:
                Utils.kill(final_output, webhook)
        elif pipeline == 'pull':
            # We simply assign the final message because if we got this far, the repo has already been pulled
            pull_success_message = (
                f'Harvey pulled {Global.repo_full_name(webhook)} successfully. {Global.SUCCESS_EMOJI}'
            )
            Global.LOGGER.info(pull_success_message)
            final_output = f'{webhook_output}\n{pull_success_message}'
            Utils.success(final_output, webhook)

    @staticmethod
    def open_project_config(webhook):
        """Open the project's config file to assign pipeline variables.

        Project configs look like the following:
        {
            "pipeline": "deploy",
            "prod_compose": true,
            "healthcheck": [
                "container_name_1",
                "container_name_2"
            ]
        }
        """
        try:
            # TODO: Long-term, turn `harvey.json` into a hidden file and make it yml: `.harvey.yml`
            filename = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook), 'harvey.json')
            with open(filename, 'r') as config_file:
                config = json.loads(config_file.read())
                Global.LOGGER.debug(json.dumps(config, indent=4))
            return config
        except FileNotFoundError:
            final_output = f'Harvey could not find a "harvey.json" file in {Global.repo_full_name(webhook)}.'
            Global.LOGGER.error(final_output)
            Utils.kill(final_output, webhook)

    def deploy(config, webhook, output):
        """Build Stage, used for `deploy` pipelines.

        This flow doesn't use the standard Docker API and instead runs `docker-compose` commands.
        """
        start_time = datetime.now()

        repo_path = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))
        # TODO: This is sad for `docker-compose.yaml` files containing an "a", allow for both
        default_compose_filepath = os.path.join(repo_path, 'docker-compose.yml')
        prod_compose_filepath = os.path.join(repo_path, 'docker-compose-prod.yml')

        try:
            if config.get('prod_compose'):
                # fmt: off
                compose_command = [
                    'docker-compose',
                    '-f', default_compose_filepath,
                    '-f', prod_compose_filepath,
                    'up', '-d',
                    '--build',
                ]
                # fmt: on
            else:
                # fmt: off
                compose_command = [
                    'docker-compose',
                    '-f', default_compose_filepath,
                    'up', '-d',
                    '--build'
                ]
                # fmt: on

            compose_output = subprocess.check_output(
                compose_command,
                stdin=None,
                stderr=None,
                timeout=Global.DEPLOY_TIMEOUT,
            )
            decoded_output = compose_output.decode('UTF-8')
            execution_time = f'Deploy stage execution time: {datetime.now() - start_time}'
            final_output = f'{decoded_output}\n{execution_time}'
            Global.LOGGER.info(final_output)
        except subprocess.TimeoutExpired:
            final_output = 'Harvey timed out deploying.'
            Global.LOGGER.error(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'{output}Harvey could not finish the deploy.'
            Global.LOGGER.error(final_output)
            Utils.kill(final_output, webhook)

        return final_output

import datetime
import json
import os
import subprocess  # nosec
from typing import (
    Any,
    Dict,
    Tuple,
)

import woodchips
import yaml

from harvey.config import Config
from harvey.containers import Container
from harvey.git import Git
from harvey.messages import Message
from harvey.repos.deployments import store_deployment_details
from harvey.repos.locks import (
    lookup_project_lock,
    update_project_lock,
)
from harvey.utils.deployments import (
    kill_deployment,
    succeed_deployment,
)
from harvey.webhooks import Webhook


class Deployment:
    @staticmethod
    def initialize_deployment(webhook: Dict[str, Any]) -> Tuple[Dict[str, Any], str, datetime.datetime]:
        """Initialize the setup for a deployment by cloning or pulling the project
        and setting up standard logging info.
        """
        logger = woodchips.get(Config.logger_name)

        try:
            # Kill the deployment if the project is locked
            if lookup_project_lock(Webhook.repo_full_name(webhook))['locked'] is True:
                kill_deployment(
                    (
                        f'{Webhook.repo_full_name(webhook)} deployments are locked. Please try again later or unlock'
                        ' deployments.'
                    ),
                    webhook,
                )
        except Exception:
            logger.error('Could not determine project lock status!')

        start_time = datetime.datetime.utcnow()

        _ = update_project_lock(
            project_name=Webhook.repo_full_name(webhook),
            locked=True,
            system_lock=True,
        )
        store_deployment_details(webhook)
        # Run git operation first to ensure the config is present and up-to-date
        git = Git.update_git_repo(webhook)

        webhook_data_key = webhook.get('data')
        if webhook_data_key:
            logger.debug(f'Pulling Harvey config for {Webhook.repo_full_name(webhook)} from webhook...')
            config = webhook_data_key
        else:
            logger.debug(f'Pulling Harvey config for {Webhook.repo_full_name(webhook)} from config file...')
            config = Deployment.open_project_config(webhook)

        deployment_type = config.get('deployment_type', Config.default_deployment)

        if deployment_type not in Config.supported_deployments:
            kill_deployment(
                message='Harvey could not run since there was no acceptable deployment specified.',
                webhook=webhook,
            )

        deployment_started_message = (
            f'{Message.work_emoji} Harvey has started a deployment ({deployment_type}) for'
            f' `{Webhook.repo_full_name(webhook)}`.'
        )
        if Config.use_slack:
            Message.send_slack_message(deployment_started_message)

        preamble = (
            f'Harvey v{Config.harvey_version} ({deployment_type.title()} Deployment)\n'
            f'Deployment Started: {start_time}\n'
            f'Deployment ID: {Webhook.repo_commit_id(webhook)}'
        )
        logger.info(preamble)

        configuration = f'Configuration:\n{json.dumps(config, indent=4)}' if Config.log_level == 'DEBUG' else ''
        commit_details = (
            f'New commit by: {Webhook.repo_commit_author(webhook)} to {Webhook.repo_full_name(webhook)}.\n'
            f'Commit Details: {Webhook.repo_commit_message(webhook)}'
        )
        git_output = git if Config.log_level == 'DEBUG' else ''
        execution_time = f'Startup execution time: {datetime.datetime.utcnow() - start_time}'

        output = f'{preamble}\n\n{configuration}\n\n{commit_details}\n\n{git_output}\n\n{execution_time}'
        logger.debug(f'{Webhook.repo_full_name(webhook)} {execution_time}')

        return config, output, start_time

    @staticmethod
    def run_deployment(webhook: Dict[str, Any]):
        """After receiving a webhook, spin up a deployment based on the config.
        If a Deployment fails, it fails early in the individual functions being called.
        """
        try:
            logger = woodchips.get(Config.logger_name)

            webhook_config, webhook_output, start_time = Deployment.initialize_deployment(webhook)
            deployment = webhook_config.get('deployment_type', Config.default_deployment).lower()

            if deployment == 'deploy':
                deploy_output = Deployment.deploy(webhook_config, webhook, webhook_output)

                healthcheck = webhook_config.get('healthcheck')
                healthcheck_messages = 'Healthchecks:\n'
                docker_client = Container.create_client()

                if healthcheck:
                    container_healthcheck_statuses = {}
                    for container in healthcheck:
                        container_healthcheck = Container.run_container_healthcheck(docker_client, container, webhook)
                        container_healthcheck_statuses[container] = container_healthcheck
                        if container_healthcheck is True:
                            healthcheck_message = f'\n{container} Healthcheck: {Message.success_emoji}'
                        else:
                            healthcheck_message = f'\n{container} Healthcheck: {Message.failure_emoji}'
                        healthcheck_messages += healthcheck_message

                    healthcheck_values = container_healthcheck_statuses.values()
                    all_healthchecks_passed = any(healthcheck_values) and list(healthcheck_values)[0] is True
                else:
                    all_healthchecks_passed = True  # Set to true here since we cannot determine, won't kill the deploy

                end_time = datetime.datetime.utcnow()
                execution_time = f'Deployment execution time: {end_time - start_time}'
                logger.debug(f'{Webhook.repo_full_name(webhook)} {execution_time}')
                final_output = f'{webhook_output}\n{deploy_output}\n{execution_time}\n{healthcheck_messages}\n'

                if all_healthchecks_passed or not healthcheck:
                    succeed_deployment(final_output, webhook)
                else:
                    kill_deployment(
                        message=final_output,
                        webhook=webhook,
                    )
            elif deployment == 'pull':
                # We simply assign the final message because if we got this far, the repo has already been pulled
                pull_success_message = (
                    f'Harvey pulled {Webhook.repo_full_name(webhook)} successfully. {Message.success_emoji}\n'
                )
                logger.info(pull_success_message)
                final_output = f'{webhook_output}\n{pull_success_message}'
                succeed_deployment(final_output, webhook)
            else:
                kill_deployment(f'deployment_type invalid, must be one of {Config.supported_deployments}', webhook)
        except Exception as error:
            # We wrap this entire block in a try/catch in an attempt to catch anything that bubbles to the
            # top before hitting sentry as this function is the top-level function called when a thread has
            # been spawned.
            kill_deployment(f'Deployment failed: {error}.', webhook)

    @staticmethod
    def open_project_config(webhook: Dict[str, Any]):
        """Open the project's config file to assign deployment variables.

        Project configs look like the following:
        {
            "deployment_type": "deploy",
            "prod_compose": true,
            "healthcheck": [
                "container_name_1",
                "container_name_2"
            ]
        }
        """
        logger = woodchips.get(Config.logger_name)

        try:
            yml_filepath = os.path.join(Config.projects_path, Webhook.repo_full_name(webhook), '.harvey.yml')
            yaml_filepath = os.path.join(Config.projects_path, Webhook.repo_full_name(webhook), '.harvey.yaml')

            if os.path.isfile(yml_filepath):
                filepath = yml_filepath
            elif os.path.isfile(yaml_filepath):
                filepath = yaml_filepath
            else:
                raise FileNotFoundError

            with open(filepath, 'r') as config_file:
                config = yaml.safe_load(config_file.read())
                logger.debug(json.dumps(config, indent=4))
            return config
        except FileNotFoundError:
            kill_deployment(
                message='Harvey could not find a ".harvey.yaml" file!',
                webhook=webhook,
            )

    @staticmethod
    def deploy(config: Dict[str, Any], webhook: Dict[str, Any], output: str) -> str:
        """Build Stage, used for `deploy` deployments.

        This flow doesn't use the Docker API but instead runs `docker compose` commands.
        """
        logger = woodchips.get(Config.logger_name)

        start_time = datetime.datetime.utcnow()

        repo_path = os.path.join(Config.projects_path, Webhook.repo_full_name(webhook))

        docker_compose_yml = 'docker-compose.yml'
        docker_compose_yaml = 'docker-compose.yaml'
        docker_compose_prod_yml = 'docker-compose-prod.yml'
        docker_compose_prod_yaml = 'docker-compose-prod.yaml'

        # Setup the `docker-compose.yml` file for all deployments based on file spelling
        if os.path.exists(os.path.join(repo_path, docker_compose_yml)):
            default_compose_filepath = os.path.join(repo_path, docker_compose_yml)
        elif os.path.exists(os.path.join(repo_path, docker_compose_yaml)):
            default_compose_filepath = os.path.join(repo_path, docker_compose_yaml)
        else:
            kill_deployment(
                message='Harvey could not find a "docker-compose.yaml" file!',
                webhook=webhook,
            )

        if config.get('prod_compose'):
            # If this is a prod deployment, setup the `docker-compose-prod.yml` file
            # in addition to the base `docker-compose.yml` file
            if os.path.exists(os.path.join(repo_path, docker_compose_prod_yml)):
                prod_compose_filepath = os.path.join(repo_path, docker_compose_prod_yml)
            elif os.path.exists(os.path.join(repo_path, docker_compose_prod_yaml)):
                prod_compose_filepath = os.path.join(repo_path, docker_compose_prod_yaml)
            else:
                kill_deployment(
                    message='Harvey could not find a "docker-compose-prod.yml" file!',
                    webhook=webhook,
                )

            # fmt: off
            compose_command = [
                'docker',
                'compose',
                '-f', default_compose_filepath,
                '-f', prod_compose_filepath,
                'up', '-d',
                '--build',
                '--force-recreate',
                '--quiet-pull',
            ]
            # fmt: on
        else:
            # fmt: off
            compose_command = [
                'docker',
                'compose',
                '-f', default_compose_filepath,
                'up', '-d',
                '--build',
                '--force-recreate',
                '--quiet-pull',
            ]
            # fmt: on

        try:
            compose_output = subprocess.check_output(  # nosec
                compose_command,
                stdin=None,
                stderr=None,
                timeout=Config.operation_timeout,
            )
            decoded_output = compose_output.decode('UTF-8')
            execution_time = f'Deploy stage execution time: {datetime.datetime.utcnow() - start_time}'
            final_output = f'{decoded_output}\n{execution_time}'
            logger.info(final_output)
        except subprocess.TimeoutExpired:
            final_output = 'Harvey timed out deploying!'
            kill_deployment(
                message=final_output,
                webhook=webhook,
            )
        except subprocess.CalledProcessError as error:
            final_output = f'{output}\nHarvey could not finish the deploy: {error}'
            kill_deployment(
                message=final_output,
                webhook=webhook,
                raise_error=True,
            )

        return final_output

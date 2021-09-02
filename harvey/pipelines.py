import json
import os
from datetime import datetime

from harvey.git import Git
from harvey.globals import Global
from harvey.messages import Message
from harvey.stages import Deploy
from harvey.utils import Utils

# TODO: We may now be able to consolidate the `pipeline` and `stage` namespaces and verbage


class Pipeline:
    @staticmethod
    def initialize_pipeline(webhook):
        """Initialize the setup for a pipeline by cloning/pulling the project
        and setting up standard logging info.
        """
        start_time = datetime.now()
        # Run git operation first to ensure the config is present and up-to-date
        git = Git.update_git_repo(webhook)
        config = Pipeline.open_project_config(webhook)

        if Global.SLACK:
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

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
        pipeline = webhook_config.get('pipeline').lower()

        if pipeline in Global.SUPPORTED_PIPELINES:
            if pipeline == 'pull':
                # We simply assign the final message because if we got this far, the repo has already been pulled
                final_output = f'{webhook_output}\nHarvey pulled the project successfully.'
            elif pipeline in ['deploy']:
                deploy_output, healthcheck = Pipeline.deploy(webhook_config, webhook, webhook_output)

                # TODO: Can this be cleaned up a bit (DRY)
                if healthcheck is False:
                    end_time = datetime.now()
                    pipeline_status = 'Pipeline failed due to a bad healthcheck.'
                    execution_time = f'Pipeline execution time: {end_time - start_time}'
                    healthcheck_message = f'Project passed healthcheck: {healthcheck}'

                    final_output = (
                        f'{webhook_output}\n{deploy_output}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}'
                    )

                    Utils.kill(final_output, webhook)
                else:
                    healthcheck_message = f'Project passed healthcheck: {healthcheck}'
                    end_time = datetime.now()
                    execution_time = f'Pipeline execution time: {end_time - start_time}'
                    pipeline_status = 'Pipeline succeeded!'

                    final_output = (
                        f'{webhook_output}\n{deploy_output}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}'
                    )

            Utils.success(final_output, webhook)
        else:
            # TODO: We may want to setup a default pipeline of `deploy` or `pull` if none is specified
            final_output = webhook_output + '\nError: Harvey could not run, there was no acceptable pipeline specified.'
            pipeline = Utils.kill(final_output, webhook)

    @staticmethod
    def open_project_config(webhook):
        """Open the project's config file to assign pipeline variables.

        Project configs look like the following:
        {
            "pipeline": "deploy",
            "compose": "some-name-compose.yml"
        }
        """
        # TODO: Add the ability to configure projects on the Harvey side
        # (eg: save values to a database via a UI) instead of only from
        # within a JSON file in the repo
        try:
            filename = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook), 'harvey.json')
            with open(filename, 'r') as config_file:
                config = json.loads(config_file.read())
                print(json.dumps(config, indent=4))
            return config
        except FileNotFoundError:
            final_output = f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

    @staticmethod
    def deploy(config, webhook, output):
        """Deploy a docker container via its `docker-compose.yml` file."""
        deploy = Deploy.run(config, webhook, output)
        healthcheck = Deploy.run_container_healthcheck(webhook)

        return deploy, healthcheck

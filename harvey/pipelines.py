import json
import os
from datetime import datetime

from harvey.git import Git
from harvey.globals import Global
from harvey.messages import Message
from harvey.stages import BuildStage, DeployComposeStage, DeployStage, TestStage
from harvey.utils import Utils

SLACK = os.getenv('SLACK')


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

        if SLACK:
            Message.send_slack_message(
                f'Harvey has started a `{config["pipeline"]}` pipeline for `{Global.repo_full_name(webhook)}`.'
            )

        preamble = (
            f'Running Harvey v{Global.HARVEY_VERSION}\n{config["pipeline"].title()} Pipeline Started: {start_time}'
        )
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}'
        print(preamble)
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
        print(execution_time)

        return config, output, start_time

    @staticmethod
    def start_pipeline(webhook, use_compose=False):
        """After receiving a webhook, spin up a pipeline based on the config.
        If a Pipeline fails, it fails early in the individual functions being called.
        """
        webhook_config, webhook_output, start_time = Pipeline.initialize_pipeline(webhook)
        pipeline = webhook_config.get('pipeline').lower()

        if pipeline in Global.SUPPORTED_PIPELINES:
            if pipeline == 'pull':
                final_output = f'{webhook_output}\nHarvey pulled the project successfully.'
            if pipeline in ['test', 'full']:
                test = Pipeline.test(webhook_config, webhook, webhook_output, start_time)

                end_time = datetime.now()
                execution_time = f'Pipeline execution time: {end_time - start_time}'
                pipeline_status = 'Pipeline succeeded!'

                final_output = f'{webhook_output}\n{test}\n{execution_time}\n{pipeline_status}'
            if pipeline in ['deploy', 'full']:
                build, deploy, healthcheck = Pipeline.deploy(
                    webhook_config, webhook, webhook_output, start_time, use_compose
                )

                stage_output = build + '\n' + deploy
                healthcheck_message = f'Project passed healthcheck: {healthcheck}'
                end_time = datetime.now()
                execution_time = f'Pipeline execution time: {end_time - start_time}'
                pipeline_status = 'Pipeline succeeded!'

                final_output = (
                    f'{webhook_output}\n{stage_output}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}'
                )

            Utils.success(final_output, webhook)
        else:
            final_output = webhook_output + '\nError: Harvey could not run, there was no acceptable pipeline specified.'
            pipeline = Utils.kill(final_output, webhook)

        return final_output

    @staticmethod
    def open_project_config(webhook):
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
            filename = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook), 'harvey.json')
            with open(filename, 'r') as file:
                config = json.loads(file.read())
                print(json.dumps(config, indent=4))
            return config
        except FileNotFoundError:
            final_output = f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

    @staticmethod
    def test(config, webhook, output, start_time):
        """Run the test stage in a pipeline"""
        test = TestStage.run(config, webhook, output)
        if 'Error: the above command exited with code' in test:
            # TODO: Ensure this works, it may be broken
            end_time = datetime.now()
            pipeline_status = 'Pipeline failed!'
            execution_time = f'Pipeline execution time: {end_time - start_time}'
            final_output = f'{output}\n{test}\n{execution_time}\n{pipeline_status}'
            Utils.kill(final_output, webhook)

        return test

    @staticmethod
    def deploy(config, webhook, output, start_time, use_compose):
        """Run the build and deploy stages in a pipeline."""
        if use_compose:
            build = ''  # When using compose, there is no build step
            deploy = DeployComposeStage.run(config, webhook, output)
            # healthcheck = Stage.run_container_healthcheck(webhook)  # TODO: Correct healthchecks for compose
            healthcheck = True
        else:
            build = BuildStage.run(config, webhook, output)
            deploy = DeployStage.run(webhook, output)
            healthcheck = DeployStage.run_container_healthcheck(webhook)

        if healthcheck is False:
            end_time = datetime.now()
            pipeline_status = 'Pipeline failed due to a bad healthcheck.'
            execution_time = f'Pipeline execution time: {end_time - start_time}'
            healthcheck_message = f'Project passed healthcheck: {healthcheck}'
            final_output = f'{output}\n{build}\n{deploy}\n{execution_time}\n{healthcheck_message}\n{pipeline_status}'
            Utils.kill(final_output, webhook)

        return build, deploy, healthcheck

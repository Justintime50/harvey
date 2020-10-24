import json
import os
from datetime import datetime
from harvey.pipeline import Pipeline
from harvey.git import Git
from harvey.globals import Global
from harvey.utils import Utils


class Webhook():
    @classmethod
    def init(cls, webhook):
        """Initiate the logic for webhooks and pull the project
        """
        start_time = datetime.now()
        preamble = f'Running Harvey v{Global.HARVEY_VERSION}\n' + \
            f'Pipeline Started: {start_time}'
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}\n'
        print(preamble)
        git_message = (f'New commit by: {Global.repo_commit_author(webhook)}. \
            \nCommit made on repo: {Global.repo_full_name(webhook)}.')
        git = Git.update_git_repo(webhook)

        # Open the project's config file to assign pipeline variables
        try:
            filename = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook),
                                    'harvey.json')
            with open(filename, 'r') as file:
                config = json.loads(file.read())
                print(json.dumps(config, indent=4))
        except FileNotFoundError as fnf_error:
            final_output = f'Error: Harvey could not find "harvey.json" file in \
                {Global.repo_full_name(webhook)}.'
            print(fnf_error)
            Utils.kill(final_output, webhook)

        execution_time = f'Startup execution time: {datetime.now() - start_time}\n'
        output = f'{preamble}\n{pipeline_id}Configuration:\n{json.dumps(config, indent=4)}' + \
            f'\n\n{git_message}\n{git}\n{execution_time}'
        print(execution_time)

        return config, output

    @classmethod
    def receive(cls, webhook):
        """Receive a webhook and spin up a pipeline based on the config
        """
        webhook_config, webhook_output = Webhook.init(webhook)

        if webhook_config['pipeline'] == 'test':
            pipeline = Pipeline.test(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'deploy':
            pipeline = Pipeline.deploy(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'full':
            pipeline = Pipeline.full(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'pull':
            pipeline = Utils.success(webhook_output, webhook)
        elif not webhook_config['pipeline']:
            final_output = webhook_output + '\nError: Harvey could not run, \
                there was no pipeline specified.'
            Utils.kill(final_output, webhook)

        return pipeline

    @classmethod
    def compose(cls, webhook):
        """Receive a webhook and spin up a pipeline based on the config
        """
        webhook_config, webhook_output = Webhook.init(webhook)

        if webhook_config['pipeline'] == 'test':
            pipeline = Pipeline.test(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'deploy':
            pipeline = Pipeline.deploy_compose(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'full':
            pipeline = Pipeline.full_compose(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'pull':
            pipeline = Utils.success(webhook_output, webhook)
        elif not webhook_config['pipeline']:
            final_output = webhook_output + '\nError: Harvey could not run, \
                there was no pipeline specified.'
            Utils.kill(final_output, webhook)

        return pipeline

"""Import webhook modules"""
# pylint: disable=R0903
import json
import os
from datetime import datetime
from .pipeline import Pipeline
from .git import Git
from .globals import Global
from .utils import Utils

class Webhook():
    """Webhook methods"""
    @classmethod
    def init(cls, webhook):
        """Initiate everything needed for a webhook function"""
        start_time = datetime.now()
        preamble = f'Running Harvey v{Global.HARVEY_VERSION}\n' + \
            f'Pipeline Started: {start_time}'
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}\n'
        print(preamble)
        git_message = (f'New commit by: {Global.repo_commit_author(webhook)}. \
            \nCommit made on repo: {Global.repo_full_name(webhook)}.')
        git = Git.pull(webhook)

        # Open the project's config file to assign pipeline variables
        try:
            filename = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook), \
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
        """Receive a webhook and pull in changes from GitHub"""
        init = Webhook.init(webhook)

        # Start a pipeline based on configuration
        if init[0]['pipeline'] == 'test':
            pipeline = Pipeline.test(init[0], webhook, init[1])
        elif init[0]['pipeline'] == 'deploy':
            pipeline = Pipeline.deploy(init[0], webhook, init[1])
        elif init[0]['pipeline'] == 'full':
            pipeline = Pipeline.full(init[0], webhook, init[1])
        elif not init[0]['pipeline']:
            final_output = init[1] + '\nError: Harvey could not run, \
                there was no pipeline specified.'
            Utils.kill(final_output, webhook)

        return pipeline

    @classmethod
    def compose(cls, webhook):
        """Receive a webhook and pull in changes from GitHub"""
        init = Webhook.init(webhook)

        # Start a pipeline based on configuration
        if init[0]['pipeline'] == 'test':
            pipeline = Pipeline.test(init[0], webhook, init[1])
        elif init[0]['pipeline'] == 'deploy':
            pipeline = Pipeline.deploy_compose(init[0], webhook, init[1])
        elif init[0]['pipeline'] == 'full':
            pipeline = Pipeline.full_compose(init[0], webhook, init[1])
        elif not init[0]['pipeline']:
            final_output = init[1] + '\nError: Harvey could not run, \
                there was no pipeline specified.'
            Utils.kill(final_output, webhook)

        return pipeline

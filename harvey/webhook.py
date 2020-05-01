"""Import webhook modules"""
# pylint: disable=R0903
import json
import os
from datetime import datetime
from .pipeline import Pipeline
from .git import Git
from .globals import Global
from .utils import Utils

class Webhook(Global):
    """Webhook methods"""
    @classmethod
    def init(cls, webhook):
        repo_name = webhook["repository"]["name"].lower()
        full_name = webhook["repository"]["full_name"].lower()
        preamble = f'Running Harvey v{Global.HARVEY_VERSION}\n{datetime.now()}\n'
        print(preamble)
        git_message = (f'New commit by: {webhook["commits"][0]["author"]["name"]} \
            \nCommit made on repo: {repo_name}')
        git = Git.pull(webhook)

        # Open the project's config file to assign pipeline variables
        filename = os.path.join(Global.PROJECTS_PATH, full_name, 'harvey.json')
        with open(filename, 'rb') as file:
            config = json.loads(file.read())
            print(config)

        output = f'{preamble}\nConfiguration:\n{config}\n{git_message}\n{git}\n'
        
        return config, output

    @classmethod
    def receive(cls, webhook):
        """Receive a webhook and pull in changes from GitHub"""
        init = Webhook.init(webhook)

        # Start a pipeline based on configuration
        if init[0]["pipeline"] == 'test':
            pipeline = Pipeline.test(init[0], webhook, init[1])
        elif init[0]["pipeline"] == 'deploy':
            pipeline = Pipeline.deploy(init[0], webhook, init[1])
        elif init[0]["pipeline"] == 'full':
            pipeline = Pipeline.full(init[0], webhook, init[1])
        elif not init[0]["pipeline"]:
            final_output = init[1] + '\nError: Harvey could not run, there was no pipeline specified'
            Utils.kill(final_output)

        return pipeline

    @classmethod
    def compose(cls, webhook):
        """Receive a webhook and pull in changes from GitHub"""
        init = Webhook.init(webhook)

        # Start a pipeline based on configuration
        if init[0]["pipeline"] == 'test':
            pipeline = Pipeline.test(init[0], webhook, init[1])
        elif init[0]["pipeline"] == 'deploy':
            pipeline = Pipeline.deploy_compose(init[0], webhook, init[1])
        elif init[0]["pipeline"] == 'full':
            pipeline = Pipeline.full_compose(init[0], webhook, init[1])
        elif not init[0]["pipeline"]:
            final_output = init[1] + '\nError: Harvey could not run, there was no pipeline specified'
            Utils.kill(final_output)

        return pipeline

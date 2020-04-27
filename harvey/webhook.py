"""Import webhook modules"""
# pylint: disable=R0903
import json
import sys
from .pipeline import Pipeline
from .git import Git
from .globals import Global

class Webhook(Global):
    """Webhook methods"""
    @classmethod
    def receive(cls, webhook):
        """Receive a webhook and pull in changes from GitHub"""
        repo_name = webhook["repository"]["name"].lower()
        full_name = webhook["repository"]["full_name"].lower()
        print(f'New commit by: {webhook["commits"][0]["author"]["name"]} \
            \nCommit made on repo: {repo_name}')
        Git.pull(webhook)

        # Open the project's config file to assign pipeline variables
        with open(f'{Global.PROJECTS_PATH}{full_name}/harvey.json', 'r') as file:
            config = json.loads(file.read())
            print(config)

        # Start a pipeline based on configuration
        if config["pipeline"] == 'test':
            pipeline = Pipeline.test(config, webhook)
        elif config["pipeline"] == 'deploy':
            pipeline = Pipeline.deploy(config, webhook)
        elif config["pipeline"] == 'full':
            pipeline = Pipeline.full(config, webhook)
        elif not config["pipeline"]:
            sys.exit("Error: Harvey could not run, there was no pipeline specified")

        return pipeline

    @classmethod
    def compose(cls, webhook):
        """Receive a webhook and pull in changes from GitHub"""
        repo_name = webhook["repository"]["name"].lower()
        full_name = webhook["repository"]["full_name"].lower()
        print(f'New commit by: {webhook["commits"][0]["author"]["name"]} \
            \nCommit made on repo: {repo_name}')
        Git.pull(webhook)

        # Open the project's config file to assign pipeline variables
        with open(f'{Global.PROJECTS_PATH}{full_name}/harvey.json', 'r') as file:
            config = json.loads(file.read())
            print(config)

        # Start a pipeline based on configuration
        if config["pipeline"] == 'test':
            pipeline = Pipeline.test(config, webhook)
        elif config["pipeline"] == 'deploy':
            pipeline = Pipeline.deploy_compose(config, webhook)
        elif config["pipeline"] == 'full':
            pipeline = Pipeline.full_compose(config, webhook)
        elif not config["pipeline"]:
            sys.exit("Error: Harvey could not run, there was no pipeline specified")

        return pipeline

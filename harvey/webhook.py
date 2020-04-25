from flask import request
import json
import os
import sys
from .pipeline import Pipeline
from .git import Git

class Webhook():
    @classmethod
    def receive(cls, webhook):
        # Receive a webhook and pull in changes from GitHub
        print(f'New commit by: {webhook["commits"][0]["author"]["name"]}\nCommit made on repo: {webhook["repository"]["name"]}')
        Git.pull(webhook)

        # Open the project's config file to assign pipeline variables
        with open(f'docker/projects/{webhook["repository"]["full_name"].lower()}/.harvey', 'r') as file:
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

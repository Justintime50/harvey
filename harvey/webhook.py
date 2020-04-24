from flask import request
import json
import os
import sys
from .pipeline import Pipeline
from .git import Git

class Webhook():
    @classmethod
    def receive(cls, data):
        # Receive a webhook
        print(f"New commit by: {data['commits'][0]['author']['name']}")
        Git.pull(data)

        # Open config file
        with open(f'docker/projects/{data["repository"]["name"]}/.harvey', 'r') as file:
            config = json.loads(file.read())
            print(config)

        # Start a pipeline based on configuration
        if config["pipeline"] == 'test':
            pipeline = Pipeline.test(config["data"])
        elif config["pipeline"] == 'deploy':
            pipeline = Pipeline.deploy(config["data"], config["tag"])
        elif config["pipeline"] == 'full':
            pipeline = Pipeline.full(config["data"], config["tag"])
        elif not config["pipeline"]:
            sys.exit("Error: Harvey could not run, there was no pipeline specified")

        return pipeline

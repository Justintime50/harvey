from flask import request
import json
import os
import imp
import sys
from .pipeline import Pipeline
from .git import Git

class Webhook():
    @classmethod
    def receive(cls, data):
        # Receive a webhook
        # TODO: Fix receiving webhooks
        print(f"New commit by: {data['commits'][0]['author']['name']}")
        Git.pull(data)

        # # Config file
        f = open(f'docker/projects/{data["name"]}/.harvey.txt')
        CONFIG = imp.load_source('CONFIG', '', f)
        f.close()

        # # path to "config" file
        # print(CONFIG.pipeline)
        # print(CONFIG.tag)
        # print(CONFIG.data["version"])

        # sys.exit("Done")

        # data = open('./harvey/build.json', 'rb').read()
        # Pipeline.full(data)

        return data

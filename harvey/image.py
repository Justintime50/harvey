"""Import image modules"""
# pylint: disable=W0511
import json
import uuid
import os
import requests
import requests_unixsocket
from .client import Client

requests_unixsocket.monkeypatch() # allows us to use requests_unixsocker via requests

class Image(Client):
    """Docker image methods"""
    @classmethod
    def build(cls, config, webhook, context=''):
        """Build a Docker image"""
        full_name = webhook["repository"]["full_name"].lower()
        repo_name = webhook["repository"]["name"].lower()
        owner_name = webhook["repository"]["owner"]["name"].lower()
        # TODO: Use the Docker API for building instead of a shell \
            # command (haven't because I can't get it working)
        # tar = open('./docker/pullbug.tar.gz', encoding="latin-1").read()
        # json = open('./harvey/build.json', 'rb').read()
        # data = requests.post(Client.BASE_URL + 'build', \
        # params=json, data=tar, headers=Client.TAR_HEADERS)

        # Global variables
        if "dockerfile" in config:
            dockerfile = f'-f {config["dockerfile"]}'
        else:
            dockerfile = ''
        # if "tag" in config:
        #     tag = f'-t {config["tag"]}'
        # else:
        #     tag = ''

        # Set variables based on the context (test vs deploy vs full)
        if context == 'test':
            project = f'--build-arg PROJECT={full_name}'
            context = ''
            tag = uuid.uuid4().hex
            tag_arg = f'-t {tag}'
        else:
            project = ''
            context = f'/projects/{full_name}'
            tag = f'{owner_name}-{repo_name}'
            tag_arg = f'-t {tag}'

        # For testing only:
        if "language" in config:
            language = f'--build-arg LANGUAGE={config["language"]}'
        else:
            language = ''
        if "version" in config:
            version = f'--build-arg VERSION={config["version"]}'
        else:
            version = ''

        # Build the image and stream the output
        stream = os.popen(f'cd docker{context} && docker build {dockerfile} \
            {tag_arg} {language} {version} {project} .')
        output = stream.read() # TODO: Make this stream live output
        print(output)
        return tag

    @classmethod
    def retrieve(cls, image_id):
        """Retrieve a Docker image"""
        data = requests.get(Client.BASE_URL + f'images/{image_id}/json')
        return data.json()

    @classmethod
    def all(cls):
        """Retrieve all Docker images"""
        data = requests.get(Client.BASE_URL + f'images/json')
        return data.json()

    @classmethod
    def remove(cls, image_id):
        """Remove (delete) a Docker image"""
        data = requests.delete(Client.BASE_URL + f'images/{image_id}', \
            data=json.dumps({'force': True}), headers=Client.JSON_HEADERS)
        return data

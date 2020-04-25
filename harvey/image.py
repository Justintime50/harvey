import requests
import json
import uuid
import requests_unixsocket
from .client import Client
import os

requests_unixsocket.monkeypatch() # allows us to use requests_unixsocker via requests

class Image(Client):
    @classmethod
    def build(cls, config, webhook, context=''):
        # TODO: Use the Docker API for building instead of a shell command (haven't because I can't get it working)
        # tar = open('./docker/pullbug.tar.gz', encoding="latin-1").read()
        # json = open('./harvey/build.json', 'rb').read()
        # data = requests.post(Client.BASE_URL + 'build', params=json, data=tar, headers=Client.TAR_HEADERS)
        
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
            project = f'--build-arg PROJECT={webhook["repository"]["full_name"].lower()}'
            context = ''
            tag = uuid.uuid4().hex
            tag_arg = f'-t {tag}'
        else:
            project = ''
            context = f'/projects/{webhook["repository"]["full_name"].lower()}'
            tag = f'{webhook["repository"]["owner"]["name"].lower()}-{webhook["repository"]["name"].lower()}'
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
        stream = os.popen(f'cd docker{context} && docker build --no-cache {dockerfile} {tag_arg} {language} {version} {project} .')
        output = stream.read() # TODO: Make this stream live output
        print(output)
        return tag

    @classmethod
    def retrieve(cls, id):
        data = requests.get(Client.BASE_URL + f'images/{id}/json')
        return data.json()

    @classmethod
    def all(cls):
        data = requests.get(Client.BASE_URL + f'images/json')
        return data.json()

    @classmethod
    def remove(cls, id):
        data = requests.delete(Client.BASE_URL + f'images/{id}', data=json.dumps({'force': True}), headers=Client.JSON_HEADERS)
        return data

import requests
import json
import requests_unixsocket
from .client import Client
import os

requests_unixsocket.monkeypatch() # allows us to use requests_unixsocker via requests

class Image(Client):
    @classmethod
    def build(cls, data, tag='latest-build', context=''):
        # TODO: Use the Docker API for building instead of a shell command (haven't because I can't get it working)
        # tar = open('./docker/pullbug.tar.gz', encoding="latin-1").read()
        # json = open('./harvey/build.json', 'rb').read()
        # data = requests.post(Client.BASE_URL + 'build', params=json, data=tar, headers=Client.TAR_HEADERS)
        
        # Global variables
        if "dockerfile" in data:
            dockerfile = f'-f {data["dockerfile"]}'
        else:
            dockerfile = ''
        if tag:
            tag = f'-t {tag}'
        else:
            tag = ''

        # Project is required to know how to build and in what context (test vs deploy)
        if "project" in data and context == 'test':
            project = f'--build-arg PROJECT={data["project"]}'
            context = ''
        elif "project" in data and context != 'test':
            project = ''
            context = f'/projects/{data["project"]}'

        # For testing only:
        if "language" in data:
            language = f'--build-arg LANGUAGE={data["language"]}'
        else:
            language = ''
        if "version" in data:
            version = f'--build-arg VERSION={data["version"]}'
        else:
            version = ''

        # Build the image and stream the output
        stream = os.popen(f'cd docker{context} && docker build --no-cache {dockerfile} {tag} {language} {version} {project} .')
        output = stream.read() # TODO: Make this stream live output
        return output

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

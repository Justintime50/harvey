"""Import image modules"""
# pylint: disable=W0511
import json
import uuid
import os
import subprocess
import requests
import requests_unixsocket
from .globals import Global

requests_unixsocket.monkeypatch() # allows us to use requests_unixsocker via requests

class Image():
    """Docker image methods"""
    @classmethod
    def build(cls, config, webhook, context=''):
        """Build a Docker image"""
        # TODO: Use the Docker API for building instead of a shell \
            # command (haven't because I can't get it working)
        # tar = open('./docker/pullbug.tar.gz', encoding="latin-1").read()
        # json = open('./harvey/build.json', 'rb').read()
        # data = requests.post(Global.BASE_URL + 'build', \
        # params=json, data=tar, headers=Global.TAR_HEADERS)

        # Global variables
        if "dockerfile" in config:
            dockerfile = f'-f {config["dockerfile"]}'
        else:
            dockerfile = ''

        # Set variables based on the context (test vs deploy vs full)
        if context == 'test':
            project = f'--build-arg PROJECT={Global.repo_full_name(webhook)}'
            path = Global.PROJECTS_PATH
            tag = uuid.uuid4().hex
        else:
            project = ''
            path = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))
            tag = f'{Global.repo_owner_name(webhook)}-{Global.repo_name(webhook)}'

        tag_arg = f'-t {tag}'

        # For testing only:
        if "language" in config and context == 'test':
            language = f'--build-arg LANGUAGE={config["language"]}'
        else:
            language = ''
        if "version" in config and context == 'test':
            version = f'--build-arg VERSION={config["version"]}'
        else:
            version = ''

        # Build the image (exceptions handled at stage level)
        image = subprocess.check_call(f'cd {path} && docker build \
            {dockerfile} {tag_arg} {language} {version} {project} .', \
            stdin=None, stdout=None, stderr=None, shell=True, timeout=1800)

        return tag, image

    @classmethod
    def retrieve(cls, image_id):
        """Retrieve a Docker image"""
        data = requests.get(Global.BASE_URL + f'images/{image_id}/json')
        return data.json()

    @classmethod
    def all(cls):
        """Retrieve all Docker images"""
        data = requests.get(Global.BASE_URL + 'images/json')
        return data.json()

    @classmethod
    def remove(cls, image_id):
        """Remove (delete) a Docker image"""
        data = requests.delete(Global.BASE_URL + f'images/{image_id}', \
            data=json.dumps({'force': True}), headers=Global.JSON_HEADERS)
        return data

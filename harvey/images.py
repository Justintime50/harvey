import os
import subprocess

import requests

from harvey.globals import Global


class Image():
    @classmethod
    def build_image(cls, config, webhook, context=''):
        """Build a Docker image by shelling out and running Docker commands.
        """
        # TODO: Use the Docker API for building instead of a shell \
        # command (haven't because I can't get it working)
        # tar = open('./docker/pullbug.tar.gz', encoding="latin-1").read()
        # json = open('./harvey/build.json', 'rb').read()
        # data = requests.post(Global.BASE_URL + 'build', \
        # params=json, data=tar, headers=Global.TAR_HEADERS)

        # Set variables based on the context (test vs deploy vs full)
        if context == 'test':
            language = f'--build-arg LANGUAGE={config.get("language", "")}'
            version = f'--build-arg VERSION={config.get("version", "")}'
            project = f'--build-arg PROJECT={Global.repo_full_name(webhook)}'
            path = f'{Global.PROJECTS_PATH}'
        else:
            language = ''
            version = ''
            project = ''
            path = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))
        dockerfile = f'-f {config["dockerfile"]}' if config.get("dockerfile") else ''
        tag_arg = f'-t {Global.docker_project_name(webhook)}'

        # Build the image (exceptions bubble up to the stage module)
        # We cd into the directory here so we have access to the files to copy into the container
        image = subprocess.check_output(
            f'cd {path} && docker build {dockerfile} {tag_arg} {language} {version} {project} .',
            stdin=None,
            stderr=None,
            shell=True,
            timeout=Global.BUILD_TIMEOUT
        )

        return image.decode('UTF-8')

    @classmethod
    def retrieve_image(cls, image_id):
        """Retrieve a Docker image
        """
        response = requests.get(Global.BASE_URL + f'images/{image_id}/json')
        return response

    @classmethod
    def retrieve_all_images(cls):
        """Retrieve all Docker images
        """
        response = requests.get(Global.BASE_URL + 'images/json')
        return response

    @classmethod
    def remove_image(cls, image_id):
        """Remove (delete) a Docker image
        """
        response = requests.delete(
            Global.BASE_URL + f'images/{image_id}',
            json={'force': True},
            headers=Global.JSON_HEADERS
        )
        return response

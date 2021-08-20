import os
import subprocess

import requests
import docker

from harvey.globals import Global


class Image:
    @staticmethod
    def build_image(config, webhook, context=""):
        """Build a Docker image by shelling out and running Docker commands."""
        # tar = open('./docker/pullbug.tar.gz', encoding="latin-1").read()
        # json = open('./harvey/build.json', 'rb').read()
        # data = requests.post(Global.BASE_URL + 'build', \
        # params=json, data=tar, headers=Global.TAR_HEADERS)

        # Set variables based on the context (test vs deploy vs full)
        if context == "test":
            language = config.get("language", "")
            version = config.get("version", "")
            project = Global.repo_full_name(webhook)
            path = Global.PROJECTS_PATH
        else:
            language = ""
            version = ""
            project = ""
            path = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))
        dockerfile = config["dockerfile"] if config.get("dockerfile") else ""
        tag_arg = Global.docker_project_name(webhook)

        # Build the image (exceptions bubble up to the stage module)
        client = docker.from_env()
        image = client.images.build(
            path=path,
            tag=tag_arg,
            buildargs={
                "LANGUAGE": language,
                "VERSION": version,
                "PROJECT": project,
            },
        )

        # Returns TAG of image
        return image.tags[0]

    @staticmethod
    def retrieve_image(image_id):
        """Retrieve a Docker image."""
        response = requests.get(Global.BASE_URL + f"images/{image_id}/json")
        return response

    @staticmethod
    def retrieve_all_images():
        """Retrieve all Docker images"""
        response = requests.get(Global.BASE_URL + "images/json")
        return response

    @staticmethod
    def remove_image(image_id):
        """Remove (delete) a Docker image."""
        response = requests.delete(
            Global.BASE_URL + f"images/{image_id}",
            json={
                "force": True,
            },
            headers=Global.JSON_HEADERS,
        )
        return response

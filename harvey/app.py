import json
import os
import time

import requests_unixsocket
from dotenv import load_dotenv
from flask import Flask, abort, request

from harvey.globals import Global
from harvey.webhook import Webhook

load_dotenv()
API = Flask(__name__)
HOST = os.getenv('HOST', '127.0.0.1')
PORT = os.getenv('PORT', '5000')
DEBUG = os.getenv('DEBUG', 'True')

# TODO: Add authentication to each endpoint


@API.route('/pipelines/start', methods=['POST'])
def start_pipeline():
    """Start a pipeline based on webhook data
    """
    return Webhook.parse_webhook(request=request, use_compose=False)


# @API.route('/pipelines/stop', methods=['POST'])
# def stop_pipeline():
#     # TODO: Add this endpoint


@API.route('/pipelines/start/compose', methods=['POST'])
def start_pipeline_compose():
    """Start a pipeline based on webhook data
    But build from compose file.
    """
    return Webhook.parse_webhook(request=request, use_compose=True)


# @API.route('/pipelines/stop/compose', methods=['POST'])
# def stop_pipeline_compose():
#     # TODO: Add this endpoint


@API.route('/pipelines/<pipeline_id>', methods=['GET'])
def retrieve_pipeline(pipeline_id):
    """Retrieve a pipeline's logs by ID
    """
    # TODO: This is a hacky temporary solution until we can
    # store this data in a database and is not meant to remain
    # as a long-term solution
    file = f'{pipeline_id}.log'
    for root, dirs, files in os.walk(Global.PROJECTS_LOG_PATH):
        if file in files:
            with open(os.path.join(root, file), 'r') as output:
                response = output.read()
            return response
    return abort(404)


@API.route('/pipelines', methods=['GET'])
def retrieve_pipelines():
    """Retrieve a list of pipelines
    """
    # TODO: This is a hacky temporary solution until we can
    # store this data in a database and is not meant to remain
    # as a long-term solution
    pipelines = {'pipelines': []}
    for root, dirs, files in os.walk(Global.PROJECTS_LOG_PATH, topdown=True):
        for file in files:
            timestamp = time.ctime(os.path.getmtime(os.path.join(root, file)))
            pipelines['pipelines'].append(
                f'{timestamp}: {os.path.join(root, file)}')
    return json.dumps(pipelines, indent=4)


# @API.route('/containers/<container_id>/healthcheck', methods=['GET'])
# def container_healthcheck():
#     # TODO: Add this endpoint


# @API.route('/containers/create', methods=['POST'])
# def create_container():
#     """Create a Docker container"""
#     tag = request.tag
#     response = json.dumps(harvey.Container.create_container(tag))
#     return response


# @API.route('/containers/<container_id>/start', methods=['POST'])
# def start_container(container_id):
#     """Start a Docker container"""
#     start = harvey.Container.start_container(container_id)
#     response = str(start)
#     return response


# @API.route('/containers/<container_id>/stop', methods=['POST'])
# def stop_container(container_id):
#     """Stop a Docker container"""
#     stop = harvey.Container.stop_container(container_id)
#     response = str(stop)
#     return response


# @API.route('/containers/<container_id>', methods=['GET'])
# def inspect_container(container_id):
#     """Retrieve a Docker container"""
#     response = json.dumps(harvey.Container.inspect_container(container_id))
#     return response


# @API.route('/containers', methods=['GET'])
# def all_containers():
#     """Retrieve all Docker containers"""
#     response = json.dumps(harvey.Container.list_containers())
#     return response


# @API.route('/containers/<container_id>/logs', methods=['GET'])
# def logs_container(container_id):
#     """Retrieve logs from a Docker container"""
#     response = str(harvey.Container.inspect_container_logs(container_id))
#     return response


# @API.route('/containers/<container_id>/wait', methods=['POST'])
# def wait_container(container_id):
#     """Wait for a Docker container to exit"""
#     response = json.dumps(harvey.Container.wait_container(container_id))
#     return response


# @API.route('/containers/<container_id>/remove', methods=['DELETE'])
# def remove_container(container_id):
#     """Remove (delete) a Docker container"""
#     remove = harvey.Container.remove_container(container_id)
#     response = str(remove)
#     return response


# @API.route('/build', methods=['POST'])
# def build_image():
#     """Build a Docker image"""
#     data = json.loads(request.data)
#     tag = json.loads(request.tag)
#     context = json.loads(request.context)
#     build = harvey.build_image(data, tag, context)
#     return build


# @API.route('/images/<image_id>', methods=['GET'])
# def retrieve_image(image_id):
#     """Retrieve a Docker image"""
#     response = json.dumps(harvey.Image.retrieve_image(image_id))
#     return response


# @API.route('/images', methods=['GET'])
# def all_images():
#     """Retrieve all Docker images"""
#     response = json.dumps(harvey.Image.retrieve_all_images())
#     return response


# @API.route('/images/<image_id>/remove', methods=['DELETE'])
# def remove_image(image_id):
#     """Remove (delete) a Docker image"""
#     remove = harvey.Image.remove_image(image_id)
#     response = str(remove)
#     return response


# @API.route('/pull', methods=['POST'])
# def pull_project():
#     """Pull/clone GitHub project"""
#     data = json.loads(request.data)
#     pull = harvey.Git.pull_repo(data)
#     response = str(pull)
#     return response


def main():
    # allows us to use requests_unixsocker via requests
    requests_unixsocket.monkeypatch()
    API.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == '__main__':
    main()

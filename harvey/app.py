import json
import os
import time
import hmac
import hashlib
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request, abort
from harvey.webhook import Webhook
from harvey.globals import Global

load_dotenv()
API = Flask(__name__)
HOST = os.getenv('HOST', '127.0.0.1')
PORT = os.getenv('PORT', '5000')
DEBUG = os.getenv('DEBUG', 'True')


# TODO: Move all of the logic out of this file and into Harvey itself
# This file should only route requests to the proper functions


@API.route('/harvey', methods=['POST'])
def receive_webhook():
    """Receive a Webhook - this is the entrypoint for Harvey"""
    target = Webhook.receive
    return webhook(target)


@API.route('/harvey/compose', methods=['POST'])
def receive_webhook_compose():
    """Receive a Webhook, build from compose file.
    This is the entrypoint for Harvey
    """
    target = Webhook.compose
    return webhook(target)


def webhook(target):
    """Initiate details to receive a webhook
    """
    data = request.data
    signature = request.headers.get('X-Hub-Signature')
    parsed_data = json.loads(data)
    if parsed_data['ref'] == 'refs/heads/master':
        if os.getenv('MODE') == 'test':
            Thread(target=target, args=(parsed_data,)).start()
            return "200"
        if decode_webhook(data, signature):
            Thread(target=target, args=(parsed_data,)).start()
            return "200"
        return abort(403)
    return abort(500, 'Harvey can only pull from the master branch.')


def decode_webhook(data, signature):
    """Decode a webhook's secret key
    """
    secret = bytes(os.getenv('WEBHOOK_SECRET'), 'UTF-8')
    mac = hmac.new(secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)


@API.route('/pipelines/<pipeline_id>', methods=['GET'])
def retrieve_pipeline(pipeline_id):
    """Retrieve a pipeline's logs by ID
    """
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
    # TODO: 1) Do not expose log paths here
    # TODO: 2) Replace this with retrieving from a DB instead
    pipelines = {'pipelines': []}
    for root, dirs, files in os.walk(Global.PROJECTS_LOG_PATH, topdown=True):
        for file in files:
            timestamp = time.ctime(os.path.getmtime(os.path.join(root, file)))
            pipelines['pipelines'].append(
                f'{timestamp}: {os.path.join(root, file)}')
    return json.dumps(pipelines, indent=4)


# @API.route('/containers/create', methods=['POST'])
# def create_container():
#     """Create a Docker container"""
#     tag = request.tag
#     response = json.dumps(harvey.Container.create(tag))
#     return response

# @API.route('/containers/<container_id>/start', methods=['POST'])
# def start_container(container_id):
#     """Start a Docker container"""
#     start = harvey.Container.start(container_id)
#     response = str(start)
#     return response

# @API.route('/containers/<container_id>/stop', methods=['POST'])
# def stop_container(container_id):
#     """Stop a Docker container"""
#     stop = harvey.Container.stop(container_id)
#     response = str(stop)
#     return response

# @API.route('/containers/<container_id>', methods=['GET'])
# def retrieve_container(container_id):
#     """Retrieve a Docker container"""
#     response = json.dumps(harvey.Container.retrieve(container_id))
#     return response

# @API.route('/containers', methods=['GET'])
# def all_containers():
#     """Retrieve all Docker containers"""
#     response = json.dumps(harvey.Container.all())
#     return response

# @API.route('/containers/<container_id>/logs', methods=['GET'])
# def logs_container(container_id):
#     """Retrieve logs from a Docker container"""
#     response = str(harvey.Container.logs(container_id))
#     return response

# @API.route('/containers/<container_id>/wait', methods=['POST'])
# def wait_container(container_id):
#     """Wait for a Docker container to exit"""
#     response = json.dumps(harvey.Container.wait(container_id))
#     return response

# @API.route('/containers/<container_id>/remove', methods=['DELETE'])
# def remove_container(container_id):
#     """Remove (delete) a Docker container"""
#     remove = harvey.Container.remove(container_id)
#     response = str(remove)
#     return response

# @API.route('/build', methods=['POST'])
# def build_image():
#     """Build a Docker image"""
#     data = json.loads(request.data)
#     tag = json.loads(request.tag)
#     context = json.loads(request.context)
#     build = harvey.Image.build(data, tag, context)
#     return build

# @API.route('/images/<image_id>', methods=['GET'])
# def retrieve_image(image_id):
#     """Retrieve a Docker image"""
#     response = json.dumps(harvey.Image.retrieve(image_id))
#     return response

# @API.route('/images', methods=['GET'])
# def all_images():
#     """Retrieve all Docker images"""
#     response = json.dumps(harvey.Image.all())
#     return response

# @API.route('/images/<image_id>/remove', methods=['DELETE'])
# def remove_image(image_id):
#     """Remove (delete) a Docker image"""
#     remove = harvey.Image.remove(image_id)
#     response = str(remove)
#     return response

# @API.route('/pull', methods=['POST'])
# def pull_project():
#     """Pull/clone GitHub project"""
#     data = json.loads(request.data)
#     pull = harvey.Git.pull(data)
#     response = str(pull)
#     return response


if __name__ == '__main__':
    API.run(host=HOST, port=PORT, debug=DEBUG)

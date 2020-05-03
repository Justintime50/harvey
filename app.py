"""Import API modules"""
# pylint: disable=W0511,W0612
from threading import Thread
import json
import os
import hmac
import hashlib
from flask import Flask, request, abort
import harvey

API = Flask(__name__)

@API.route('/harvey', methods=['POST'])
def receive_webhook():
    """Receive a Webhook - this is the entrypoint for Harvey"""
    target = harvey.Webhook.receive
    return webhook(target)

@API.route('/harvey/compose', methods=['POST'])
def receive_webhook_compose():
    """Receive a Webhook, build from compose file - this is the entrypoint for Harvey"""
    target = harvey.Webhook.compose
    return webhook(target)

def webhook(target):
    """Initiate details to receive a webhook"""
    data = request.data
    signature = request.headers.get('X-Hub-Signature')
    if os.getenv('MODE') == 'test':
        Thread(target=target, args=(json.loads(data),)).start()
        return "OK"
    if decode_webhook(data, signature):
        Thread(target=target, args=(json.loads(data),)).start()
        return "OK"
    return abort(403)

def decode_webhook(data, signature):
    """Decode a webhook's secret key"""
    secret = bytes(os.getenv('WEBHOOK_SECRET'), 'UTF-8')
    mac = hmac.new(secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)

@API.route('/pipeline/<pipeline_id>', methods=['GET'])
def retrieve_pipeline(pipeline_id):
    """Retrieve a pipeline's logs by ID"""
    file = f'{pipeline_id}.log'
    for root, dirs, files in os.walk(harvey.Global.PROJECTS_LOG_PATH):
        if file in files:
            with open(os.path.join(root, file), 'r') as output:
                response = output.read()
            return response
    return abort(404)

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
    API.run(host='0.0.0.0')

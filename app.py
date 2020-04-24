from flask import Flask, request
from threading import Thread
import json
import harvey

api = Flask(__name__)

"""Container Endpoints"""
@api.route('/containers/create', methods=['POST'])
def create_container():
    tag = request.tag
    response = json.dumps(harvey.Container.create(tag))
    return response
    
@api.route('/containers/<id>/start', methods=['POST'])
def start_container(id):
    start = harvey.Container.start(id)
    response = str(start)
    return response

@api.route('/containers/<id>/stop', methods=['POST'])
def stop_container(id):
    start = harvey.Container.stop(id)
    response = str(start)
    return response

@api.route('/containers/<id>', methods=['GET'])
def retrieve_container(id):
    response = json.dumps(harvey.Container.retrieve(id))
    return response

@api.route('/containers', methods=['GET'])
def all_containers():
    response = json.dumps(harvey.Container.all())
    return response

@api.route('/containers/<id>/logs', methods=['GET'])
def logs_container(id):
    response = str(harvey.Container.logs(id))
    return response

@api.route('/containers/<id>/wait', methods=['POST'])
def wait_container(id):
    response = json.dumps(harvey.Container.wait(id))
    return response

@api.route('/containers/<id>/remove', methods=['DELETE'])
def remove_container(id):
    remove = harvey.Container.remove(id)
    response = str(remove)
    return response

"""Image Endpoints"""
@api.route('/build', methods=['POST'])
def build_image():
    data = json.loads(request.data)
    tag = json.loads(request.tag)
    context = json.loads(request.context)

    build = harvey.Image.build(data, tag, context)
    return build

@api.route('/images/<id>', methods=['GET'])
def retrieve_image(id):
    response = json.dumps(harvey.Image.retrieve(id))
    return response

@api.route('/images', methods=['GET'])
def all_images():
    response = json.dumps(harvey.Image.all())
    return response

@api.route('/images/<id>/remove', methods=['DELETE'])
def remove_image(id):
    remove = harvey.Image.remove(id)
    response = str(remove)
    return response

"""Webhook Endpoints"""
@api.route('/harvey', methods=['POST'])
def receive_webhook():
    data = json.loads(request.data)
    # TODO: Ensure this is the best way to accomplish this
    Thread(target=harvey.Webhook.receive, args=(data,)).start()
    return "OK"

"""Git Endpoints"""
@api.route('/pull', methods=['POST'])
def pull_project():
    data = json.loads(request.data)
    pull = harvey.Git.pull(data)
    response = str(pull)
    return response

"""Pipeline Endpoints"""
@api.route('/pipeline/test', methods=['POST'])
def test_pipeline():
    data = json.loads(request.data)
    test = harvey.Pipeline.test(data)
    response = json.dumps(test)
    return response

@api.route('/pipeline/deploy', methods=['POST'])
def deploy_pipeline():
    data = json.loads(request.data)
    tag = json.loads(request.tag)
    deploy = harvey.Pipeline.deploy(data, tag)
    response = json.dumps(deploy)
    return response

@api.route('/pipeline/full', methods=['POST'])
def full_pipeline():
    data = json.loads(request.data)
    tag = json.loads(request.tag)
    full = harvey.Pipeline.full(data, tag)
    response = json.dumps(full)
    return response

if __name__ == '__main__':
    api.run()

from flask import Flask, request
import json
import harvey

api = Flask(__name__)

"""Container Endpoints"""
@api.route('/containers/create', methods=['POST'])
def create_container(tag):
    return harvey.Container.create(tag)
    
@api.route('/containers/<id>/start', methods=['POST'])
def start_container(id):
    return harvey.Container.start(id)

@api.route('/containers/<id>/stop', methods=['POST'])
def stop_container(id):
    return harvey.Container.stop(id)

@api.route('/containers/<id>', methods=['GET'])
def retrieve_container(id):
    return harvey.Container.retrieve(id)

@api.route('/containers', methods=['GET'])
def all_containers():
    return harvey.Container.all()

@api.route('/containers/<id>/logs', methods=['GET'])
def logs_container(id):
    return harvey.Container.logs(id)

@api.route('/containers/<id>/wait', methods=['POST'])
def wait_container():
    return harvey.Container.wait(id)

@api.route('/containers/<id>/remove', methods=['DELETE'])
def remove_container():
    return harvey.Container.remove(id)

"""Image Endpoints"""
@api.route('/build', methods=['POST'])
def build_image(data, tag='latest-build', context=''):
    return harvey.Image.build(data, tag, context)

@api.route('/images/<id>', methods=['GET'])
def retrieve_image(id):
    return harvey.Image.retrieve(id)

@api.route('/images', methods=['GET'])
def all_images():
    return harvey.Image.all()

@api.route('/images/<id>/remove', methods=['DELETE'])
def remove_image(id):
    return harvey.Image.remove(id)

"""Webhook Endpoints"""
@api.route('/webhook', methods=['POST'])
def receive_webhook():
    data = json.loads(request.data)
    # data = request.data
    harvey.Webhook.receive(data)
    return "OK"

"""Git Endpoints"""
@api.route('/pull', methods=['POST'])
def pull_project(data):
    return harvey.Git.pull(data)

"""Pipeline Endpoints"""
@api.route('/pipeline/test', methods=['POST'])
def test_pipeline(data):
    return harvey.Pipeline.test(data)

@api.route('/pipeline/deploy', methods=['POST'])
def build_pipeline(data, tag):
    return harvey.Pipeline.deploy(data, tag)

@api.route('/pipeline/full', methods=['POST'])
def full_pipeline(data, tag):
    data = json.loads(request.data)
    return harvey.Pipeline.full(data, tag)

if __name__ == '__main__':
    api.run()

import json
import os
import time

import requests_unixsocket
from dotenv import load_dotenv
from flask import Flask, abort, request

from harvey.globals import Global
from harvey.webhooks import Webhook

load_dotenv()  # must remain at the top of this file
API = Flask(__name__)
HOST = os.getenv('HOST', '127.0.0.1')
PORT = os.getenv('PORT', '5000')
DEBUG = os.getenv('DEBUG', 'True')

# TODO: Add authentication to each endpoint


@API.route('/health', methods=['GET'])
def healthcheck():
    """Return a 200 if Harvey is running."""
    status_code = 200
    response = {
        'success': True,
        'message': 'Ok',
    }, status_code

    return response


@API.route('/pipelines/start', methods=['POST'])
def start_pipeline():
    """Start a pipeline based on webhook data."""
    return Webhook.parse_webhook(request=request, use_compose=False)


@API.route('/pipelines/start/compose', methods=['POST'])
def start_pipeline_compose():
    """Start a pipeline based on webhook data
    But build from compose file.
    """
    return Webhook.parse_webhook(request=request, use_compose=True)


@API.route('/pipelines/<pipeline_id>', methods=['GET'])
def retrieve_pipeline(pipeline_id):
    """Retrieve a pipeline's logs by ID."""
    # TODO: This is a hacky temporary solution until we can
    # store this data in a database and is not meant to remain
    # as a long-term solution
    filename = f'{pipeline_id}.log'
    for root, dirs, files in os.walk(Global.PROJECTS_LOG_PATH):
        if filename in files:
            with open(os.path.join(root, filename), 'r') as output:
                response = output.read()
            return response
    return abort(404)


@API.route('/pipelines', methods=['GET'])
def retrieve_pipelines():
    """Retrieve a list of pipelines."""
    # TODO: This is a hacky temporary solution until we can
    # store this data in a database and is not meant to remain
    # as a long-term solution
    pipelines = {
        'pipelines': [],
    }
    for root, dirs, files in os.walk(Global.PROJECTS_LOG_PATH, topdown=True):
        for filename in files:
            timestamp = time.ctime(os.path.getmtime(os.path.join(root, filename)))
            pipelines['pipelines'].append(f'{timestamp}: {os.path.join(root, filename)}')
    return json.dumps(pipelines, indent=4)


def main():
    # allows us to use requests_unixsocket via requests
    requests_unixsocket.monkeypatch()
    API.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == '__main__':
    main()

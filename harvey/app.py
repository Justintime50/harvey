import json
import os
import time

import requests_unixsocket
from dotenv import load_dotenv
from flask import Flask, abort, request

from harvey.globals import Global
from harvey.webhooks import Webhook

load_dotenv()  # must remain at the top of this file
APP = Flask(__name__)
HOST = os.getenv('HOST', '127.0.0.1')
PORT = os.getenv('PORT', '5000')
DEBUG = os.getenv('DEBUG', 'True')


@APP.errorhandler(404)
def not_found(e):
    """Return a 404 if the route is not found."""
    status_code = 404
    response = {
        'success': False,
        'message': 'Not a valid endpoint.',
    }, status_code

    return response


@APP.route('/health', methods=['GET'])
def harvey_healthcheck():
    """Return a 200 if Harvey is running."""
    status_code = 200
    response = {
        'success': True,
        'message': 'Ok',
    }, status_code

    return response


@APP.route('/pipelines/start/compose', methods=['POST'])  # TODO: This is deprecated, remove in a future release
@APP.route('/pipelines/start', methods=['POST'])
def start_pipeline():
    """Start a pipeline based on webhook data and the `docker-compose.yml` file."""
    return Webhook.parse_webhook(request=request)


@APP.route('/pipelines/<pipeline_id>', methods=['GET'])
def retrieve_pipeline(pipeline_id):
    """Retrieve a pipeline's logs by ID."""
    # TODO: Add authentication to this endpoint

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


@APP.route('/pipelines', methods=['GET'])
def retrieve_pipelines():
    """Retrieve a list of pipelines."""
    # TODO: Add authentication to this endpoint

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
    # Allows us to use requests_unixsocket via requests
    requests_unixsocket.monkeypatch()
    APP.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == '__main__':
    main()

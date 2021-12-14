import datetime
import os
import time

import requests_unixsocket  # type: ignore
from dotenv import load_dotenv
from flask import Flask, abort, request

from harvey.globals import Global
from harvey.utils import LOG_LEVEL, setup_logger
from harvey.webhooks import Webhook

load_dotenv()  # Must remain at the top of this file
APP = Flask(__name__)
HOST = os.getenv('HOST', '127.0.0.1')
PORT = os.getenv('PORT', '5000')


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


@APP.route('/pipelines/start', methods=['POST'])
def start_pipeline():
    """Start a pipeline based on webhook data and the `docker-compose.yml` file."""
    return Webhook.parse_webhook(request=request)


@APP.route('/pipelines/<pipeline_id>', methods=['GET'])
def retrieve_pipeline(pipeline_id: str):
    """Retrieve a pipeline's logs by ID.

    A `pipeline_id` will be `username-reponame` as they appear on GitHub.
    """
    filename = f'{pipeline_id}.log'
    project_log_path = os.path.join(Global.PROJECTS_LOG_PATH, filename)

    try:
        with open(project_log_path, 'r') as output:
            project_log = output.read()

            last_run = datetime.datetime.strptime(time.ctime(os.path.getmtime(project_log_path)), '%c')
            status = (
                'Success' if 'success' in project_log.lower() or 'succeeded' in project_log.lower() else 'Failure'
            )  # Naively check the logs for an indicator of the status being success

            response = {
                'project': pipeline_id,
                'last_run': f'{last_run}',
                'status': status,
                'project_log': project_log,
            }

            return response
    except Exception:
        return abort(404)


@APP.route('/pipelines', methods=['GET'])
def retrieve_pipelines():
    """Retrieve a list of pipelines.

    The `project` values will be `username-reponame` as they appear on GitHub.
    """
    pipelines = {}

    for root, dirs, files in os.walk(Global.PROJECTS_LOG_PATH, topdown=True):
        for filename in files:
            # Skip the macOS meta directory file
            if filename == '.DS_Store':
                continue
            full_file_path = os.path.join(root, filename)
            last_run = datetime.datetime.strptime(time.ctime(os.path.getmtime(full_file_path)), '%c')
            log_file = filename.split('.')[0]

            with open(full_file_path, 'r') as log_file_contents:
                log_file_data = log_file_contents.read()

                status = (
                    'Success'
                    if 'success' in log_file_data.lower() or 'succeeded' in log_file_data.lower()
                    else 'Failure'
                )  # Naively check the logs for an indicator of the status being success

            pipelines[log_file] = {
                'last_run': f'{last_run}',
                'status': status,
                'pipeline_log': '...',  # Retrieve a single record to get the pipeline_log
            }

    return pipelines


def main():
    # Allows us to use requests_unixsocket via requests
    requests_unixsocket.monkeypatch()
    flask_debug = LOG_LEVEL == 'DEBUG'
    setup_logger()
    APP.run(host=HOST, port=PORT, debug=flask_debug)


if __name__ == '__main__':
    main()

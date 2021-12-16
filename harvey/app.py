import os

import requests_unixsocket  # type: ignore
from dotenv import load_dotenv
from flask import Flask, abort, request
from sqlitedict import SqliteDict  # type: ignore

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

    A `pipeline_id` will be `username-repo_name-commit_id`.
    """
    try:
        with SqliteDict(Global.PIPELINES_STORE_PATH) as mydict:
            return mydict[pipeline_id]
    except Exception:
        return abort(404)


@APP.route('/pipelines', methods=['GET'])
def retrieve_pipelines():
    """Retrieves pipelines from the Sqlite store.

    - The keys will be `username-repo_name-commit_id`.
    - The user can optionally pass a URL param of `project` to filter the results
    """
    pipelines = {}
    pipeline_return_limit = 100

    project_filter = request.args.get('project')

    # TODO: Retrieve the most recent pipelines
    with SqliteDict(Global.PIPELINES_STORE_PATH) as mydict:
        for index, (key, value) in enumerate(mydict.iteritems()):
            if index >= pipeline_return_limit:
                break

            if project_filter and project_filter in key:
                pipelines[key] = value
            elif not project_filter:
                pipelines[key] = value

    return pipelines


def main():
    # Allows us to use requests_unixsocket via requests
    requests_unixsocket.monkeypatch()
    flask_debug = LOG_LEVEL == 'DEBUG'
    setup_logger()
    APP.run(host=HOST, port=PORT, debug=flask_debug)


if __name__ == '__main__':
    main()

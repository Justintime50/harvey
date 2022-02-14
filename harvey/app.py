import os

import requests_unixsocket  # type: ignore
from dotenv import load_dotenv
from flask import Flask, abort, request

from harvey.api import Api
from harvey.config import Config
from harvey.utils import setup_logger

load_dotenv()  # Must remain at the top of this file
APP = Flask(__name__)


@APP.errorhandler(401)
def not_authorized(e):
    """Return a 401 if the request is not authorized."""
    status_code = 401
    response = {
        'success': False,
        'message': 'You are not authorized to access this endpoint. Please check your credentials and try again.',
    }, status_code

    return response


@APP.errorhandler(404)
def not_found(e):
    """Return a 404 if the route is not found."""
    status_code = 404
    response = {
        'success': False,
        'message': 'The endpoint you hit is either not valid or the record was not found.',
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


@APP.route('/pipelines', methods=['GET'])
@Api.check_api_key
def retrieve_pipelines():
    """Retrieves pipelines from the Sqlite store.

    - The keys will be `username-repo_name-commit_id`.
    - The user can optionally pass a URL param of `page_size` to limit how many results are returned
    - The user can optionally pass a URL param of `project` to filter what pipelines get returned
    """
    try:
        return Api.retrieve_pipelines(request)
    except Exception:
        raise


@APP.route('/pipelines/<pipeline_id>', methods=['GET'])
@Api.check_api_key
def retrieve_pipeline(pipeline_id: str):
    """Retrieve a pipeline's details by ID.

    A `pipeline_id` will be `username-repo_name-commit_id`.
    """
    try:
        return Api.retrieve_pipeline(pipeline_id)
    except Exception:
        return abort(404)


# Notably, we do not check the API key here because we'll check its presence later when we parse the webhook
@APP.route('/pipelines/start', methods=['POST'])
def start_pipeline():
    """Start a pipeline based on webhook data and the `docker-compose.yml` file.

    This is the main entrypoint for Harvey.
    """
    try:
        return Api.parse_github_webhook(request)
    except Exception:
        raise


@APP.route('/projects', methods=['GET'])
@Api.check_api_key
def retrieve_projects():
    """Retrieves a list of project names from the git repos stored in Harvey."""
    try:
        return Api.retrieve_projects(request)
    except Exception:
        raise


@APP.route('/locks', methods=['GET'])
@Api.check_api_key
def retrieve_locks():
    """Retrieves the list of locks"""
    try:
        return Api.retrieve_locks(request)
    except Exception:
        raise


@APP.route('/locks/<project_name>', methods=['GET'])
@Api.check_api_key
def retrieve_lock(project_name: str):
    """Retrieves the lock status of a project by its name."""
    try:
        return Api.retrieve_lock(project_name)
    except Exception:
        return abort(404)


@APP.route('/projects/<project_name>/lock', methods=['PUT'])
@Api.check_api_key
def lock_project(project_name: str):
    """Enables the deployment lock for a project."""
    try:
        return Api.lock_project(project_name)
    except Exception:
        raise


@APP.route('/projects/<project_name>/unlock', methods=['PUT'])
@Api.check_api_key
def unlock_project(project_name: str):
    """Disables the deployment lock for a project."""
    try:
        return Api.unlock_project(project_name)
    except Exception:
        raise


def main():
    setup_logger()

    # Setup the directory for the SQLite databases
    if not os.path.exists(Config.stores_path):
        os.makedirs(Config.stores_path)

    requests_unixsocket.monkeypatch()  # Allows us to use requests_unixsocket via requests

    flask_debug = Config.log_level == 'DEBUG'
    APP.run(host=Config.host, port=Config.port, debug=flask_debug)


if __name__ == '__main__':
    main()

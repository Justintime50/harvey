import os
import subprocess  # nosec
from typing import (
    Any,
    Dict,
    Optional,
)

import requests_unixsocket  # type: ignore
import sentry_sdk
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    request,
)

from harvey.api import Api
from harvey.config import Config
from harvey.utils import setup_logger


load_dotenv()  # Must remain at the top of this file
APP = Flask(__name__)
REQUIRED_DOCKER_COMPOSE_VERSION = 'v2'


def create_response_dict(message: str, success: Optional[bool] = False, status_code: Optional[int] = 500):
    """Response object that all Harvey responses return."""
    return {
        'message': message,
        'success': success,
    }, status_code


@APP.errorhandler(401)
def not_authorized(e):
    """Return a 401 if the request is not authorized."""
    return create_response_dict(
        message='You are not authorized to access this endpoint. Please check your credentials and try again.',
        success=False,
        status_code=401,
    )


@APP.errorhandler(404)
def not_found(e) -> Dict[str, Any]:
    """Return a 404 if the route is not found."""
    return create_response_dict(
        message='The endpoint you hit is either not valid or the record was not found.',
        success=False,
        status_code=404,
    )


@APP.errorhandler(500)
def server_error(e) -> Dict[str, Any]:
    """Return a 500 if there is a problem with Harvey."""
    return create_response_dict(
        message='An error has occured due to something on our end.',
        success=False,
        status_code=500,
    )


@APP.route('/health', methods=['GET'])
def harvey_healthcheck():
    """Return a 200 if Harvey is running."""
    return create_response_dict(
        message='Ok',
        success=True,
        status_code=200,
    )


@APP.route('/deployments', methods=['GET'])
@Api.check_api_key
def retrieve_deployments():
    """Retrieves deployments from the Sqlite store.

    - The keys will be `username-repo_name-commit_id`.
    - The user can optionally pass a URL param of `page_size` to limit how many results are returned
    - The user can optionally pass a URL param of `project` to filter what deployments get returned
    """
    try:
        return Api.retrieve_deployments(request)
    except Exception:
        return abort(500)


@APP.route('/deployments/<deployment_id>', methods=['GET'])
@Api.check_api_key
def retrieve_deployment(deployment_id: str):
    """Retrieve a deployment's details by ID.

    A `deployment_id` will be `username-repo_name-commit_id`.
    """
    try:
        return Api.retrieve_deployment(deployment_id)
    except Exception:
        return abort(500)


# Notably, we do not check the API key here because we'll check its presence later when we parse the webhook
@APP.route('/deploy', methods=['POST'])
def deploy_project():
    """Deploy a project based on webhook data and the `docker-compose.yml` file.

    This is the main entrypoint for Harvey.
    """
    try:
        return Api.parse_github_webhook(request)
    except Exception:
        return abort(500)


@APP.route('/projects', methods=['GET'])
@Api.check_api_key
def retrieve_projects():
    """Retrieves a list of project names from the git repos stored in Harvey."""
    try:
        return Api.retrieve_projects(request)
    except Exception:
        return abort(500)


@APP.route('/locks', methods=['GET'])
@Api.check_api_key
def retrieve_locks():
    """Retrieves the list of locks"""
    try:
        return Api.retrieve_locks(request)
    except Exception:
        return abort(500)


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
        return abort(500)


@APP.route('/projects/<project_name>/unlock', methods=['PUT'])
@Api.check_api_key
def unlock_project(project_name: str):
    """Disables the deployment lock for a project."""
    try:
        return Api.unlock_project(project_name)
    except Exception:
        return abort(500)


def bootstrap(debug_mode):
    """Bootstrap the Harvey instance on startup.

    Any task required for Harvey to work that only needs to be instantiated once should go here.
    """
    setup_logger()

    # Ensure the correct Docker Compose version is available
    docker_compose_version = subprocess.check_output(  # nosec
        ['docker-compose', '--version'],
        stdin=None,
        stderr=None,
        timeout=3,
    ).decode('UTF-8')
    if REQUIRED_DOCKER_COMPOSE_VERSION not in docker_compose_version:
        raise Exception(f'Harvey requires Docker Compose {REQUIRED_DOCKER_COMPOSE_VERSION}.')

    # Setup Sentry
    if Config.sentry_url:
        sentry_sdk.init(
            Config.sentry_url,
            debug=debug_mode,
        )

    # Setup the directory for the SQLite databases
    if not os.path.exists(Config.database_path):
        os.makedirs(Config.database_path)

    # Allows us to use requests_unixsocket via requests
    requests_unixsocket.monkeypatch()


if __name__ == '__main__':
    # These tasks take place when run via Flask
    debug_mode = Config.log_level == 'DEBUG'
    bootstrap(debug_mode)

    APP.run(host=Config.host, port=Config.port, debug=debug_mode)


if __name__ != '__main__':
    # These tasks take place when run via Gunicorn, the remaining config can be found in `wsgi.py`
    debug_mode = Config.log_level == 'DEBUG'
    bootstrap(debug_mode)

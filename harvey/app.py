import os
import threading
from typing import (
    Any,
    Dict,
    Optional,
)

import requests_unixsocket  # type: ignore
import sentry_sdk
import werkzeug
import woodchips
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    request,
)

from harvey.api import Api
from harvey.config import Config
from harvey.deployments import Deployment
from harvey.errors import HarveyError
from harvey.locks import (
    lock_project,
    retrieve_lock,
    unlock_project,
)
from harvey.repos.deployments import (
    retrieve_deployment,
    retrieve_deployments,
)
from harvey.repos.locks import retrieve_locks
from harvey.repos.projects import retrieve_projects
from harvey.repos.webhooks import retrieve_webhook
from harvey.utils.utils import (
    run_subprocess_command,
    setup_logger,
)


# Must remain at the top of this file to take effect, we load both from the path and locally
load_dotenv(dotenv_path=Config.harvey_path)
load_dotenv()

APP = Flask(__name__)
REQUIRED_DOCKER_COMPOSE_VERSION = 'v2'

# Fixes segfaults on macOS, see the following for more details:
# - https://bugs.python.org/issue30385
# - https://github.com/unbit/uwsgi/issues/1722
# - https://github.com/Justintime50/harvey/issues/72
os.environ["no_proxy"] = "*"


def bootstrap() -> bool:
    """Bootstrap the Harvey instance on startup.

    Any task required for Harvey to work that only needs to be instantiated once should go here.
    """
    setup_logger()
    debug = _get_debug_bool(Config.log_level)

    # Ensure the correct Docker Compose version is available
    docker_compose_version = run_subprocess_command(['docker', 'compose', 'version'])
    if REQUIRED_DOCKER_COMPOSE_VERSION not in docker_compose_version:
        raise HarveyError(f'Harvey requires Docker Compose {REQUIRED_DOCKER_COMPOSE_VERSION}.')

    # Setup Sentry
    if Config.sentry_url:
        sentry_sdk.init(
            Config.sentry_url,
            debug=debug,
        )

    # Setup the directory for the SQLite databases
    if not os.path.exists(Config.database_path):
        os.makedirs(Config.database_path)

    # Allows us to use requests_unixsocket via requests
    requests_unixsocket.monkeypatch()

    return debug


@APP.errorhandler(401)
def not_authorized(error):
    """Return a 401 if the request is not authorized."""
    return _create_response_dict(
        message='You are not authorized to access this endpoint. Please check your credentials and try again.',
        success=False,
        status_code=401,
    )


@APP.errorhandler(404)
def not_found(error) -> Dict[str, Any]:
    """Return a 404 if the route is not found."""
    return _create_response_dict(
        message='The endpoint you hit is either not valid or the record was not found.',
        success=False,
        status_code=404,
    )


@APP.errorhandler(500)
def server_error(error) -> Dict[str, Any]:
    """Return a 500 if there is a problem with Harvey."""
    return _create_response_dict(
        message='An error has occured due to something on our end.',
        success=False,
        status_code=500,
    )


@APP.route('/health', methods=['GET'])
def harvey_healthcheck_endpoint():
    """Return a 200 if Harvey is running."""
    return _create_response_dict(
        message='Ok',
        success=True,
        status_code=200,
    )


@APP.route('/deployments', methods=['GET'])
@Api.check_api_key
def retrieve_deployments_endpoint():
    """Retrieves deployments from the Sqlite store.

    - The keys will be `username-repo_name-commit_id`.
    - The user can optionally pass a URL param of `page_size` to limit how many results are returned
    - The user can optionally pass a URL param of `project` to filter what deployments get returned
    """
    try:
        return retrieve_deployments(request)
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/deployments/<deployment_id>', methods=['GET'])
@Api.check_api_key
def retrieve_deployment_endpoint(deployment_id: str):
    """Retrieve a deployment's details by ID.

    A `deployment_id` will be `username-repo_name-commit_id`.
    """
    try:
        return retrieve_deployment(deployment_id)
    except Exception as error:
        _log_error(error)
        return abort(500)


# Notably, we do not check the API key here because we'll check its presence later when we parse the webhook
@APP.route('/deploy', methods=['POST'])
def deploy_project_endpoint():
    """Deploy a project based on webhook data and the `docker-compose.yml` file.

    This is the main entrypoint for Harvey.
    """
    try:
        return Api.parse_github_webhook(request)
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/projects', methods=['GET'])
@Api.check_api_key
def retrieve_projects_endpoint():
    """Retrieves a list of project names from the git repos stored in Harvey."""
    try:
        return retrieve_projects(request)
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/projects/<project_name>/redeploy', methods=['POST'])
@Api.check_api_key
def redeploy_project_endpoint(project_name):
    """Redeploy a project based on local webhook data stored in the database from a previous deploy."""
    try:
        webhook = retrieve_webhook(project_name)
        if not webhook:
            raise HarveyError(f'Webhook does not exist for {project_name}')
        else:
            threading.Thread(
                name=project_name,
                target=Deployment.run_deployment,
                args=(webhook,),
            ).start()
            return _create_response_dict(
                f'Redeploying {project_name}...',
                success=True,
                status_code=200,
            )
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/projects/<project_name>/webhook', methods=['GET'])
@Api.check_api_key
def retrieve_project_webhook_endpoint(project_name):
    """Retrieves the locally stored webhook of a project."""
    try:
        webhook = retrieve_webhook(project_name)
        if not webhook:
            return abort(404)  # This will throw an exception in the except block below
        else:
            return _create_response_dict(
                webhook,
                success=True,
                status_code=200,
            )
    except werkzeug.exceptions.NotFound:
        raise
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/projects/<project_name>/lock', methods=['PUT'])
@Api.check_api_key
def lock_project_endpoint(project_name: str):
    """Enables the deployment lock for a project."""
    try:
        return lock_project(project_name)
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/projects/<project_name>/unlock', methods=['PUT'])
@Api.check_api_key
def unlock_project_endpoint(project_name: str):
    """Disables the deployment lock for a project."""
    try:
        return unlock_project(project_name)
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/locks', methods=['GET'])
@Api.check_api_key
def retrieve_locks_endpoint():
    """Retrieves the list of locks"""
    try:
        return retrieve_locks(request)
    except Exception as error:
        _log_error(error)
        return abort(500)


@APP.route('/locks/<project_name>', methods=['GET'])
@Api.check_api_key
def retrieve_lock_endpoint(project_name: str):
    """Retrieves the lock status of a project by its name."""
    try:
        return retrieve_lock(project_name)
    except Exception as error:
        _log_error(error)
        return abort(404)


@APP.route('/threads', methods=['GET'])
@Api.check_api_key
def retrieve_threads_endpoint():
    """Retrieves a list of running threads for Harvey. Threads indicate ongoing deployments."""
    threads = []
    for thread in threading.enumerate():
        threads.append(thread.name)

    return {'threads': threads}


def _create_response_dict(message: str, success: Optional[bool] = False, status_code: Optional[int] = 500):
    """Response object that all Harvey responses return."""
    return {
        'message': message,
        'success': success,
    }, status_code


def _log_error(error):
    """Logs an error with Woodchips."""
    logger = woodchips.get(Config.logger_name)
    logger.error(error)


def _get_debug_bool(log_level) -> bool:
    """Returns True if `log_level` is `DEBUG`."""
    return log_level == 'DEBUG'


if __name__ == '__main__':
    """These tasks take place when run via Flask."""
    debug = bootstrap()

    APP.run(host=Config.host, port=Config.port, debug=debug)


if __name__ != '__main__':
    """These tasks take place when run via uWSGI, the remaining config can be found in `wsgi.py`."""
    bootstrap()

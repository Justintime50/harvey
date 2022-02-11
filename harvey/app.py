import os

import requests_unixsocket  # type: ignore
from dotenv import load_dotenv
from flask import Flask, abort, request
from sqlitedict import SqliteDict  # type: ignore

from harvey.api import Api
from harvey.config import Config
from harvey.utils import Utils, setup_logger

load_dotenv()  # Must remain at the top of this file
APP = Flask(__name__)


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
    return Api.parse_webhook(request=request)


@APP.route('/pipelines/<pipeline_id>', methods=['GET'])
def retrieve_pipeline(pipeline_id: str):
    """Retrieve a pipeline's details by ID.

    A `pipeline_id` will be `username-repo_name-commit_id`.
    """
    try:
        with SqliteDict(Config.pipelines_store_path) as mydict:
            for key, value in mydict.iteritems():
                transformed_key = key.split('@')
                if pipeline_id == f'{transformed_key[0]}-{transformed_key[1]}':
                    return value
        raise Exception
    except Exception:
        return abort(404)


@APP.route('/pipelines', methods=['GET'])
def retrieve_pipelines():
    """Retrieves pipelines from the Sqlite store.

    - The keys will be `username-repo_name-commit_id`.
    - The user can optionally pass a URL param of `page_size` to limit how many results are returned
    - The user can optionally pass a URL param of `project` to filter what pipelines get returned
    """
    pipelines = {'pipelines': []}

    page_size = int(request.args.get('page_size', Config.pagination_limit))
    project_name = request.args.get('project')

    with SqliteDict(Config.pipelines_store_path) as mydict:
        for record_num, (key, value) in enumerate(mydict.iteritems(), start=1):
            if record_num > page_size:
                break

            if project_name and value['project'] == project_name:
                pipelines['pipelines'].append(value)
            elif not project_name:
                pipelines['pipelines'].append(value)
            else:
                pass

    sorted_pipelines = sorted(pipelines['pipelines'], key=lambda i: i['timestamp'], reverse=True)
    pipelines['pipelines'] = sorted_pipelines

    return pipelines


@APP.route('/projects', methods=['GET'])
def retrieve_projects():
    """Retrieves a list of project names from the git repos stored in Harvey."""
    projects = {'projects': []}

    page_size = int(request.args.get('page_size', Config.pagination_limit))

    project_owners = os.listdir(Config.projects_path)
    if '.DS_Store' in project_owners:
        project_owners.remove('.DS_Store')
    for project_owner in project_owners:
        project_names = os.listdir(os.path.join(Config.projects_path, project_owner))
        if '.DS_Store' in project_names:
            project_names.remove('.DS_Store')
        for project_name in project_names:
            final_project_name = f'{project_owner}-{project_name}'
            projects['projects'].append(final_project_name)

        if len(projects['projects']) > page_size:
            break

    return projects


@APP.route('/locks/<project_name>', methods=['GET'])
def retrieve_lock(project_name: str):
    """Retrieves the lock status of a project by its name."""
    try:
        lock_status = Utils.lookup_project_lock(project_name)

        if lock_status:
            return {'locked': lock_status}
        else:
            raise Exception
    except Exception:
        return abort(404)


# TODO: Add a `lock` and `unlock` endpoint for deployments


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

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
    """Retrieve a pipeline's details by ID.

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
    - The user can optionally pass a URL param of `page_size` to limit how many results are returned
    """
    pipelines = {'pipelines': []}
    return_limit = 100

    page_size = int(request.args.get('page_size', return_limit))

    # TODO: Retrieve the most recent pipelines
    with SqliteDict(Global.PIPELINES_STORE_PATH) as mydict:
        for record_num, (key, value) in enumerate(mydict.iteritems(), start=1):
            if record_num > page_size:
                break

            pipelines['pipelines'].append(value)

    return pipelines


@APP.route('/projects', methods=['GET'])
def retrieve_projects():
    """Retrieves projects from the Sqlite store."""
    projects = {'projects': []}
    return_limit = 100

    page_size = int(request.args.get('page_size', return_limit))

    project_owners = os.listdir(Global.PROJECTS_PATH)
    for project_owner in project_owners:
        project_names = os.listdir(os.path.join(Global.PROJECTS_PATH, project_owner))
        for project_name in project_names:
            final_project_name = f'{project_owner}-{project_name}'
            projects['projects'].append(final_project_name)

        if len(projects['projects']) > page_size:
            break

    return projects


@APP.route('/project-pipelines/<project_name>', methods=['GET'])
def retrieve_project_pipelines(project_name: str):
    """Retrieves a list of pipelines for a given project from the Sqlite store.

    - The user can optionally pass a URL param of `page_size` to limit how many results are returned
    """
    pipelines = {'pipelines': []}
    return_limit = 100

    page_size = int(request.args.get('page_size', return_limit))

    # TODO: Retrieve the most recent pipelines
    with SqliteDict(Global.PIPELINES_STORE_PATH) as mydict:
        for key, value in mydict.iteritems():
            if value['project'] == project_name:
                pipelines['pipelines'].append(value)
            else:
                # Don't include pipelines for another project
                pass

            if len(pipelines['pipelines']) > page_size:
                break

    return pipelines


def main():
    requests_unixsocket.monkeypatch()  # Allows us to use requests_unixsocket via requests
    flask_debug = LOG_LEVEL == 'DEBUG'
    setup_logger()
    APP.run(host=HOST, port=PORT, debug=flask_debug)


if __name__ == '__main__':
    main()

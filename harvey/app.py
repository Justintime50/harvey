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
            for key, value in mydict.iteritems():
                transformed_key = key.split('@')
                if pipeline_id == f'{transformed_key[0]}-{transformed_key[1]}':
                    return value
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
    return_limit = 100

    page_size = int(request.args.get('page_size', return_limit))
    project_name = request.args.get('project')

    with SqliteDict(Global.PIPELINES_STORE_PATH) as mydict:
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
    """Retrieves projects from the Sqlite store."""
    projects = {'projects': []}
    return_limit = 100

    page_size = int(request.args.get('page_size', return_limit))

    project_owners = os.listdir(Global.PROJECTS_PATH)
    if '.DS_Store' in project_owners:
        project_owners.remove('.DS_Store')
    for project_owner in project_owners:
        project_names = os.listdir(os.path.join(Global.PROJECTS_PATH, project_owner))
        if '.DS_Store' in project_names:
            project_names.remove('.DS_Store')
        for project_name in project_names:
            final_project_name = f'{project_owner}-{project_name}'
            projects['projects'].append(final_project_name)

        if len(projects['projects']) > page_size:
            break

    return projects


def main():
    setup_logger()

    # Setup the directory for the Sqlite databases
    if not os.path.exists(Global.STORES_PATH):
        os.mkdir(Global.STORES_PATH)

    requests_unixsocket.monkeypatch()  # Allows us to use requests_unixsocket via requests

    flask_debug = LOG_LEVEL == 'DEBUG'
    APP.run(host=HOST, port=PORT, debug=flask_debug)


if __name__ == '__main__':
    main()

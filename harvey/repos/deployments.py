import datetime
from typing import (
    Any,
    Dict,
    List,
)

import flask
import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.errors import HarveyError
from harvey.utils.api_utils import get_page_size
from harvey.webhooks import Webhook


DATABASE_TABLE_NAME = 'deployments'


def store_deployment_details(webhook: Dict[str, Any], final_output: str = 'NA'):
    """Store the deployment's details including logs and metadata to a Sqlite database.

    A project ID consists of the `project_name@commit_id`.
    """
    logger = woodchips.get(Config.logger_name)

    logger.debug(f'Storing deployment details for {Webhook.repo_full_name(webhook)}...')

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        # Naively check the logs for an indicator of the status being success
        if 'success' in final_output.lower() or 'succeeded' in final_output.lower():
            deployment_status = 'Success'
        elif final_output == 'NA':
            deployment_status = 'In-Progress'
        else:
            deployment_status = 'Failure'

        database_table[Webhook.deployment_id(webhook)] = {
            'project': Webhook.repo_full_name(webhook).replace("/", "-"),
            'commit': Webhook.repo_commit_id(webhook),
            'log': final_output,
            'status': deployment_status,
            'timestamp': str(datetime.datetime.utcnow()),
        }

        database_table.commit()


def retrieve_deployment(deployment_id: str) -> Dict[str, Any]:
    """Retrieve a deployment's details from a given `deployment_id`."""
    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        for key, value in database_table.iteritems():
            transformed_key = key.split('@')
            if deployment_id == f'{transformed_key[0]}-{transformed_key[1]}':
                return value

    raise HarveyError(f'Could not retrieve deployment\'s details for {deployment_id}!')


def retrieve_deployments(request: flask.Request) -> Dict[str, List[Any]]:
    """Retrieve a list of deployments until the pagination limit is reached."""
    deployments: Dict[str, Any] = {'deployments': []}

    page_size = get_page_size(request)
    project_name = request.args.get('project')

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        for _, value in database_table.iteritems():
            # If a project name is provided, only return deployments for that project
            if project_name and value['project'] == project_name:
                deployments['deployments'].append(value)
            # This block is for a generic list of deployments (all deployments)
            elif not project_name:
                deployments['deployments'].append(value)
            # If a project name was specified but doesn't match, don't add to list
            else:
                pass

    sorted_deployments = sorted(deployments['deployments'], key=lambda i: i['timestamp'], reverse=True)[:page_size]
    deployments['total_count'] = len(deployments['deployments'])
    deployments['deployments'] = sorted_deployments

    return deployments

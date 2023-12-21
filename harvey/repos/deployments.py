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
from harvey.utils.utils import get_utc_timestamp
from harvey.webhooks import Webhook


DATABASE_TABLE_NAME = 'deployments'


def store_deployment_details(webhook: Dict[str, Any], final_output: str = 'NA'):
    """Store the deployment's details including logs and metadata to a Sqlite database.

    A project ID consists of the `project_name@commit_id`.
    """
    logger = woodchips.get(Config.logger_name)

    logger.debug(f'Storing deployment details for {Webhook.repo_full_name(webhook)}...')

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        if 'deployment succeeded' in final_output.lower():
            deployment_status = 'Success'
        elif final_output == 'NA':
            deployment_status = 'In-Progress'
        else:
            deployment_status = 'Failure'

        now = str(get_utc_timestamp())

        deployment_runtime = final_output.partition('Deployment execution time: ')[2].split('\n\n')[0]

        attempt: Dict[str, Any] = {
            'log': final_output,
            'status': deployment_status,
            'timestamp': now,
            'runtime': deployment_runtime if deployment_runtime else None,
        }

        if database_table.get(Webhook.deployment_id(webhook)):
            attempts = database_table[Webhook.deployment_id(webhook)].get('attempts', [])
        else:
            attempts = []

        if deployment_status == 'In-Progress':
            attempt_number = len(attempts) + 1
            attempt['attempt'] = attempt_number
            attempts.append(attempt)
        else:
            # If we get here, we failed or succeeded, take the previous "In-Progress entry and update it"
            attempt_number = len(attempts)
            attempt['attempt'] = attempt_number
            attempts[-1] = attempt

        database_table[Webhook.deployment_id(webhook)] = {
            'project': Webhook.repo_full_name(webhook).replace("/", "-"),
            'commit': Webhook.repo_commit_id(webhook),
            # This timestamp will be the most recent attempt's timestamp, important to have at the root for sorting
            'timestamp': now,
            'attempts': attempts,
        }

        database_table.commit()


def retrieve_deployment(deployment_id: str) -> Dict[str, Any]:
    """Retrieve a deployment's details from a given `deployment_id`."""
    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        for key, value in database_table.items():
            transformed_key = key.split('@')
            if deployment_id == f'{transformed_key[0]}-{transformed_key[1]}':
                if value.get('attempts'):
                    value['attempts'] = sorted(value['attempts'], key=lambda x: x['attempt'], reverse=True)
                return value

    raise HarveyError(f'Could not retrieve deployment details for {deployment_id}!')


def retrieve_deployments(request: flask.Request) -> Dict[str, List[Any]]:
    """Retrieve a list of deployments until the pagination limit is reached."""
    deployments: Dict[str, Any] = {'deployments': []}

    page_size = get_page_size(request)
    project_name = request.args.get('project')

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        for _, value in database_table.items():
            # If a project name is provided, only return deployments for that project
            if project_name and value['project'] == project_name:
                if value.get('attempts'):
                    value['attempts'] = sorted(value['attempts'], key=lambda x: x['attempt'], reverse=True)
                deployments['deployments'].append(value)
            # This block is for a generic list of deployments (all deployments)
            elif not project_name:
                if value.get('attempts'):
                    value['attempts'] = sorted(value['attempts'], key=lambda x: x['attempt'], reverse=True)
                deployments['deployments'].append(value)
            # If a project name was specified but doesn't match, don't add to list
            else:
                pass

    sorted_deployments = sorted(deployments['deployments'], key=lambda i: i['timestamp'], reverse=True)[:page_size]
    deployments['total_count'] = len(
        [attempt for deployment in deployments['deployments'] for attempt in deployment.get('attempts', [])]
    )
    deployments['deployments'] = sorted_deployments

    return deployments

import base64
import os
from functools import wraps
from threading import Thread
from typing import Any, Dict, List, Tuple

import flask
import requests
import woodchips
from flask import abort, request
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.locks import Lock
from harvey.pipelines import Pipeline
from harvey.webhooks import Webhook


class Api:
    """The Api class contains all the actions accessible via an API endpoint.

    These functions may call out to other modules in Harvey and ultimately serve as the "glue"
    that pulls the entire action together prior to returning whatever the result is to the user via API.
    """

    @staticmethod
    def _page_size(request: flask.Request) -> int:
        """Return a sane page size based on the request."""
        return int(request.args.get('page_size')) if request.args.get('page_size') else Config.pagination_limit

    @staticmethod
    def check_api_key(func):
        """Decorator for API endpoints that require an API key."""

        @wraps(func)
        def check_auth(*args, **kwargs):
            """Checks that the Authorization header (Basic Auth) matches the secret on file."""
            auth_header = request.headers.get('Authorization')

            # Only check the API key if the Harvey instance expects one
            if Config.webhook_secret:
                if auth_header:
                    split_auth = auth_header.strip().split(' ')

                    if len(split_auth) == 2:
                        try:
                            password, _ = base64.b64decode(split_auth[1]).decode().split(':', 1)
                        except Exception:
                            raise
                    else:
                        raise Exception

                    if password == Config.webhook_secret:
                        return func(*args, **kwargs)
                else:
                    return abort(401)
            else:
                # The Harvey instance does not expect an API key, return the endpoint without validation
                return func(*args, **kwargs)

        return check_auth

    @staticmethod
    def parse_github_webhook(request: requests.Request) -> Tuple[Dict[str, object], int]:
        """Parse a webhook's data. Return success or error status.

        1. Check if the payload is valid JSON
        2. Check if the branch is in the allowed set of branches to run a pipeline from
        3. Check if the webhook secret matches (optional)
        """
        logger = woodchips.get(Config.logger_name)

        success = False
        message = 'Server-side error.'
        status_code = 500
        payload_json = request.json
        payload_data = request.data  # We need this to properly decode the webhook secret
        signature = request.headers.get('X-Hub-Signature')

        if payload_json:
            logger.debug(f'{Webhook.repo_full_name(payload_json)} webhook: {payload_json}')

            # The `ref` field from GitHub looks like `refs/heads/main`, so we split on the final
            # slash to get the branch name and check against the user-allowed list of branches.
            branch_name = payload_json['ref'].rsplit('/', 1)[-1]
            tag_commit = 'refs/tags'

            if Config.webhook_secret and not Webhook.validate_webhook_secret(payload_data, signature):
                message = 'The X-Hub-Signature did not match the WEBHOOK_SECRET.'
                status_code = 403
            elif (branch_name in Config.allowed_branches) or (
                Config.deploy_on_tag and tag_commit in payload_json['ref']
            ):
                Thread(
                    target=Pipeline.run_pipeline,
                    args=(payload_json,),
                ).start()

                message = f'Started pipeline for {Webhook.repo_full_name(payload_json)}'
                status_code = 200
                success = True

                logger.info(message)
            else:
                message = 'Harvey received a webhook event for a branch that is not included in the ALLOWED_BRANCHES.'
                status_code = 422

                logger.debug(message)
        else:
            message = 'Malformed or missing JSON data in webhook.'
            status_code = 422

            logger.debug(message)

        response = {
            'success': success,
            'message': message,
        }, status_code

        return response

    @staticmethod
    def retrieve_pipeline(pipeline_id: str) -> Dict[str, Any]:
        """Retrieve a pipeline's details from a given `pipeline_id`."""
        with SqliteDict(Config.pipelines_store_path) as mydict:
            for key, value in mydict.iteritems():
                transformed_key = key.split('@')
                if pipeline_id == f'{transformed_key[0]}-{transformed_key[1]}':
                    return value
        raise Exception

    @staticmethod
    def retrieve_pipelines(request: flask.Request) -> Dict[str, List[Any]]:
        """Retrieve a list of pipelines until the pagination limit is reached."""
        pipelines: Dict[str, List[Any]] = {'pipelines': []}

        page_size = Api._page_size(request)
        project_name = request.args.get('project')

        with SqliteDict(Config.pipelines_store_path) as mydict:
            for _, value in mydict.iteritems():
                # If a project name is provided, only return pipelines for that project
                if project_name and value['project'] == project_name:
                    pipelines['pipelines'].append(value)
                # This block is for a generic list of pipelines (all pipelines)
                elif not project_name:
                    pipelines['pipelines'].append(value)
                # If a project name was specified but doesn't match, don't add to list
                else:
                    pass

        sorted_pipelines = sorted(pipelines['pipelines'], key=lambda i: i['timestamp'], reverse=True)[:page_size]
        pipelines['pipelines'] = sorted_pipelines

        return pipelines

    @staticmethod
    def retrieve_projects(request: flask.Request) -> Dict[str, List[Any]]:
        """Retrieve a list of projects stored in Harvey by scanning the `projects` directory."""
        projects: Dict[str, List[str]] = {'projects': []}

        page_size = Api._page_size(request)

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

    @staticmethod
    def retrieve_locks(request: flask.Request) -> Dict[str, List[Any]]:
        locks: Dict[str, List[Any]] = {'locks': []}

        page_size = Api._page_size(request)

        with SqliteDict(Config.locks_store_path) as mydict:
            for key, values in mydict.iteritems():
                locks['locks'].append(
                    {
                        'project': key,
                        'locked': values['locked'],
                    }
                )

        sorted_locks = sorted(locks['locks'], key=lambda x: x['project'])[:page_size]
        locks['locks'] = sorted_locks

        return locks

    @staticmethod
    def retrieve_lock(project_name: str) -> Dict[str, bool]:
        """Retrieve the `lock` status of a project via its fully-qualified repo name."""
        try:
            lock_status = Lock.lookup_project_lock(project_name)

            return {'locked': lock_status}
        except Exception:
            raise

    @staticmethod
    def lock_project(project_name: str):
        """Locks the deployments of a project."""
        try:
            lock_status = Lock.update_project_lock(project_name=project_name, locked=True)

            return {'locked': lock_status}
        except Exception:
            raise

    @staticmethod
    def unlock_project(project_name: str):
        """Unlocks the deployments of a project."""
        try:
            lock_status = Lock.update_project_lock(project_name=project_name, locked=False)

            return {'locked': lock_status}
        except Exception:
            raise

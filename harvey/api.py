import base64
from functools import wraps
from threading import Thread
from typing import (
    Dict,
    Tuple,
)

import requests
import woodchips
from flask import (
    abort,
    request,
)

from harvey.config import Config
from harvey.deployments import Deployment
from harvey.errors import HarveyError
from harvey.repos.webhooks import update_webhook
from harvey.webhooks import Webhook


class Api:
    """The Api class contains all the actions accessible via an API endpoint.

    These functions may call out to other modules in Harvey and ultimately serve as the "glue"
    that pulls the entire action together prior to returning whatever the result is to the user via API.
    """

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
                        password, _ = base64.b64decode(split_auth[1]).decode().split(':', 1)
                    else:
                        raise HarveyError('Auth header misconfigured!')

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
        2. Check if the branch is in the allowed set of branches to run a deployment from
        3. Check if the webhook secret matches (optional)
        4. Store the webhook to the database so we can reuse it later
        """
        logger = woodchips.get(Config.logger_name)

        success = False
        message = 'Server-side error.'
        status_code = 500
        payload_json = request.json
        payload_data = request.data  # We need this to properly decode the webhook secret
        signature = request.headers.get('X-Hub-Signature-256')

        if payload_json:
            logger.info(f'Webhook received for: {Webhook.repo_full_name(payload_json)}')

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
                    target=Deployment.run_deployment,
                    args=(payload_json,),
                ).start()

                message = f'Started deployment for {Webhook.repo_full_name(payload_json)}'
                status_code = 200
                success = True

                logger.info(message)

                update_webhook(
                    project_name=Webhook.repo_full_name(payload_json),
                    webhook=payload_json,
                )
            else:
                message = (
                    'Harvey received a webhook event for a branch that is not included in the'
                    f' ALLOWED_BRANCHES for {Webhook.repo_full_name(payload_json)}.'
                )
                status_code = 422

                logger.error(message)
        else:
            message = 'Malformed or missing JSON data in webhook.'
            status_code = 422

            logger.error(message)

        response = {
            'success': success,
            'message': message,
        }, status_code

        return response

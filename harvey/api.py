from threading import Thread
from typing import Dict, Tuple

import requests
import woodchips

from harvey.config import Config
from harvey.pipelines import Pipeline
from harvey.webhooks import Webhook


class Api:
    @staticmethod
    def parse_webhook(request: requests.Request) -> Tuple[Dict[str, object], int]:
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

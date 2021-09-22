import hashlib
import hmac
import os
from threading import Thread

from harvey.globals import Global
from harvey.pipelines import Pipeline

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')


class Webhook:
    @staticmethod
    def parse_webhook(request):
        """Parse a webhook's data. Return success or error status.

        1. Check if the payload is valid JSON
        2. Check if the branch is in the allowed set of branches to run a pipeline from
        3. Check if the webhook secret matches (optional)
        """
        success = False
        message = 'Server-side error.'
        status_code = 500
        payload_json = request.get_json()
        signature = request.headers.get('X-Hub-Signature')
        breakpoint()

        if payload_json:
            # Exit fast when we shouldn't continue
            if WEBHOOK_SECRET and not Webhook.validate_webhook_secret(payload_json, signature):
                message = 'The X-Hub-Signature did not match the WEBHOOK_SECRET.'
                status_code = 403
            # The `ref` field from GitHub looks like `refs/heads/main`, so we split on the final
            # slash to get the branch name and check against the user-allowed list of branches.
            # TODO: We need to allow the user to specify if they want to deploy on allowed branchs or tags
            elif (
                payload_json['ref'].rsplit('/', 1)[-1] in Global.ALLOWED_BRANCHES or 'refs/tags' in payload_json['ref']
            ):
                Thread(
                    target=Pipeline.run_pipeline,
                    args=(payload_json,),
                ).start()
                message = f'Started pipeline for {payload_json["repository"]["name"]}'
                status_code = 200
                success = True
            else:
                message = 'Harvey received a webhook event for a branch that is not included in the ALLOWED_BRANCHES.'
                status_code = 422
        else:
            message = 'Malformed or missing JSON data in webhook.'
            status_code = 422

        response = {
            'success': success,
            'message': message,
        }, status_code

        return response

    @staticmethod
    def validate_webhook_secret(data, signature):
        """Decode and validate a webhook's secret key."""
        secret_validated = False

        if signature:
            secret = bytes(WEBHOOK_SECRET, 'utf-8')
            expected_signature = hmac.new(secret, msg=data, digestmod=hashlib.sha1)
            digest = 'sha1=' + expected_signature.hexdigest()

            if hmac.compare_digest(digest, signature):
                secret_validated = True

        return secret_validated

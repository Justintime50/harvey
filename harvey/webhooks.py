import hashlib
import hmac
import os
from threading import Thread

from harvey.globals import Global
from harvey.pipelines import Pipeline

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')


class Webhook():
    @classmethod
    def parse_webhook(cls, request, use_compose):
        """Parse a webhook's data. Return success or error status.
        """
        # TODO: Restructure this function so it can be used for more than starting a pipeline
        success = False
        message = 'Server-side error.'
        status_code = 500
        payload_data = request.data
        payload_json = request.json
        signature = request.headers.get('X-Hub-Signature')

        if payload_data and payload_json:
            if Global.APP_MODE != 'test' and not cls.decode_webhook(payload_data, signature):
                message = 'The X-Hub-Signature did not match the WEBHOOK_SECRET.'
                status_code = 403
            # TODO: Allow the user to configure whatever branch they'd like to pull from or
            # a list of branches that can be pulled from
            elif payload_json['ref'] in ['refs/heads/master', 'refs/heads/main']:
                if Global.APP_MODE == 'test' or cls.decode_webhook(payload_data, signature):
                    Thread(target=Pipeline.start_pipeline, args=(payload_json, use_compose,)).start()
                    message = f'Started pipeline for {payload_json["repository"]["name"]}'
                    status_code = 200
                    success = True
            else:
                message = 'Harvey can only pull from the "master" or "main" branch of a repo.'
                status_code = 422
        else:
            message = 'Malformed or missing JSON data in webhook.'
            status_code = 422
        response = {
            'success': success,
            'message': message,
        }, status_code
        return response

    @classmethod
    def decode_webhook(cls, data, signature):
        """Decode a webhook's secret key
        """
        if signature:
            secret = bytes(WEBHOOK_SECRET, 'UTF-8')
            mac = hmac.new(secret, msg=data, digestmod=hashlib.sha1)
            digest = 'sha1=' + mac.hexdigest()
            return hmac.compare_digest(digest, signature)
        else:
            return False

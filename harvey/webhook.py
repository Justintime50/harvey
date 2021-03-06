import hashlib
import hmac
import json
import os
from datetime import datetime
from threading import Thread

from harvey.git import Git
from harvey.globals import Global
from harvey.pipeline import Pipeline
from harvey.utils import Utils

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')


class Webhook():
    @classmethod
    def initialize_pipeline(cls, webhook):
        """Initiate the logic for webhooks and pull the project
        """
        start_time = datetime.now()
        preamble = f'Running Harvey v{Global.HARVEY_VERSION}\nPipeline Started: {start_time}'
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}\n'
        print(preamble)
        git_message = (f'New commit by: {Global.repo_commit_author(webhook)}.'
                       f'\nCommit made on repo: {Global.repo_full_name(webhook)}.')
        git = Git.update_git_repo(webhook)
        config = cls.open_project_config(webhook)
        execution_time = f'Startup execution time: {datetime.now() - start_time}\n'
        output = (f'{preamble}\n{pipeline_id}Configuration:\n{json.dumps(config, indent=4)}'
                  f'\n\n{git_message}\n{git}\n{execution_time}')
        print(execution_time)
        return config, output

    @classmethod
    def open_project_config(cls, webhook):
        """Open the project's config file to assign pipeline variables.

        Project configs look like the following:
        {
            "pipeline": "full",
            "language": "php",
            "version": "7.4"
        }
        """
        # TODO: Add the ability to configure projects on the Harvey side
        # (eg: save values to a database via a UI) instead of only from
        # within a JSON file in the repo
        try:
            filename = os.path.join(
                Global.PROJECTS_PATH, Global.repo_full_name(webhook), 'harvey.json'
            )
            with open(filename, 'r') as file:
                config = json.loads(file.read())
                print(json.dumps(config, indent=4))
            return config
        except FileNotFoundError:
            final_output = f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

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
                    Thread(target=cls.start_pipeline, args=(payload_json, use_compose,)).start()
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

    @classmethod
    def start_pipeline(cls, webhook, use_compose=False):
        """Receive a webhook and spin up a pipeline based on the config
        """
        webhook_config, webhook_output = cls.initialize_pipeline(webhook)
        webhook_pipeline = webhook_config['pipeline']

        if webhook_pipeline == 'pull':
            pipeline = Utils.success(webhook_output, webhook)
        elif webhook_pipeline == 'test':
            pipeline = Pipeline.test(webhook_config, webhook, webhook_output)
        elif webhook_pipeline == 'deploy' and use_compose is False:
            pipeline = Pipeline.deploy(webhook_config, webhook, webhook_output)
        elif webhook_pipeline == 'full' and use_compose is True:
            pipeline = Pipeline.full_compose(webhook_config, webhook, webhook_output)
        elif webhook_pipeline == 'deploy' and use_compose is True:
            pipeline = Pipeline.deploy_compose(webhook_config, webhook, webhook_output)
        elif webhook_pipeline == 'full' and use_compose is False:
            pipeline = Pipeline.full(webhook_config, webhook, webhook_output)
        else:
            final_output = webhook_output + '\nError: Harvey could not run, there was no acceptable pipeline specified.'
            pipeline = Utils.kill(final_output, webhook)

        return pipeline

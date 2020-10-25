import json
import os
from datetime import datetime
import hmac
import hashlib
from flask import abort
from threading import Thread
from harvey.pipeline import Pipeline
from harvey.git import Git
from harvey.globals import Global
from harvey.utils import Utils


class Webhook():
    @classmethod
    def init(cls, webhook):
        """Initiate the logic for webhooks and pull the project
        """
        start_time = datetime.now()
        preamble = f'Running Harvey v{Global.HARVEY_VERSION}\n' + \
            f'Pipeline Started: {start_time}'
        pipeline_id = f'Pipeline ID: {Global.repo_commit_id(webhook)}\n'
        print(preamble)
        git_message = (f'New commit by: {Global.repo_commit_author(webhook)}. \
            \nCommit made on repo: {Global.repo_full_name(webhook)}.')
        git = Git.update_git_repo(webhook)

        # Open the project's config file to assign pipeline variables
        try:
            filename = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook),
                                    'harvey.json')
            with open(filename, 'r') as file:
                config = json.loads(file.read())
                print(json.dumps(config, indent=4))
        except FileNotFoundError as fnf_error:
            final_output = f'Error: Harvey could not find "harvey.json" file in \
                {Global.repo_full_name(webhook)}.'
            print(fnf_error)
            Utils.kill(final_output, webhook)

        execution_time = f'Startup execution time: {datetime.now() - start_time}\n'
        output = f'{preamble}\n{pipeline_id}Configuration:\n{json.dumps(config, indent=4)}' + \
            f'\n\n{git_message}\n{git}\n{execution_time}'
        print(execution_time)

        return config, output

    @classmethod
    def parse_webhook(cls, request, target):
        """Initiate details to receive a webhook
        """
        data = request.data
        signature = request.headers.get('X-Hub-Signature')
        parsed_data = json.loads(data)  # TODO: Is this necessary?
        # TODO: Allow the user to configure whatever branch they'd like to pull from
        if parsed_data['ref'] in ['refs/heads/master', 'refs/heads/main']:
            if os.getenv('MODE') == 'test':
                Thread(target=target, args=(parsed_data,)).start()
                return "200"
            if cls.decode_webhook(data, signature):
                Thread(target=target, args=(parsed_data,)).start()
                return "200"
            return abort(403)
        return abort(500, 'Harvey can only pull from the "master" or "main" branch.')

    @classmethod
    def decode_webhook(cls, data, signature):
        """Decode a webhook's secret key
        """
        secret = bytes(os.getenv('WEBHOOK_SECRET'), 'UTF-8')
        mac = hmac.new(secret, msg=data, digestmod=hashlib.sha1)
        return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)

    @classmethod
    def start_pipeline(cls, webhook):
        """Receive a webhook and spin up a pipeline based on the config
        """
        webhook_config, webhook_output = Webhook.init(webhook)

        if webhook_config['pipeline'] == 'test':
            pipeline = Pipeline.test(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'deploy':
            pipeline = Pipeline.deploy(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'full':
            pipeline = Pipeline.full(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'pull':
            pipeline = Utils.success(webhook_output, webhook)
        elif not webhook_config['pipeline']:
            final_output = webhook_output + '\nError: Harvey could not run, \
                there was no pipeline specified.'
            Utils.kill(final_output, webhook)

        return pipeline

    @classmethod
    def start_pipeline_compose(cls, webhook):
        """Receive a webhook and spin up a pipeline based on the config
        """
        webhook_config, webhook_output = Webhook.init(webhook)

        if webhook_config['pipeline'] == 'test':
            pipeline = Pipeline.test(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'deploy':
            pipeline = Pipeline.deploy_compose(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'full':
            pipeline = Pipeline.full_compose(webhook_config, webhook, webhook_output)
        elif webhook_config['pipeline'] == 'pull':
            pipeline = Utils.success(webhook_output, webhook)
        elif not webhook_config['pipeline']:
            final_output = webhook_output + '\nError: Harvey could not run, \
                there was no pipeline specified.'
            Utils.kill(final_output, webhook)

        return pipeline

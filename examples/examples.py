# flake8: noqa
import json

import requests

import harvey

"""API Entrypoint (Webhook)"""
with open('examples/git_webhook.json', 'r') as file:
    data = json.load(file)
    request = requests.post(
        'http://127.0.0.1:5000/pipelines/start',
        json=data,
        headers={
            'Content-Type': 'application/json',
        },
    )
    print(request.json())

# """Retrieve a Pipeline by ID"""
# request = requests.get(
#     'http://127.0.0.1:5000/pipelines/test_owner-test-repo-name',
#     headers={
#         'Content-Type': 'application/json',
#     },
# )
# print(request.json())

# """Retrieve all pipelines"""
# request = requests.get(
#     'http://127.0.0.1:5000/pipelines',
#     headers={
#         'Content-Type': 'application/json',
#     },
# )
# print(request.json())

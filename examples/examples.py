# flake8: noqa
import json

import requests

import harvey

# """API Entrypoint (Webhook)"""
# with open('examples/git_webhook.json', 'r') as file:
#     data = json.load(file)
#     request = requests.post(
#         'http://127.0.0.1:5000/deploy',
#         json=data,
#         headers={
#             'Content-Type': 'application/json',
#         },
#     )
#     print(request.json())

# """Retrieve a Deployment by ID"""
# request = requests.get(
#     'http://127.0.0.1:5000/deployments/justintime50-justinpaulhammond-1',
#     headers={
#         'Content-Type': 'application/json',
#     },
# )
# print(request.json())

# """Retrieve all deployments"""
# request = requests.get(
#     'http://127.0.0.1:5000/deployments',
#     headers={
#         'Content-Type': 'application/json',
#     },
# )
# print(json.dumps(request.json(), indent=4))

"""Retrieve the lock status of a project"""
request = requests.get(
    'http://127.0.0.1:5000/locks/justintime50-justinpaulhammond',
    headers={
        'Content-Type': 'application/json',
    },
)
print(json.dumps(request.json(), indent=4))

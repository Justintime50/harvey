import json
import os

import requests


# USAGE: Run Harvey in the background `just run`, then do `just integration`. Confirm the deployment succeeds


mock_webhook_path = os.path.join('test', 'integration', 'mock_webhook.json')
with open(mock_webhook_path, 'r') as file:
    data = json.load(file)

request = requests.post(
    'http://127.0.0.1:5000/deploy',
    json=data,
    headers={
        'Content-Type': 'application/json',
    },
)

print(request.json())

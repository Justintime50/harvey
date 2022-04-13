import json
import os

import requests

# USAGE: Run Harvey in the background `make run`, then do `make integration_test`. Confirm the pipeline succeeds


mock_webhook_path = os.path.join('test', 'integration', 'mock_webhook.json')
with open(mock_webhook_path, 'r') as file:
    data = json.load(file)
    request = requests.post(
        'http://127.0.0.1:5050/pipelines/start',
        json=data,
        headers={
            'Content-Type': 'application/json',
        },
    )

    print(request.json())

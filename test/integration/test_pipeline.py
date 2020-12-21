import json
import requests
import harvey

# USAGE: Run Harvey in the background `make run`, then do `make integration_test`. Confirm the pipeline succeeds
# TODO: Make integration testing automated


with open('examples/git_webhook.json', 'r') as file:
    data = json.load(file)
    request = requests.post(
        'http://127.0.0.1:5000/pipelines/start',
        json=data,
        headers=harvey.Global.JSON_HEADERS
    )
    print(request.json())

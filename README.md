<div align="center">

# Harvey

The lightweight Docker Compose deployment platform.

[![Build Status](https://github.com/Justintime50/harvey/workflows/build/badge.svg)](https://github.com/Justintime50/harvey/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/harvey/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/harvey?branch=main)
[![PyPi](https://img.shields.io/pypi/v/harvey-ci)](https://pypi.org/project/harvey-ci/)
[![Licence](https://img.shields.io/github/license/justintime50/harvey)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/harvey/showcase.png" alt="Showcase">

</div>

## Why Docker Compose Deployments

I've long been a fan of the simplicity of a `docker-compose` file and its usage. Deploying with systems such as Rancher or a self-hosted GitLab seemed too daunting with uneccessary overhead for simple projects. Why can't I use the same setup in production for spinning up projects as I do during development? Skip the environment variable injection, key stores, and references by having a system such as Harvey spin up my project by simply [using docker-compose in production](https://docs.docker.com/compose/production/).

## How it Works

Harvey receives a webhook from GitHub, pulls in the changes, and deploys them. If you have Slack enabled, Harvey can send you the deployment summary.

1. GitHub webhook fires and is received by Harvey stating that a new commit hit an enabled repo on an allowed branch to be deployed
1. Harvey pulls in your changes and builds your docker image locally
1. Next, Harvey spins up the new docker container and tears down the old one once it's up and running
1. Harvey will then run a container healthcheck to ensure your container is up and running
1. Finally, (if enabled) Harvey can shoot off a message via Slack to notify users the build was a success or not

## Install

Because of the way Harvey was built with Docker (using sockets) this project that builds and orchestrates Docker images and containers cannot itself run in Docker and must be run on your bare-metal OS.

```bash
# Install Harvey via GitHub
git clone https://github.com/Justintime50/harvey.git
make install
cp .env.example .env

# Install Harvey via Pip (untested, may have odd path issues)
pip3 install harvey-ci

# Get Makefile help
make help
```

1. Install Docker & login
1. Ensure you've added your ssh key to the ssh agent: `ssh-add` followed by your password
1. Setup enviornment variables as needed in the `.env` file
1. Enable GitHub webhooks for all your repositories you want to use Harvey with (point them to `http://example.com:5000/pipelines/start`, send the payload as JSON)
    * You could alternatively setup a GitHub Action or other CI flow to only trigger a webhook event once tests pass for instance (must include all the details as if it were generated by GitHub, see [Workflow Webhook](https://github.com/distributhor/workflow-webhook) for an example on how to do this.)

## Usage

```bash
# Run locally
make run

# Run in production
harvey-ci
```

## Things to Know

* Harvey will timeout git clone/pull after 300 seconds
* Harvey will timeout deploys after 30 minutes
* Harvey will shallow clone your project with the latest 10 commits
* Harvey expects the container name to match the GitHub repository name exactly, otherwise the healthcheck will fail

## Harvey Configuration

**Configuration Criteria**
* Each repo either needs a `harvey.json` file in the root directory stored in git (which will be used whenever a GitHub webhook fires) or a `data` key passed into the webhook delivered to Harvey (via something like GitHub Actions). This can be accomplished by using something like [workflow-webhook](https://github.com/distributhor/workflow-webhook) or another homegrown solution (requires the entire webhook payload from GitHub. Harvey will always fallback to the `harvey.json` file if there is no `data` key present)
* You can specify one of `deploy` or `pull` as the pipeline type to run
* This file must follow proper JSON standards (start and end with `{ }`, contain commas after each item, no trailing commas, and be surrounded by quotes)
* Optional: `compose` value can be passed to specify the `docker-compose` file to be used. This key can also be used to specify a base file with additional compose files as overrides (eg: `docker-compose.yml -f docker-compose-prod.yml`).

**harvey.json Example**
```javascript
{
    "pipeline": "deploy",
    "compose": "my-docker-compose-prod.yml"
}
```

**GitHub Action Example**
```yml
deploy:
    needs: ["test", "lint"]
    runs-on: ubuntu-latest
    steps:
        - name: Deploy to Harvey
        if: github.ref == 'refs/heads/main'
        uses: distributhor/workflow-webhook@v2
        env:
            webhook_type: "json-extended"
            webhook_url: ${{ secrets.WEBHOOK_URL }}
            webhook_secret: ${{ secrets.WEBHOOK_SECRET }}
            data: '{ "pipeline": "deploy", "compose" : "my-docker-compose-prod.yml" }'
```

Harvey's entrypoint (eg: `127.0.0.1:5000/pipelines/start`) accepts a webhook from GitHub. If you'd like to simulate a GitHub webhook, simply pass a JSON file like the following example to the Harvey webhook endpoint (ensure you have an environment variable `MODE=test` to bypass the need for a webhook secret and GitHub headers):

```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "justinpaulhammond",
    "full_name": "Justintime50/justinpaulhammond",
    "url": "https://github.com/Justintime50/justinpaulhammond",
    "ssh_url": "git@github.com:Justintime50/justinpaulhammond.git"
  },
  "owner": {
    "name": "Justintime50"
  },
  "commits": [
    {
      "id": "1",
      "author": {
        "name": "Justintime50"
      }
    }
  ],
  "data": {
    "pipeline": "deploy"
  }
}

```

### App Configuration

```
Environment Variables:
    SLACK             Set to "true" to send slack messages
    SLACK_CHANNEL     The Slack channel to send messages to
    SLACK_BOT_TOKEN   The Slackbot token to use to authenticate each request to Slack
    WEBHOOK_SECRET    The Webhook secret required by GitHub (if enabled, leave blank to ignore) to secure your webhooks. Default: disabled
    FILTER_WEBHOOKS   Setting this to `true` will filter webhooks and only accept those from GitHub's list of webhook IP ranges. Default: False
    HOST              The host Harvey will run on. Default: 127.0.0.1
    PORT              The port Harvey will run on. Default: 5000
    DEBUG             Whether the Flask API will run in debug mode or not. Default: False
    ALLOWED_BRANCHES  A comma separated list of branch names that are allowed to trigger pipelines from a webhook event. Default: "main,master"
```

### Example Python Functions

See `examples.py` for all available methods of each class. Almost every usage example is contained in this file.

```bash
venv/bin/python examples/examples.py
```

**Example API Calls**

```bash
# Retrieve a list of pipelines
curl -X GET http://127.0.0.1:5000/pipelines

# Retrieve the pipeline output from Harvey using a commit ID.
curl -X GET http://127.0.0.1:5000/pipeline/f599cde2f2a0ad562bb7982328fe0aeee9d22b1c
```

## Development

```bash
# Get a comprehensive list of development tools
make help
```

<div align="center">

# Harvey

The lightweight Docker Compose deployment platform.

[![Build Status](https://github.com/Justintime50/harvey/workflows/build/badge.svg)](https://github.com/Justintime50/harvey/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/harvey/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/harvey?branch=main)
[![PyPi](https://img.shields.io/pypi/v/harvey-cd)](https://pypi.org/project/harvey-cd/)
[![Licence](https://img.shields.io/github/license/justintime50/harvey)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/harvey/showcase.png" alt="Showcase">

</div>

**NOTE:** Harvey is unstable and rapidly changing. Although used in the wild, it's not completely documented and interfaces are changing frequently. Keep an eye on the project as it continues to mature.

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
cp .env-example .env
make install
```

1. Install Docker & login
1. Ensure you've added your ssh key to the ssh agent: `ssh-add` followed by your password
1. Setup enviornment variables as needed in the `.env` file
1. Enable GitHub webhooks for all your repositories you want to use Harvey with (point them to `http://example.com:5000/deploy`, send the payload as JSON)
   - You could alternatively setup a GitHub Action or other CI flow to only trigger a webhook event once tests pass for instance (must include all the details as if it were generated by GitHub, see [Workflow Webhook](https://github.com/distributhor/workflow-webhook) for an example on how to do this.)

## Usage

```bash
# Run locally for development (runs via Flask)
make run

# Run in production (runs via Gunicorn)
make prod

# Spin up the optional reverse proxy (adjust the URLs in the docker-compose files)
docker compose up -d # local
docker compose -f docker-compose.yml -f docker-compose-prod.yml up -d # prod
```

### Things to Know

- Harvey will timeout git clone/pull after 300 seconds
- Harvey will timeout deploys after 30 minutes
- Harvey will shallow clone your project to the most recent commit
- Harvey expects the container name to match the GitHub repository name exactly, otherwise the healthcheck will fail
- Harvey will rotate internal logs automatically and cleanup; however, uWSGI logs will rotate but do not currently clean themselves up and could balloon with a lot of traffic to the API

### Harvey Configuration

**Configuration Criteria**

- Each repo either needs a `.harvey.yml` file in the root directory stored in git (which will be used whenever a GitHub webhook fires) or a `data` key passed into the webhook delivered to Harvey (via something like GitHub Actions). This can be accomplished by using something like [workflow-webhook](https://github.com/distributhor/workflow-webhook) or another homegrown solution (requires the entire webhook payload from GitHub. Harvey will always fallback to the `.harvey.yml` file if there is no `data` key present)
- You can specify one of `deploy` or `pull` as the `deployment_type` to run (`deploy` is the default)
- This file must follow proper JSON standards (start and end with `{ }`, contain commas after each item, no trailing commas, and be surrounded by quotes)
- Optional: `prod_compose: true` json can be passed to instruct Harvey to use a prod `docker-compose` file in addition to the base compose file. This will run the equivelant of the following when deploying: `docker-compose -f docker-compose.yml -f docker-compose-prod.yml`.

**.harvey.yaml Example**

```yml
deployment_type: deploy
prod_compose: true
healthcheck:
  - container_name_1
  - container_name_2
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
            data: '{ "deployment_type": "deploy", "prod_compose" : true, "healthcheck": ["container_name_1", "container_name_2"] }'
```

Harvey's entrypoint (eg: `127.0.0.1:5000/deploy`) accepts a webhook from GitHub. If you'd like to simulate a GitHub webhook, simply pass a JSON file like the following example to the Harvey webhook endpoint:

```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "justinpaulhammond",
    "full_name": "Justintime50/justinpaulhammond",
    "url": "https://github.com/Justintime50/justinpaulhammond",
    "ssh_url": "git@github.com:Justintime50/justinpaulhammond.git",
    "owner": {
      "name": "Justintime50"
    }
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
    "deployment_type": "deploy"
  }
}
```

### App Configuration

```
Environment Variables:
    USE_SLACK         Set to "true" to send slack messages. Default: False
    SLACK_CHANNEL     The Slack channel to send messages to
    SLACK_BOT_TOKEN   The Slackbot token to use to authenticate each request to Slack
    WEBHOOK_SECRET    The Webhook secret required by GitHub (if enabled, leave blank to ignore) to secure your webhooks. Default: None
    HOST              The host Harvey will run on. Default: 127.0.0.1
    PORT              The port Harvey will run on. Default: 5000
    LOG_LEVEL         The logging level used for the entire application. Default: INFO
    ALLOWED_BRANCHES  A comma separated list of branch names that are allowed to trigger deployments from a webhook event. Default: "main,master"
    PAGINATION_LIMIT  The number of records to return via API. Default: 20
    DEPLOY_TIMEOUT    The number of seconds any given deploy can take before timing out. Default: 600
    GIT_TIMEOUT       The number of seconds any given git operation can take before timing out. Default: 300
    DEPLOY_ON_TAG     A boolean specifying if a tag pushed will trigger a deploy. Default: True
    HARVEY_PATH       The path where Harvey will store projects, logs, and the SQLite databases. Default: ~/harvey
    SENTRY_URL        The URL authorized to receive sentry alerts.
```

### API

The Harvey API can be secured via Basic Auth by setting the `WEBHOOK_SECRET` env var (this secret is used for authenticating a webhook came from GitHub in addition to securing the remaining endpoints).

The following endpoints are available to interact with Harvey:

- `/deployments` (GET) - Retrieve a list of deployments
- `/deployments/{deployment_id}` (GET) - Retrieve the details of a single deployment
- `/deploy` (POST) - Deploy a project with data from a GitHub webhook
- `/projects` (GET) - Retrieve a list of projects
- `/projects/{project_name}/lock` (PUT) - Locks the deployments of a project
- `/projects/{project_name}/unlock` (PUT) - Unlocks the deployments of a project
- `/locks` (GET) - Retrieve a list of locks
- `/locks/{project_name}` (GET) - Retrieve the lock status of a project

### Example Python Functions

See `examples.py` for all available methods of each class. Almost every usage example is contained in this file.

```bash
venv/bin/python examples/examples.py
```

**Example API Calls**

```bash
# Retrieve a list of deployments
curl -X GET http://127.0.0.1:5000/deployments

# Retrieve a deployment from Harvey using the full repo name
curl -X GET http://127.0.0.1:5000/deployments/justintime50-justinpaulhammond
```

## Development

```bash
# Get a comprehensive list of development tools
make help
```

### Releasing

1. Update the version in `Config.harvey_version`
1. Update the version in `setup.py`

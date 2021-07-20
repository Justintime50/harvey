<div align="center">

# Harvey

Your personal CI/CD and Docker orchestration platform.

[![Build Status](https://github.com/Justintime50/harvey/workflows/build/badge.svg)](https://github.com/Justintime50/harvey/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/harvey/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/harvey?branch=main)
[![PyPi](https://img.shields.io/pypi/v/harvey-ci)](https://pypi.org/project/harvey-ci/)
[![Licence](https://img.shields.io/github/license/justintime50/harvey)](LICENSE)

<img src="assets/showcase.png">

</div>

**NOTE:** Harvey is still under development. Star or watch this repo to stay up to date on its development.

Harvey was born because Rancher has too much overhead and GitLab is too RAM hungry to self-host on my small personal server. CI's like Travis are fantastic for open source but pricy for private use and can't be self hosted - deployments across servers looked like a nightmare so I created Harvey - the homegrown CI/CD and Docker orchestrator that kept things simple and lean. Harvey can run multiple pipelines concurrently as it pulls new changes, tests them, builds them, and deploys them in production.

## How it Works

Harvey receives a webhook from GitHub, pulls in the changes, tests them, builds them, then deploys them. If you have Slack enabled, Harvey will send you the pipeline summary.

1. GitHub webhook fires and is received by Harvey stating that a new commit hit an enabled repo
    * Harvey pulls in the new changes for that repo via Git (currently, only commits made to `master` or `main` will prompt a new pipeline to start)
1. Next Harvey tests your code based on the criteria provided
1. Then Harvey builds your docker image locally
1. Next Harvey spins up the new docker container and tears down the old one once it's up and running
1. Then Harvey will run a container healthcheck to ensure your container is up and running and didn't exit on startup
1. Finally, (if enabled) Harvey will shoot off a message to notify users the build was a success or not

Harvey has lightweight testing functionality which is configurable via shell scripts. Harvey builds a unique self-isolated Docker container to test your code and returns the logs from your tests when finished.

## Install

Because of the way Harvey was built with Docker (using sockets) this project that builds and orchestrates Docker images and containers cannot itself run in Docker and must be run on your bare-metal OS.

```bash
# Install Harvey
pip3 install harvey-ci

# Install locally
make install
cp .env.example .env

# Get Makefile help
make help
```

1. Install Docker & login
1. Ensure you've added your ssh key to the ssh agent: `ssh-add` followed by your password
1. Enable logging (see `Logs` below)
1. Setup enviornment variables as needed
1. Enable GitHub webhooks for all your repositories you want to use Harvey with (point them to `http://example.com:5000/pipelines/start`, send the payload as JSON)

### Logs

The [following](https://docs.docker.com/config/containers/logging/json-file/#usage) is required in your Docker daemon file to be able to view logs:

```js
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3" 
    }
}
```

## Usage

```bash
# Run locally
make run

# Run in production
harvey-ci
```

Find the full [docs here](docs/README.md). 

Harvey's entrypoint (eg: `127.0.0.1:5000/pipelines/start`) accepts a webhook from GitHub. If you'd like to simulate a GitHub webhook, simply pass a JSON file like the following example to the Harvey webhook endpoint (ensure you have an environment variable `MODE=test` to bypass the need for a webhook secret and GitHub headers):

```javascript
{
    "repository": {
        "name": "justinpaulhammond.com",
        "full_name": "Justintime50/justinpaulhammond.com",
        "url": "https://github.com/Justintime50/justinpaulhammond.com",
    },
    "owner": {
        "name": "Justintime50",
    }
}
```

### Configuration

```
Environment Variables:
    SLACK           Set to "true" to send slack messages
    SLACK_CHANNEL   The Slack channel to send messages to
    SLACK_BOT_TOKEN The Slackbot token to use to authenticate each request to Slack
    WEBHOOK_SECRET  The Webhook secret required by GitHub (if enabled) to secure your webhooks
    FILTER_WEBHOOKS Setting this to `true` will filter webhooks and only accept those from GitHub's list of webhook IP ranges. Default: False
    MODE            Set to "test" to bypass the header and auth data from GitHub to test. Default: production
    HOST            The host Harvey will run on. Default: 127.0.0.1
    PORT            The port Harvey will run on. Default: 5000
    DEBUG           Whether the Flask API will run in debug mode or not
```

### Example Python Functions

See `examples.py` for all available methods of each class. Almost every usage example is contained in this file.

```bash
venv/bin/python examples/examples.py
```

**Example API Call:**

Retrieve the pipeline output from Harvey using a commit ID.

```bash
curl -X GET http://127.0.0.1:5000/pipeline/f599cde2f2a0ad562bb7982328fe0aeee9d22b1c
```

#### Supported Language Strings

Here are some common examples of testing environments you can use. Any Docker `image:tag` combo should work.

- `python` (3.6, 3.7, 3.8)
- `php` (7.2, 7.3, 7.4)
- `node` (12, 13, 14)
- `ruby` (2.5, 2.6, 2.7)
- `golang` (1.13, 1.14)
- Shell scripts (see below)

**Null Params**
- If no language is provided, an `Alpine Linux` container with `Shellcheck` pre-installed will be used.
- If no version is provided, the `latest` tag will be used.

### Add a Harvey badge to your project

[![Harvey CI](https://img.shields.io/badge/CI%2FCD-Harvey-blue)](https://github.com/Justintime50/harvey)

Add the following to your project's README:

```
[![Harvey CI](https://img.shields.io/badge/CI%2FCD-Harvey-blue)](https://github.com/Justintime50/harvey)
```

## Development

```bash
# Lint the project
make lint

# Run tests
make test

# Run test coverage
make coverage
```

## Resources

- [Use docker-compose in production](https://docs.docker.com/compose/production/)

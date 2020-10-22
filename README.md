<div align="center">

# Harvey

Your personal CI/CD and Docker orchestration platform.

[![Build Status](https://travis-ci.com/Justintime50/harvey.svg?branch=master)](https://travis-ci.com/Justintime50/harvey)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/harvey/badge.svg?branch=master)](https://coveralls.io/github/Justintime50/harvey?branch=master)
[![PyPi](https://img.shields.io/pypi/v/harvey-ci)](https://pypi.org/project/harvey-ci/)
[![Licence](https://img.shields.io/github/license/justintime50/harvey)](LICENSE)

<img src="assets/showcase.png">

</div>

**NOTE:** Harvey is still under development. Star or watch this repo to stay up to date on its development.

Harvey was born because Rancher has too much overhead and GitLab is too RAM hungry to self-host on my small personal server. CI's like Travis are fantastic for open source but pricy for private use and can't be self hosted - deployments across servers looked like a nightmare so I created Harvey - the homegrown CI/CD and Docker orchestrator that kept things simple and lean. Harvey can run multiple pipelines concurrently and initial tests have Harvey's pipelines coming in between just 20 seconds and 2 minutes to pull new changes and test, build, and deploy in production.

## How it Works

Harvey receives a webhook from GitHub, pulls in the changes, tests them, builds them, then deploys them. When all is said and done - we'll even provide you a message to say "job's done".

1. GitHub webhook fires to your self-hosted endpoint stating that a new commit hit an enabled repo
    - Your server pulls in the new changes for that repo via Git
1. Next we test your code based on the criteria provided
1. Then we build your docker image locally
1. Next we spin up the new docker container and tear down the old one once it's up and running, making downtime barely a blip
1. Finally we shoot off a message to notify users the build was a success or not

Harvey has lightweight testing functionality which is configurable via shell scripts. Harvey builds a unique self-isolated Docker container to test your code and returns the logs from your tests when finished.

## Install

Because of the way Harvey was built with Docker (using sockets) this project that builds and orchestrates Docker images and containers cannot itself run in Docker and must be run on your bare-metal OS.

```bash
# Install Harvey
pip3 install harvey-ci

# Install locally
make install

# Get Makefile help
make help
```

1. Install Docker & login
1. Ensure you've added your ssh key to the ssh agent: `ssh-add` followed by your password
1. Enable logging (see below)
1. Setup enviornment variables in `.env`
1. Add webhooks for all your repositories you want to use Harvey with (point them to `http://example.com:5000/harvey`, send the payload as JSON)

**NOTE:** It is not recommended to use Harvey alongside other CI/CD or Docker orchestration platforms on the same machine.

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

Find the full [docs here](docs/README.md). 

Harvey's entrypoint is a webhook (eg: `127.0.0.1:5000/harvey`). Pass GitHub data to Harvey and let it do the rest. If you'd like to simulate a GitHub webhook, simply pass a JSON file like the following example to the Harvey webhook endpoint (ensure you have an environment variable `MODE=test` to bypass the need for a webhook secret):

```javascript
{
    "repository": {
        "name": "justinpaulhammond.com",
        "full_name": "Justintime50/justinpaulhammond.com",
        "url": "https://github.com/Justintime50/justinpaulhammond.com",
    }
    "owner": {
        "name": "Justintime50",
    }
}
```

### Start API Server (for Webhook)

**Start Harvey:**

```bash
make run
```

**Start Ngrok HTTP Bridge:**

This will enable you to bridge from the web to your local machine without changing the default Flask server. Setup your account here: https://ngrok.com.

```bash
# Setup account (one time, go to ngrok.com to setup)
make bridge-auth TOKEN=123...

# Run bridge
make bridge PORT=5000
```

Take the URL Ngrok provides and use that on your webhooks.

### Example Python Functions

See `examples.py` for all available methods of each class. Almost every usage example is contained in this file.

```bash
venv/bin/python examples.py
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

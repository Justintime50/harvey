<div align="center">

# Harvey

Your personal CI/CD and Docker orchestration platform.

[![Build Status](https://travis-ci.org/Justintime50/harvey.svg?branch=master)](https://travis-ci.org/Justintime50/harvey)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)

<img src="assets/showcase.png" style="max-width:200px">

</div>

***NOTE:** Harvey is still in development with MANY items needing attention (see TODO section below). While usable, it's not suggested to use Harvey in production just yet.*

Harvey was born because Rancher has too much overhead and GitLab is too RAM hungry to self-host on my small personal server. CI's like Travis are fantastic for open source but pricy for private use and can't be self hosted - deployments across servers looked like a nightmare so I created Harvey - the homegrown CI/CD and Docker orchestrator that kept things simple and lean. Preliminary tests have Harvey's pipelines coming in between just 30 seconds and 2 minutes to pull new changes and test, build, and deploy in production

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

1. Install Docker & login
1. Ensure you've added your ssh key to the ssh agent for private repos `ssh-add`
1. Enable logging (below)
1. Download this project and see documentation/examples for usage
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

**NOTE:** This has only been tested on macOS.

Find the full [docs here](docs/docs.md). 

Harvey's entrypoint is a webhook (eg: `127.0.0.1:5000/harvey`). Pass GitHub data to Harvey and let it do the rest. If you'd like to simulate a GitHub webhook, simply pass a JSON file like the following example to the Harvey webhook endpoint:

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

### Scripting

See `examples.py` for all available methods of each class. Almost every usage example is contained in this file.

```bash
python3 examples.py
```

### API Server

**Start Server:**
```bash
python3 app.py
```

**Example API Call:**
```bash
curl -X GET http://127.0.0.1:5000/containers/test-project
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

## Resources

- [pylint-exit](https://pypi.org/project/pylint-exit/)

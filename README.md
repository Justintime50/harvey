<div align="center">

# Harvey

Your personal CI/CD and Docker orchestration platform.

[![Build Status](https://travis-ci.org/Justintime50/harvey.svg?branch=master)](https://travis-ci.org/Justintime50/harvey)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)

<img src="assets/showcase.png" style="max-width:250px">

</div>

***NOTE:** Harvey is still in development with MANY items needing attention (see TODO section below). While usable, it's not suggested to use Harvey in production just yet.*

Harvey was born because Rancher has too much overhead and GitLab is too RAM hungry to self-host on my small personal server. CI's like Travis are fantastic for open source but pricy for private use and can't be self hosted - deployments across servers looked like a nightmare so I created Harvey - the homegrown CI/CD and Docker orchestrator that kept things simple and lean. Preliminary tests have Harvey's pipelines coming in between just 30 seconds and 2 minutes to pull new changes and test, build, and deploy in production

Harvey receives a webhook from your version control software of choice, pulls in the changes, tests them, builds them, then deploys them. When all is said and done - we'll even provide you a webhook to say "job's done".

Harvey has lightweight testing functionality which is configurable via shell scripts. Harvey builds a unique self-isolated Docker container to test your code and returns the logs from your tests.

## Install

Because of the way Harvey was built with Docker (using sockets) this project that builds and orchestrates Docker images and containers cannot itself run in Docker and must be run on your bare-metal OS.

1. Install Docker & login
1. Ensure you've added your ssh key to the ssh agent for private repos `ssh-add`
1. Enable logging (below)
1. Download this projec and see documentation/examples for usage
1. Add webhooks for all your repositories you want to use Harvey with (point them to `http://example.com:5000/webhook`, send as json)

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

NOTE: This has only been tested on macOS.

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
curl -X GET http://127.0.0.1:5000/containers/fe3087b2004cac28b820dd48661dd2b4d974293a1b9968a2d8fcc969c0325707
```

#### Supported Language Strings

These are some ideas you can pass. Any docker `image:tag` combo could work. Most common for testing:

- `python` (3.6, 3.7, 3.8)
- `php` (7.2, 7.3, 7.4)
- `node` (12, 13, 14)
- `ruby` (2.5, 2.6, 2.7)
- `golang` (1.13, 1.14)
- Shell scripts (see below)

**Null Params**
- If no language is provided, an `Alpine Linux` container with `Shellcheck` pre-installed will be used.
- If no version is provided, the `latest` tag will be used.

### Documentation

Find the [docs here](dos/docs.md).

## Flow

1. GitHub webhook shoots off to the server stating when a new commit hits master for an enabled repo
    - Git pulls in the changes for that repo
1. Next we test (custom config file, basically a list of bash comands to run - built inside a unique testing container then torn down when done)
1. Next we build your docker image locally
1. Next we spin up the new docker container and replace the old one once it's up and running
1. Finally we shoot off a webhook to notify users the build was a success or not

## Resources

- [pylint-exit](https://pypi.org/project/pylint-exit/)

## TODO

Harvey works! But just barely. There is a LOT to do to make this production ready, especially if used by multiple users:

- Authentication
- Documentation
- Remove `requirements` and put them in setup (prod & dev)
- Add `pylint-exit` as a shell function that can be called upon in `harvey.sh` files
- Fix `latin` encoding for logs which messes with output
- Need to add some logic to flush logs after a certain date?
- Add logic to webhooks to only build on the master branch commits (possibly based on the `refs` attribute in the GitHub json?)
- Introduce try/catch logic to ensure each step of the process works correctly
- Fix the need for double tags when building
- Ensure that tests fail with code `exit 1` so that the build phase/deploy isn't triggered
- Figure out a good way to implement a docker-in-docker concept (which yes, is tricky and bad - but people may want to test their docker containers)
- Explore dockerizing this project (difficult as we use the Docker socket to connect to the docker instance - putting this inside Docker makes connecting difficult)
- Security audit - ensure only authenticated users can do actions, ensure people can only interact with their own images and containers, ensure this application cannot bleed out onto the bare-bones OS
- Fix ALL the TODO items found throughout the project
- Ensure we have the right mix of cache vs no-cache. It's imperative that builds are unique each time and pull in data properly, but it's also important for speed we cache what we can without having residue from previous runs
- Ensure that we aren't leaving dangling images or containers lying around eating up resources and disk space
- Ingest environment variables into the container
- Better logging (include output from everything in the log, not just container logs meaning the build output and each steps output)
- Add a way for each project to be configurable (enabled/disabled, test pipeline or full?)
- Fix passing data via API (error: `TypeError: full_pipeline() missing 2 required positional arguments: 'data' and 'tag'`)

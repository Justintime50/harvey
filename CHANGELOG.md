# CHANGELOG

## v0.24.0 (2023-06-20)

- Adds `runtime` to each deployment attempt's data structure so you can track that over time
- Threads via Harvey are now named (after a project) and can be retrieved via the new `/threads` endpoint
- Fixes a bug where subprocess errors would get clobbered, now output from subprocesses should be printed as a string instead of bytes or being stripped out
- Overhauls the deployment logs to show more or less information depending on if you are running in debug mode or not
- Unifies message structure when sending to Slack, stdout/stderr, and storing to database
- Properly sorts attempts in desc order by `timestamp` so clients don't need to
- Fix a bug where deploys were miscategorized as success when they were actually a failure

## v0.23.0 (2023-03-29)

- Stores webhooks to the database so we can use them later for things like redeploying or reference
- Adds a new `/projects/<project_name>/redeploy` endpoint that allows you to redeploy a project with the local webhook data
- Fixes the long-running and multi-bug issues related to workers, connections, and timeouts stopping harvey from running
  - Simplifies the uwsgi worker config greatly in the hopes to fix thread locking issues (closes #72)
  - Fixes connections getting refused after ~24 hours of uptime due to using the http socket instead of the uwsgi socket
  - Patches segfault on macOS by not using proxies
  - Adjusts various timeouts and limits across the board to assist with edge-case connection and errors related to the server
- Unifies `git_timeout` and `deploy_timeout` to new `operation_timeout` with a default of 300 seconds.
  - Lowers Docker API timeout from 30 seconds to 10 seconds
- Deployments now store the `log`, `timestamp` and `status` keys inside an `attempts` array allowing for multiple saved records of each attempt of a deploy. This is helpful when a commit is redeployed later ensuring that the information from every attempt at deploying a specific commit are retained. Previously, you would only have the most recent details available because the log, status, and timestamp were overridden on each new deploy of the same commit. There is still a `timestamp` at the root level of deployments that will update to the most recent attempt's timestamp (closes #74)
- Overhauls logging
  - Adjusts log sizes from 200kb to 2mb
  - Logs now delete on a uWSGI cron each day if they are older than 14 days
  - We no longer log harvey and uwsgi logs separately since they were both going into the uwsgi logs (closes #78)
- Bumps all dependencies

## v0.22.1 (2023-01-01)

- Adds a try/catch block to the spawned thread in an attempt to kill off failed deployments
- Moves database logic to adopt the `repos` pattern to separate their logic from the rest of the service
- Adds a script to fail `In-Progress` deployments
- Changes the verbose webhook body debug logger to an info logger that only says which repos the webhook originated from
- Log 500 error messages correctly when an endpoint is hit (previously some errors weren't ever bubbling up and were suppressed or lost)
- Don't throw an error when a lock cannot be looked up for a project, log instead (allows for first-time deploys)
- Various other bug fixes and improvements

## v0.22.0 (2022-11-28)

- API has more unified error handling for 5xx error types
- Introduced new `HarveyError` and cleaned up various error handling throughout the app. All messages should now properly get logged when a deployment gets killed, errors raised when Sentries need to be triggered, and various log levels were corrected
- Healthchecks of containers now check when the container was started to ensure that not only are they running, but that they restarted within the last 60 seconds as a part of the deploy
  - Fixed a bug where containers may not properly recreate when their configs or images don't differ from the last deploy
- If a project's lock status cannot be determined, we now kill the process instead of continuing and logging only to ensure we don't steamroll a previous deployment
- Harvey can now distinguish between a system lock and a user lock allowing for user-locked deployments to stay that way even if a deployment fails
- Wraps `store_deployment_details` in a try/except to log out errors with saving details to the DB
- Drops default deployment timeout from 30 minutes to 10 minutes
- Various other improvements and fixes

## v0.21.0 (2022-11-21)

- Bumps `uwsgi` from `2.0.20` to `2.0.21` unlocking Python 3.10 and 3.11 support
- Bumps nginx version
- Changes from process/threads concurrency to dynamic worker concurrency with uwsgi
- Added timeouts and worker kill commands so Harvey will canabolize itself instead of the OS in the case of long running workers or too many requests
- Adds `total_count` to collection responses

## v0.20.1 (2022-07-26)

- Switches from `sha1` webhook secrets from GitHub to `sha256` for increased security and finally adds unit tests for the `validate_webhook_secret` function

## v0.20.0 (2022-07-11)

- Swaps `gunicorn` for `uwsgi` for better performance. This switch also fixes the concurrency deadlock in production
- Harvey now runs as a daemon which should drastically improve performance
- Drops default processes running from 4 to 2
- Adds a check to ensure the `deployment_type` passed was valid and fails if not

## v0.19.0 (2022-05-22)

- Changes name of the PyPI project from `harvey-ci` to `harvey-cd` to better match the nature of the application
- Consolidates all sqlite database tables into a single database file for better performance and disk savings (to properly migrate to using this new database structure, please run the `utils/consolidate_sqlite_databases.py` script which will migrate and consolidate the old database(s) content to the single unified file)

## v0.18.0 (2022-05-01)

### Breaking Changes

- Renamed all occurances of `pipeline` to `deployment` to unify the language used throughout the project and avoid confusion
- The `pipeline` key has been renamed to `deployment_type` in the webhook data. A default of `deploy` has been set where previously there was no default
- The `/pipelines/start` endpoint is now called `/deploy`
- All other `/pipeline` endpoints have been renamed `/deployment`

### Features

- Adds a simple authentication system where endpoints can be protected with the same API key as the webhook secret (uses basic auth)
- Added new `/locks`, `/locks/{project_name}`, `/projects/{project_name}/lock`, and `/projects/{project_name}/unlock` endpoints
- Adds `sentry` integration
- Performance improvements for sorting & paginating large lists of deployments and locks
- Enforces Docker Compose v2 availability by checking during the app bootstrap process

### Bug Fixes

- Fixes a bug where retrieving a lock status may return the wrong value
- Fixes a bug that kills builds when a lock cannot be found (eg: new projects)

### Chores

- Moved all `lock` functionality to its own module

## v0.17.0 (2022-02-12)

- Overhauled the deployment logs to provide more details that are easier to read
- Changed the required `harvey.json` file for each project to `.harvey.yml` (expected fields/values remain the same)
- Sets the default pagination limit down to 20 from 100, adds `PAGINATION_LIMIT` env var to allow customization
- Added new `HARVEY_PATH`, `GIT_TIMEOUT`, `DEPLPOY_TIMEOUT`, and `DEPLOY_ON_TAG` env vars for customization
- Better syncing of the version string for the release and what appears in logs
- Better error handling around `404`s at the API level
- Emojis will now be converted to a fallback string representation in deployment logs while they will remain emojis in Slack messages
- Various bug fixes and refactoring improvements

## v0.16.0 (2022-01-18)

- Added logging with configurable log level
- Use new `docker compose` invocation over older `docker-compose`
- Various code refactor including bug fixes and optimizations, and improved code coverage
  - Cleaned up various dead env variables and documentation
- No longer log progress bars of Docker image builds
- Gracefully handles not being able to find a container or list of containers
- Shallow clone repos to 1 commit instead of 10
- Retry deployments that fail due to local, uncommitted changes present when pulling the repo (closes #38)
- Adds a locking mechanism to deployments when a deployment is in-flight to avoid crashing Docker when multiple `docker compose` commands are run simultaneously for a single project (closes #58)
- Now saves projects to `~/harvey/projects` instead of locally to `harvey/projects`
- Now saves project_logs to `~/harvey/project_logs` instead of locally to `harvey/logs`
- Adds a check to ensure there is a `docker-compose.yml` file present
  - Now supports yaml files ending in both `yml` or `yaml`
- Overhauled the API to allow retrieval of projects in addition to deployments. We now also store more metadata about each object including a timestamp, the full log, the project name, commit, status, etc
- Fixed various path bugs that wouldn't resolve properly on Windows (used `os.path.join()`)
- Changed all datetime/timestamp fields to use `utc` time

## v0.15.0 (2021-11-13)

- Adds the ability to pass Harvey configuration data in a `data` field in the webhook instead of the default `harvey.json` configuration file kept in the repo (either are now options)
- Configuration data now properly gets validated (deployment key and existence)
- Added emojis to the healthcheck messages via Slack
- The `deployments` and `stages` modules were consolidated into `deployments` now that the testing functionality has been removed
- Removed the `filter webhook` functionality as it was prohibitively expensive to do correctly due to the vast number of IPs to guard against
- Reworked how we pulled json data from webhooks to be more straightforward
- We now use the `docker` Python SDK instead of hitting raw socket endpoints (closes #49)
- Adds `gunicorn` for production deployments instead of the development Flask server
- Refactors invocations of subprocesses to not use the shell, no longer change directories but invoke commands from within the context they require
  - Changes the `compose` key to `prod_compose` which now accepts a boolean. We no longer support custom flags to the compose endpoint
- Removes deprecated `/compose` endpoint which has been replaced with the `/start` endpoint
- Adds a new `healthcheck` key on the config which accepts an array of container names to check for when deploying. Harvey will attempt to run healthchecks against these containers and retry a few times if they are not yet running. The deployment will only show as success if we can only get a good healthcheck from the list of containers provided. This new option now allows healthchecks to be run against all containers in the stack instead of the base app alone (great for adding databases, caches, and other containers you may have)
- Various bug fixes

## v0.14.0 (2021-09-06)

### Breaking Changes

- Strips away all non-compose logic - Harvey is now exclusively a `Docker Compose` deployment platform (closes #9, closes #15, closes #19, closes #20, closes #22, closes #24, closes #28, closes #44)
- Strips away the non-functioning testing framework so that we can focus on deployments instead of the full CI/CD landscape
- Removes the poorly integrated `APP_MODE` env variable now that `FILTER_WEBHOOKS` can be toggled

### Other Changes

- Added a `404` error handler to the API
- Rebasing repositories now doesn't assume the branch to rebase against is titled `main`
- Cleaned up all documentation to reflect the breaking changes

## v0.13.1 (2021-08-30)

- Corrected a container naming bug that could make compose containers fail their healthchecks due to mismatched container names
- Small enhancements and cleanup throughout the project

## v0.13.0 (2021-08-26)

- Corrects encoding of test logs, binary data should no longer show in the output (closes #4)
- Overhauls the webhook flow
  - Users can now configure their own comma separated list of `ALLOWED_BRANCHES`
  - Previously a webhook secret was required; now, Harvey will run Deployments without a webhook secret (bypassing decoding and validation of the previously non-existent secret) if there is no `WEBHOOK_SECRET` variable set
  - Additional refactor surrounding how we validate webhook secrets
- Fixed the container healthcheck when using the compose workflow - this was accomplished by making the compose and non-compose container names uniform
- Bumps dependencies (Flask 1 to Flask 2) and now requires Python 3.7. Also removes the `mock` library in favor of the builtin `unittest.mock` library
- Various code refactors and bug fixes

## v0.12.0 (2021-08-17)

- Adds a `/health` endpoint that returns a 200 if Harvey is up and running

## v0.11.0 (2021-07-19)

- Adds the ability to filter webhooks based on origin, this is great if you want to deny all requests that don't come from GitHub. This can be achieved via the `FILTER_WEBHOOKS` environment variable (closes #41)

## v0.10.2 (2021-05-31)

- Pins dependencies

## v0.10.1 (2021-04-12)

- Fixes a bug for brand new repos that weren't yet cloned not being able to read the harvey configuration due to bad ordering of operations

## v0.10.0 (2021-03-10)

- Overhaul the `stages` modules, improved code readability and documentation
- Added unit tests for the `stages` module
- Various bug fixes

## v0.9.0 (2021-03-09)

- Overhauled the Deployment/Webhook modules and removed lots of duplicate code
- Fixed a bug where the deployment timer wouldn't account for startup time (closes #35)
- Added unit tests for the `deployments` module
- Various other bug fixes

## v0.8.2 (2021-03-06)

- Disabled container healthchecks temporarily for docker-compose workflows
- Fixed healthcheck bug for key error

## v0.8.1 (2021-03-06)

- Fixed a bug where webhook secrets couldn't be decoded properly
- Fixed a bug where `.env` files wouldn't load variables properly
- Container healthchecks may have previously failed with a key error if the container wasn't completely running yet. Corrected key error and added retry logic for checking if a container is running after deployments
- Cleaned and refactored various code
- Various additional bug fixes

## v0.8.0 (2020-12-20)

- Refactored the `image` module and added unit tests
- Added a fallback variable for `MODE` set to `production`
- Created `conftest` file for test suite, started shifting fixtures around
- Bumped Docker API version from `1.40` to `1.41`, there should be no change in behavior
- Fixed a bug where if a container didn't exist yet, it would still try to wait, stop, and remove it on the deploy stage. The output would also blow up as it was impossible to do because it didn't exist. Now we check if a container exists prior to running those commands on the deploy stage and skip if no container exists
- Various bug fixes and optimizations

## v0.7.0 (2020-10-26)

- Refactored the `webhook` module and added unit tests
- Refactored webhook logic to return appropriate JSON messages and HTTP status codes
- Fixed bugs where Harvey would blow up when no JSON, malformed JSON, or other webhook details weren't correct
- Fixed a bug that would not catch when a bad deployment name would be given
- Various other bug fixes and improvements
- Added basic tests to API routes

## v0.6.0 (2020-10-25)

- Added unit tests for the `container` module and refactored various code there
- Fixed a bug where the deploy stage of a deployment would fail if a container already existed but was stopped
- Added Harvey badge info to README
- Moved all logic from `app.py` to the `webhook` module, updated endpoint urls to be more verbose and explicit
- Various other bug fixes and code cleanup

## v0.5.0 (2020-10-24)

- Fixed a bug where container names were not being created properly which led to other issues down the deployment flow
- Added a `healthcheck` feature - deployments now run a healthcheck and ensure the container is running (and didn't exit) before declaring the deployment a success
- Various bug fixes and under-the-hood improvements throughout the entire experience
- Removed ngrok executable and all info about ngrok from README

## v0.4.0 (2020-10-23)

- Added a preamble Slack message when a deployment starts. Now you'll get notified when a deployment starts in addition to when it finishes (closes #39)
- Added a `SLACK` env variable so you can decide if you want to send Slack messages or not
- Added unit tests for the `message` module
- Documented all env variables in the README
- Fixed a bug where git clone/pull logic was swapped and wasn't returning anything

## v0.3.0 (2020-10-22)

- Refactored git logic into smaller units
- Added unit tests for `git` module
- Changed `fast forward` git operation to `rebase`

## v0.2.0 (2020-09-18)

- Added testing framework and code coverage
- Added more linting
- Updated Makefile to include more commands
- Various code refactors
- Documentation updates

## v0.1.1 (2020-08-09)

- Added the ability to retrieve a list of deployment ID's and their timestamps
- Restructured `utils` file classes and method names

## v0.1.0 (2020)

- Initial release

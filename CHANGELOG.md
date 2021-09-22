# CHANGELOG

## NEXT RELEASE

* Adds the ability to pass Harvey configuration data in a `data` field in the webhook instead of the default `harvey.json` configuration file kept in the repo (either are now options)
* Configuration data now properly gets validated (pipeline key and existence)
* Added emojis to the healthcheck messages via Slack
* The `pipelines` and `stages` modules were consolidated into `pipelines` now that the testing functionality has been removed
* Removed the `filter webhook` functionality as it was prohibitively expensive to do correctly due to the vast number of IPs to guard against
* Fixed a bug that would pass `None` instead of an empty string to the `docker-compose` command when no `compose` key was used in the config
* Changed from using a combo of `.json` and `.data` on the request payloads and instead use Flask's builtin `.get_json()` function to better handle incoming payload data

## v0.14.0 (2021-09-06)

### Breaking Changes

* Strips away all non-compose logic - Harvey is now exclusively a `Docker Compose` deployment platform (closes #9, closes #15, closes #19, closes #20, closes #22, closes #24, closes #28, closes #44)
* Strips away the non-functioning testing framework so that we can focus on deployments instead of the full CI/CD landscape
* Removes the poorly integrated `APP_MODE` env variable now that `FILTER_WEBHOOKS` can be toggled

### Other Changes

* Added a `404` error handler to the API
* Rebasing repositories now doesn't assume the branch to rebase against is titled `main`
* Cleaned up all documentation to reflect the breaking changes

## v0.13.1 (2021-08-30)

* Corrected a container naming bug that could make compose containers fail their healthchecks due to mismatched container names
* Small enhancements and cleanup throughout the project

## v0.13.0 (2021-08-26)

* Corrects encoding of test logs, binary data should no longer show in the output (closes #4)
* Overhauls the webhook flow
    * Users can now configure their own comma separated list of `ALLOWED_BRANCHES`
    * Previously a webhook secret was required; now, Harvey will run Pipelines without a webhook secret (bypassing decoding and validation of the previously non-existent secret) if there is no `WEBHOOK_SECRET` variable set
    * Additional refactor surrounding how we validate webhook secrets
* Fixed the container healthcheck when using the compose workflow - this was accomplished by making the compose and non-compose container names uniform
* Bumps dependencies (Flask 1 to Flask 2) and now requires Python 3.7. Also removes the `mock` library in favor of the builtin `unittest.mock` library
* Various code refactors and bug fixes

## v0.12.0 (2021-08-17)

* Adds a `/health` endpoint that returns a 200 if Harvey is up and running

## v0.11.0 (2021-07-19)

* Adds the ability to filter webhooks based on origin, this is great if you want to deny all requests that don't come from GitHub. This can be achieved via the `FILTER_WEBHOOKS` environment variable (closes #41)

## v0.10.2 (2021-05-31)

* Pins dependencies

## v0.10.1 (2021-04-12)

* Fixes a bug for brand new repos that weren't yet cloned not being able to read the harvey configuration due to bad ordering of operations

## v0.10.0 (2021-03-10)

* Overhaul the `stages` modules, improved code readability and documentation
* Added unit tests for the `stages` module
* Various bug fixes

## v0.9.0 (2021-03-09)

* Overhauled the Pipeline/Webhook modules and removed lots of duplicate code
* Fixed a bug where the pipeline timer wouldn't account for startup time (closes #35)
* Added unit tests for the `pipelines` module
* Various other bug fixes

## v0.8.2 (2021-03-06)

* Disabled container healthchecks temporarily for docker-compose workflows
* Fixed healthcheck bug for key error

## v0.8.1 (2021-03-06)

* Fixed a bug where webhook secrets couldn't be decoded properly
* Fixed a bug where `.env` files wouldn't load variables properly
* Container healthchecks may have previously failed with a key error if the container wasn't completely running yet. Corrected key error and added retry logic for checking if a container is running after deployments
* Cleaned and refactored various code
* Various additional bug fixes

## v0.8.0 (2020-12-20)

* Refactored the `image` module and added unit tests
* Added a fallback variable for `MODE` set to `production`
* Created `conftest` file for test suite, started shifting fixtures around
* Bumped Docker API version from `1.40` to `1.41`, there should be no change in behavior
* Fixed a bug where if a container didn't exist yet, it would still try to wait, stop, and remove it on the deploy stage. The output would also blow up as it was impossible to do because it didn't exist. Now we check if a container exists prior to running those commands on the deploy stage and skip if no container exists
* Various bug fixes and optimizations

## v0.7.0 (2020-10-26)

* Refactored the `webhook` module and added unit tests
* Refactored webhook logic to return appropriate JSON messages and HTTP status codes
* Fixed bugs where Harvey would blow up when no JSON, malformed JSON, or other webhook details weren't correct
* Fixed a bug that would not catch when a bad pipeline name would be given
* Various other bug fixes and improvements
* Added basic tests to API routes

## v0.6.0 (2020-10-25)

* Added unit tests for the `container` module and refactored various code there
* Fixed a bug where the deploy stage of a pipeline would fail if a container already existed but was stopped
* Added Harvey badge info to README
* Moved all logic from `app.py` to the `webhook` module, updated endpoint urls to be more verbose and explicit
* Various other bug fixes and code cleanup

## v0.5.0 (2020-10-24)

* Fixed a bug where container names were not being created properly which led to other issues down the pipeline flow
* Added a `healthcheck` feature - pipelines now run a healthcheck and ensure the container is running (and didn't exit) before declaring the pipeline a success
* Various bug fixes and under-the-hood improvements throughout the entire experience
* Removed ngrok executable and all info about ngrok from README

## v0.4.0 (2020-10-23)

* Added a preamble Slack message when a pipeline starts. Now you'll get notified when a pipeline starts in addition to when it finishes (closes #39)
* Added a `SLACK` env variable so you can decide if you want to send Slack messages or not
* Added unit tests for the `message` module
* Documented all env variables in the README
* Fixed a bug where git clone/pull logic was swapped and wasn't returning anything

## v0.3.0 (2020-10-22)

* Refactored git logic into smaller units
* Added unit tests for `git` module
* Changed `fast forward` git operation to `rebase`

## v0.2.0 (2020-09-18)

* Added testing framework and code coverage
* Added more linting
* Updated Makefile to include more commands
* Various code refactors
* Documentation updates

## v0.1.1 (2020-08-09)

* Added the ability to retrieve a list of pipeline ID's and their timestamps
* Restructured `utils` file classes and method names

## v0.1.0 (2020)

* Initial release

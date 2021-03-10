# CHANGELOG

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

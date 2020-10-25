# CHANGELOG

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

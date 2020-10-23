# CHANGELOG

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

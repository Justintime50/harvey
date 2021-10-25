PYTHON_BINARY := python3
VIRTUAL_BIN := venv/bin
PROJECT_NAME := harvey

## help - Display help about make targets for this Makefile
help:
	@cat Makefile | grep '^## ' --color=never | cut -c4- | sed -e "`printf 's/ - /\t- /;'`" | column -s "`printf '\t'`" -t

## build - Builds the project in preparation for release
build:
	$(PYTHON_BINARY) setup.py sdist bdist_wheel

## coverage - Test the project and generate an HTML coverage report
coverage:
	$(VIRTUAL_BIN)/pytest --cov=$(PROJECT_NAME) --cov-branch --cov-report=html --cov-report=term-missing

## clean - Remove the virtual environment and clear out .pyc files
clean:
	rm -rf ~/.venv/$(PROJECT_NAME)/ venv
	find . -name '*.pyc' -delete
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

## black - Runs the Black Python formatter against the project
black:
	$(VIRTUAL_BIN)/black $(PROJECT_NAME)/ test/

## black-check - Checks if the project is formatted correctly against the Black rules
black-check:
	$(VIRTUAL_BIN)/black $(PROJECT_NAME)/ test/ --check

## format - Runs all formatting tools against the project
format: black isort lint

## format-check - Checks if the project is formatted correctly against all formatting rules
format-check: black-check isort-check lint

## install - Install the project locally
install:
	$(PYTHON_BINARY) -m venv ~/.venv/$(PROJECT_NAME)/
	ln -snf ~/.venv/$(PROJECT_NAME)/ venv
	$(VIRTUAL_BIN)/pip install -e ."[dev]"

## integration_test - Test the project end-to-end
integration_test:
	venv/bin/python test/integration/test_pipeline.py

## isort - Sorts imports throughout the project
isort:
	$(VIRTUAL_BIN)/isort $(PROJECT_NAME)/ test/

## isort-check - Checks that imports throughout the project are sorted correctly
isort-check:
	$(VIRTUAL_BIN)/isort $(PROJECT_NAME)/ test/ --check-only

## lint - Lint the project
lint:
	$(VIRTUAL_BIN)/flake8 $(PROJECT_NAME)/ test/

## prod - Run the service in production
prod:
	venv/bin/gunicorn --workers=2 wsgi:APP

## run - Run the service locally
run:
	venv/bin/python harvey/app.py

## test - Test the project
test:
	$(VIRTUAL_BIN)/pytest

.PHONY: help build coverage clean black black-check format format-check install integration_test isort isort-check lint prod run test

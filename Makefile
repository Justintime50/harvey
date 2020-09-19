VIRTUALENV := python3 -m venv

## help - Display help about make targets for this Makefile
help:
	@cat Makefile | grep '^## ' --color=never | cut -c4- | sed -e "`printf 's/ - /\t- /;'`" | column -s "`printf '\t'`" -t

## venv - Install the virtual environment
venv:
	$(VIRTUALENV) ~/.venv/harvey/
	ln -snf ~/.venv/harvey/ venv
	venv/bin/pip install -e ."[dev]"

## install - Install the project locally
install: | venv

run: ## Run the service locally
	venv/bin/python harvey/app.py

docker: ## Run the service in a docker container (always builds)
	docker-compose up -d --build

bridge-auth: ## Setup the Ngrok service by providing it your token
	./ngrok authtoken $(TOKEN)

bridge: ## Run the Ngrok service and provide it a port to run on
	./ngrok http $(PORT)

## clean - Remove the virtual environment and clear out .pyc files
clean:
	rm -rf ~/.venv/harvey/ venv
	find . -name '*.pyc' -delete
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

## lint - Lint the project
lint:
	venv/bin/flake8 harvey/*.py
	venv/bin/flake8 test/*.py

## test - Test the project
test:
	venv/bin/pytest

.PHONY: help install clean lint test 

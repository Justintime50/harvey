help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

install: ## Install the complete service locally
	pip3 install -e ."[dev]"
	cp .env.example .env

run: ## Run the service locally
	python3 app.py

docker: ## Run the service in a docker container (always builds)
	docker-compose up -d --build

bridge-auth: ## Setup the Ngrok service by providing it your token
	./ngrok authtoken $(TOKEN)

bridge: ## Run the Ngrok service and provide it a port to run on
	./ngrok http $(PORT)

lint: ## Lint the project
	pylint harvey/*.py

.PHONY: help install run docker lint 

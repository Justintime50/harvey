PYTHON_BINARY := "python3"
VIRTUAL_ENV := "venv"
VIRTUAL_BIN := VIRTUAL_ENV / "bin"
PROJECT_NAME := "harvey"
TEST_DIR := "test"
SCRIPTS_DIR := "scripts"

# Scans the project for security vulnerabilities
bandit:
    {{VIRTUAL_BIN}}/bandit -r {{PROJECT_NAME}}/

# Runs the Black Python formatter against the project
black:
    {{VIRTUAL_BIN}}/black {{PROJECT_NAME}}/ {{TEST_DIR}}/ {{SCRIPTS_DIR}}/

# Checks if the project is formatted correctly against the Black rules
black-check:
    {{VIRTUAL_BIN}}/black {{PROJECT_NAME}}/ {{TEST_DIR}}/ {{SCRIPTS_DIR}}/ --check

# Builds the project in preparation for release
build:
    {{VIRTUAL_BIN}}/python -m build

# Cleans the project
clean:
    rm -rf {{VIRTUAL_ENV}} dist *.egg-info .coverage htmlcov .*cache
    find . -name '*.pyc' -delete

# Test the project and generate an HTML coverage report
coverage:
    {{VIRTUAL_BIN}}/pytest {{TEST_DIR}}/unit --cov={{PROJECT_NAME}} --cov-branch --cov-report=html --cov-report=lcov --cov-report=term-missing --cov-fail-under=75

# Run flake8 checks against the project
flake8:
    {{VIRTUAL_BIN}}/flake8 {{PROJECT_NAME}}/ {{TEST_DIR}}/ {{SCRIPTS_DIR}}/

# Lints the project
lint: black-check isort-check flake8 mypy bandit

# Runs all formatting tools against the project
lint-fix: black isort

# Install the project locally
install:
    {{PYTHON_BINARY}} -m venv {{VIRTUAL_ENV}}
    {{VIRTUAL_BIN}}/pip install -e ."[dev]"

# Test the project end-to-end
integration:
    venv/bin/python {{TEST_DIR}}/integration/test_deployment.py

# Sorts imports throughout the project
isort:
    {{VIRTUAL_BIN}}/isort {{PROJECT_NAME}}/ {{TEST_DIR}}/ {{SCRIPTS_DIR}}/

# Checks that imports throughout the project are sorted correctly
isort-check:
    {{VIRTUAL_BIN}}/isort {{PROJECT_NAME}}/ {{TEST_DIR}}/ {{SCRIPTS_DIR}}/ --check-only

# Run the service in production
prod:
    docker compose -f docker-compose.yml -f docker-compose-prod.yml up -d --build
    venv/bin/uwsgi --ini uwsgi.ini --virtualenv venv

# Run the service locally
run:
    docker compose up -d --build
    venv/bin/python harvey/app.py

# Run mypy type checking on the project
mypy:
    {{VIRTUAL_BIN}}/mypy {{PROJECT_NAME}}/ {{TEST_DIR}}/ {{SCRIPTS_DIR}}/

# Test the project
test:
    {{VIRTUAL_BIN}}/pytest {{TEST_DIR}}/unit

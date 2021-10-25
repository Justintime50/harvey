from unittest.mock import MagicMock

import pytest

import harvey.app as app


@pytest.fixture
def mock_client():
    mock_client = app.APP.test_client()

    return mock_client


@pytest.fixture
def mock_webhook(branch='main'):
    mock_webhook = {
        "ref": f'refs/heads/{branch}',
        "repository": {
            "name": "TEST-repo-name",
            "full_name": "TEST_user/TEST-repo-name",
            "ssh_url": "https://test-url.com",
            "owner": {
                "name": "TEST_owner",
            },
        },
        "commits": [
            {
                "id": 123456,
                "author": {
                    "name": "test_user",
                },
            }
        ],
    }

    return mock_webhook


@pytest.fixture
def mock_webhook_object(branch='main'):
    webhook = MagicMock()
    webhook.json = {
        "ref": f'refs/heads/{branch}',
        "repository": {
            "name": "TEST-repo-name",
        },
    }

    return webhook


@pytest.fixture
def mock_tag():
    mock_tag = 'mock-tag'

    return mock_tag


@pytest.fixture
def mock_output():
    mock_output = 'mock output'

    return mock_output


@pytest.fixture
def mock_project_path():
    mock_project_path = 'projects/test_user/test-repo-name'

    return mock_project_path


# TODO: Make this fixture work and put it in the `test_build_image` test
def mock_config(pipeline='deploy', compose=None):
    mock_config = {
        'pipeline': pipeline,
        'compose': compose if compose else None,
    }

    return mock_config

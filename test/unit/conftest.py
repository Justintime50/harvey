from unittest.mock import MagicMock, Mock

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


# TODO: Move this to a fixture
def mock_response(status=201, json_data={'mock': 'json'}):
    response = MagicMock()
    response.json = MagicMock(
        return_value=json_data,
    )
    response.status_code = status

    return response


# TODO: Make this fixture work and put it in the `test_build_image` test
def mock_config(pipeline='deploy', compose=None):
    mock_config = {
        'pipeline': pipeline,
        'compose': compose if compose else None,
    }

    return mock_config


# TODO: Move this to a fixture
def mock_response_container(status=200, dead=False, paused=False, restarting=False, running=True):
    response = Mock()
    response.json = Mock(
        return_value={
            'State': {
                'Dead': dead,
                'Paused': paused,
                'Restarting': restarting,
                'Running': running,
            }
        }
    )
    response.status_code = status

    return response

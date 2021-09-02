from unittest.mock import MagicMock, Mock

import harvey.app as app
import pytest


@pytest.fixture
def mock_client():
    return app.API.test_client()


@pytest.fixture
def mock_webhook(branch='main'):
    return {
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


@pytest.fixture
def mock_webhook_object(branch='main'):
    webhook = MagicMock()
    webhook.remote_addr = '192.30.252.0'  # A real GitHub IP address
    webhook.json = {
        "ref": f'refs/heads/{branch}',
        "repository": {
            "name": "TEST-repo-name",
        },
    }
    return webhook


@pytest.fixture
def mock_tag():
    return 'mock-tag'


@pytest.fixture
def mock_output():
    return 'mock output'


@pytest.fixture
def mock_project_path():
    return 'projects/test_user/test-repo-name'


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
    return {
        'pipeline': pipeline,
        'compose': compose if compose else None,
    }


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

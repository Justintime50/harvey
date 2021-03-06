import harvey.app as app
import mock
import pytest


@pytest.fixture
def mock_client():
    return app.API.test_client()


@pytest.fixture
def mock_webhook(branch='refs/heads/main'):
    return {
        "ref": branch,
        "repository": {
            "name": "TEST-repo-name",
            "full_name": "TEST_user/TEST-repo-name",
            "ssh_url": "https://test-url.com",
            "owner": {
                    "name": "TEST_owner"
            }
        },
        "commits": [
            {
                "id": 123456,
                "author": {
                    "name": "test_user"
                }
            }
        ]
    }


@pytest.fixture
def mock_webhook_object(branch='refs/heads/main'):
    webhook = mock.MagicMock()
    webhook.json = {
        "ref": branch,
        "repository": {
            "name": "TEST-repo-name",
        }
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
    response = mock.MagicMock()
    response.json = mock.MagicMock(
        return_value=json_data
    )
    response.status_code = status
    return response


# TODO: Make this fixture work and put it in the `test_build_image` test
def mock_config(pipeline='deploy', language='python', version='3.9'):
    return {
        'pipeline': pipeline,
        'language': language,
        'version': version,
    }


# TODO: Move this to a fixture
def mock_response_container(status=200, dead=False, paused=False, restarting=False, running=True):
    response = mock.Mock()
    response.json = mock.Mock(
        return_value={
            'State': {
                'Dead': dead,
                'Paused': paused,
                'Restarting': restarting,
                'Running': running
            }
        }
    )
    response.status_code = status
    return response

import mock
import pytest
from harvey.stage import Stage
from harvey.globals import Global


@pytest.fixture
def _mock_webhook():
    webhook = {
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
    return webhook


MOCK_JSON_CONTAINER_RUNNING = {
    'State': {
        'Dead': False,
        'Paused': False,
        'Restarting': False,
        'Running': True
    }
}
MOCK_JSON_CONTAINER_NOT_RUNNING = {
    'State': {
        'Dead': True,
        'Paused': True,
        'Restarting': True,
        'Running': False
    }
}


@mock.patch('time.sleep', return_value=None)
@mock.patch('harvey.container.Container.inspect_container', return_value=MOCK_JSON_CONTAINER_RUNNING)
def test_run_container_healthcheck_success(mock_container_json, mock_sleep, _mock_webhook):
    healthcheck, healthcheck_message = Stage.run_container_healthcheck(_mock_webhook)
    mock_container_json.assert_called_once_with(Global.docker_project_name(_mock_webhook))
    assert healthcheck is True
    assert healthcheck_message == 'Project healthcheck succeeded!'


@mock.patch('time.sleep', return_value=None)
@mock.patch('harvey.container.Container.inspect_container', return_value=MOCK_JSON_CONTAINER_NOT_RUNNING)
def test_run_container_healthcheck_failed(mock_container_json, _mock_webhook):
    healthcheck, healthcheck_message = Stage.run_container_healthcheck(_mock_webhook)
    mock_container_json.assert_called_once_with(Global.docker_project_name(_mock_webhook))
    assert healthcheck is False
    assert healthcheck_message == 'Project healthcheck failed.'

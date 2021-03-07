from test.unit.conftest import \
    mock_response_container  # Remove once fixtures are fixed

import mock
from harvey.globals import Global
from harvey.stages import Stage


@mock.patch('time.sleep', return_value=None)
@mock.patch('harvey.containers.Container.inspect_container',
            return_value=mock_response_container(status=200, dead=False, paused=False,
                                                 restarting=False, running=True))
def test_run_container_healthcheck_success(mock_container_json, mock_sleep, mock_webhook):
    healthcheck = Stage.run_container_healthcheck(mock_webhook)
    mock_container_json.assert_called_once_with(Global.docker_project_name(mock_webhook))
    assert healthcheck is True


@mock.patch('time.sleep', return_value=None)
@mock.patch('harvey.containers.Container.inspect_container',
            return_value=mock_response_container(status=500, dead=True, paused=False,
                                                 restarting=False, running=False))
def test_run_container_healthcheck_failed(mock_container_json, mock_sleep, mock_webhook):
    healthcheck = Stage.run_container_healthcheck(mock_webhook)
    mock_container_json.assert_called_once_with(Global.docker_project_name(mock_webhook))
    assert healthcheck is False

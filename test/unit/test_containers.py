from test.unit.conftest import mock_response  # Remove once fixtures are fixed
from test.unit.conftest import mock_response_container  # Remove once fixtures are fixed
from unittest.mock import patch

from harvey.containers import Container
from harvey.globals import Global


@patch('requests.get', return_value=mock_response(status=200))
def test_inspect_container(mock_request, mock_tag):
    container = Container.inspect_container(mock_tag)

    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{mock_tag}/json')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


@patch('requests.get', return_value=mock_response(status=200))
def test_list_containers(mock_request, mock_tag):
    container = Container.list_containers()

    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/json')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


@patch('time.sleep', return_value=None)
@patch(
    'harvey.containers.Container.inspect_container',
    return_value=mock_response_container(status=200, dead=False, paused=False, restarting=False, running=True),
)
def test_run_container_healthcheck_success(mock_container_json, mock_sleep, mock_webhook):
    healthcheck = Container.run_container_healthcheck(mock_webhook)

    mock_container_json.assert_called_once_with(Global.repo_name(mock_webhook))
    assert healthcheck is True


@patch('time.sleep', return_value=None)
@patch(
    'harvey.containers.Container.inspect_container',
    return_value=mock_response_container(status=500, dead=True, paused=False, restarting=False, running=False),
)
def test_run_container_healthcheck_failed(mock_container_json, mock_sleep, mock_webhook):
    """This test checks that if a healthcheck fails, we properly retry"""
    healthcheck = Container.run_container_healthcheck(mock_webhook)

    mock_container_json.assert_called_with(Global.repo_name(mock_webhook))
    assert mock_container_json.call_count == 6
    assert healthcheck is False

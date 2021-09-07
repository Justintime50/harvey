from test.unit.conftest import mock_response  # Remove once fixtures are fixed
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

import mock
from harvey.container import Container
from harvey.globals import Global
from test.unit.conftest import mock_response  # Remove once fixtures are fixed


@mock.patch('requests.post', return_value=mock_response(status=201))
def test_create_container(mock_request, mock_tag):
    container = Container.create_container(mock_tag)
    mock_request.assert_called_once_with(
        f'{Global.BASE_URL}containers/create',
        params={'name': mock_tag},
        json={'Image': mock_tag},
        headers=Global.JSON_HEADERS
    )
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 201


@mock.patch('requests.post', return_value=mock_response(status=204))
def test_start_container(mock_request, mock_tag):
    container = Container.start_container(mock_tag)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{mock_tag}/start')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 204


@mock.patch('requests.post', return_value=mock_response(status=204))
def test_stop_container(mock_request, mock_tag):
    container = Container.stop_container(mock_tag)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{mock_tag}/stop')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 204


@mock.patch('requests.get', return_value=mock_response(status=200))
def test_inspect_container(mock_request, mock_tag):
    container = Container.inspect_container(mock_tag)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{mock_tag}/json')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


@mock.patch('requests.get', return_value=mock_response(status=200))
def test_list_containers(mock_request, mock_tag):
    container = Container.list_containers()
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/json')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


@mock.patch('requests.get', return_value=mock_response(status=200))
def test_inspect_container_logs(mock_request):
    Container.inspect_container_logs(1)
    mock_request.assert_called_once_with(
        f'{Global.BASE_URL}containers/1/logs',
        params={'stdout': True, 'stderr': True}
    )


@mock.patch('requests.post', return_value=mock_response(status=200))
def test_wait_container(mock_request, mock_tag):
    container = Container.wait_container(mock_tag)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{mock_tag}/wait')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


@mock.patch('requests.delete', return_value=mock_response(status=204))
def test_remove_container(mock_request, mock_tag):
    container = Container.remove_container(mock_tag)
    mock_request.assert_called_once_with(
        f'{Global.BASE_URL}containers/{mock_tag}',
        json={'force': True},
        headers=Global.JSON_HEADERS
    )
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 204

import mock
from harvey.container import Container
from harvey.globals import Global


def _mock_response(status=201):
    response = mock.Mock()
    response.json = mock.Mock(
        return_value={'mock': 'json'}
    )
    response.status_code = status
    return response


MOCK_TAG = 'mock-tag'


@mock.patch('requests.post', return_value=_mock_response(status=201))
def test_create_container(mock_request):
    container = Container.create_container(MOCK_TAG)
    mock_request.assert_called_once_with(
        f'{Global.BASE_URL}containers/create',
        params={'name': MOCK_TAG},
        json={'Image': MOCK_TAG},
        headers=Global.JSON_HEADERS
    )
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 201


@mock.patch('requests.post', return_value=_mock_response(status=204))
def test_start_container(mock_request):
    container = Container.start_container(MOCK_TAG)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{MOCK_TAG}/start')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 204


@mock.patch('requests.post', return_value=_mock_response(status=204))
def test_stop_container(mock_request):
    container = Container.stop_container(MOCK_TAG)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{MOCK_TAG}/stop')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 204


@mock.patch('requests.get', return_value=_mock_response(status=200))
def test_inspect_container(mock_request):
    container = Container.inspect_container(MOCK_TAG)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{MOCK_TAG}/json')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


@mock.patch('requests.get', return_value=_mock_response(status=200))
def test_list_containers(mock_request):
    container = Container.list_containers()
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/json')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


# TODO: Container logs


@mock.patch('requests.post', return_value=_mock_response(status=200))
def test_wait_container(mock_request):
    container = Container.wait_container(MOCK_TAG)
    mock_request.assert_called_once_with(f'{Global.BASE_URL}containers/{MOCK_TAG}/wait')
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 200


@mock.patch('requests.delete', return_value=_mock_response(status=204))
def test_remove_container(mock_request):
    container = Container.remove_container(MOCK_TAG)
    mock_request.assert_called_once_with(
        f'{Global.BASE_URL}containers/{MOCK_TAG}',
        json={'force': True},
        headers=Global.JSON_HEADERS
    )
    assert container.json() == {'mock': 'json'}
    assert container.status_code == 204

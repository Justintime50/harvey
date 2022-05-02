import pytest


@pytest.mark.parametrize(
    'route',
    [
        'health',
        'deployments',
        'deployments/mock-deployment-id',
        'projects',
        'locks',
        'locks/mock-project-name',
    ],
)
def test_routes_are_reachable_get(mock_client, route):
    response = mock_client.get(route)

    assert response


@pytest.mark.parametrize(
    'route',
    [
        'deploy',
    ],
)
def test_routes_are_reachable_post(mock_client, route):
    response = mock_client.post(route)

    assert response


@pytest.mark.parametrize(
    'route',
    [
        'locks/mock-project-name/enable',
        'locks/mock-project-name/disable',
    ],
)
def test_routes_are_reachable_put(mock_client, route):
    response = mock_client.put(route)

    assert response


def test_routes_not_found(mock_client):
    response = mock_client.get('bad_route')

    assert response.status_code == 404

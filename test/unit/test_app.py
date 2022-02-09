import pytest


@pytest.mark.parametrize(
    'route',
    [
        'health',
        'pipelines',
        'pipelines/mock-pipeline-id',
        'projects',
        'locks/mock-project-name',
    ],
)
def test_routes_are_reachable_get(mock_client, route):
    response = mock_client.get(route)

    assert response


@pytest.mark.parametrize(
    'route',
    [
        'pipelines/start',
    ],
)
def test_routes_are_reachable_post(mock_client, route):
    response = mock_client.post(route)

    assert response


def test_routes_not_found(mock_client):
    response = mock_client.get('bad_route')

    assert response.status_code == 404

from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    'route',
    [
        'health',
        'deployments',
        'deployments/mock-deployment-id',
        'projects',
        'projects/mock-project-name/webhook',
        'locks',
        'locks/mock-project-name',
        'threads',
    ],
)
def test_routes_are_reachable_get(mock_client, route):
    response = mock_client.get(route)

    assert response


@pytest.mark.parametrize(
    'route',
    ['deploy', 'projects/mock-project-name/redeploy'],
)
def test_routes_are_reachable_post(mock_client, route):
    response = mock_client.post(route)

    assert response


@pytest.mark.parametrize(
    'route',
    [
        'projects/mock-project-name/lock',
        'projects/mock-project-name/unlock',
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


@patch('harvey.config.Config.webhook_secret', '123')
def test_routes_not_authorized(mock_client):
    """We have a secret set but don't pass one resulting in a not authorized response."""
    response = mock_client.get('locks')

    assert response.status_code == 401

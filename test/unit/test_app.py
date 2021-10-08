from unittest.mock import patch

import pytest

import harvey.app as app


@pytest.mark.parametrize(
    'route',
    [
        'health',
        'pipelines',
        # 'pipelines/<pipeline_id>',  # TODO: Figure out how to test endpoints with parameters
    ],
)
def test_routes_are_reachable_get(mock_client, route):
    response = mock_client.get(route)

    assert response.status_code == 200


def test_routes_not_found(mock_client):
    response = mock_client.get('bad_route')

    assert response.status_code == 404


@patch('harvey.webhooks.Webhook.parse_webhook')
def test_start_pipeline(mock_parse_webhook):
    # TODO: Long-term, test the status_code and logic
    app.start_pipeline()

    mock_parse_webhook.assert_called_once()

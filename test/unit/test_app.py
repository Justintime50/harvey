import harvey.app as app
import mock
import pytest


@pytest.mark.parametrize(
    'route',
    [
        'pipelines',
        # 'pipelines/<pipeline_id>',  # TODO: Figure out how to test endpoints with parameters

    ]
)
def test_routes_are_reachable_get(mock_client, route):
    response = mock_client.get(route)
    assert response.status_code == 200


@mock.patch('harvey.webhook.Webhook.parse_webhook')
def test_start_pipeline(mock_parse_webhook):
    # TODO: Long-term, test the status_code and logic
    app.start_pipeline()
    mock_parse_webhook.assert_called_once()


@mock.patch('harvey.webhook.Webhook.parse_webhook')
def test_start_pipeline_compose(mock_parse_webhook):
    # TODO: Long-term, test the status_code and logic
    app.start_pipeline_compose()
    mock_parse_webhook.assert_called_once()

import mock
import pytest
import harvey.app as app


MOCK_WEBHOOK = {
    "ref": 'refs/heads/master',
    "repository": {
        "name": "TEST-repo-name",
        "full_name": "TEST_user/TEST-repo-name",
        "ssh_url": "https://test-url.com",
        "owner": {
                "name": "TEST_owner"
        }
    },
    "commits": [
        {
            "id": 123456,
            "author": {
                "name": "test_user"
            }
        }
    ]
}


@pytest.fixture
def client():
    return app.API.test_client()


@pytest.mark.parametrize(
    'route',
    [
        'pipelines',
        # 'pipelines/<pipeline_id>',  # TODO: Figure out how to test endpoints with parameters

    ]
)
def test_routes_are_reachable_get(client, route):
    response = client.get(route)
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

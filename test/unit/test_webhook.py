import mock
import pytest
import hashlib
from harvey.globals import Global
from harvey.webhook import Webhook


@pytest.fixture
def _mock_webhook():
    webhook = {
        "ref": "refs/heads/master",
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
    return webhook


def _mock_config(pipeline='deploy'):
    config = {
        'pipeline': pipeline,
        'language': 'python',
        'version': '3.8',
    }
    return config


@pytest.fixture
def _mock_response(status=200):
    response = mock.MagicMock()
    response.json = {
        "ref": "refs/heads/master",
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
    response.status_code = status
    return response


@pytest.fixture
def _mock_response_no_json(status=200):
    response = mock.MagicMock()
    response.json = None
    response.status_code = status
    return response


MOCK_OUTPUT = 'mock output'


@mock.patch('json.dumps')
@mock.patch('harvey.git.Git.update_git_repo')
@mock.patch('harvey.webhook.Webhook.open_project_config', return_value=_mock_config)
def test_initialize_pipeline(mock_open_project_config, mock_update_git_repo, mock_json_dumps, _mock_webhook):
    webhook_config, webhook_output = Webhook.initialize_pipeline(_mock_webhook)
    mock_open_project_config.assert_called_once_with(_mock_webhook)
    mock_update_git_repo.assert_called_once_with(_mock_webhook)


@mock.patch('json.loads', return_value={'mock': 'json'})
def test_open_project_config(_mock_webhook):
    with mock.patch('builtins.open', mock.mock_open()):
        config = Webhook.open_project_config(_mock_webhook)
        assert config == {'mock': 'json'}


@mock.patch('harvey.utils.Utils.kill')
def test_open_project_config_not_found(mock_utils_kill, _mock_webhook):
    with mock.patch('builtins.open', mock.mock_open()) as mock_open:
        mock_open.side_effect = FileNotFoundError
        Webhook.open_project_config(_mock_webhook)
        mock_utils_kill.assert_called_once_with(
            f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(_mock_webhook)}.',
            _mock_webhook
        )


@mock.patch('harvey.webhook.APP_MODE', 'test')
@mock.patch('harvey.webhook.Webhook.start_pipeline')
def test_parse_webhook(mock_start_pipeline, _mock_response):
    webhook = Webhook.parse_webhook(_mock_response, False)
    assert webhook[0] == {
        'message': 'Started pipeline for TEST-repo-name',
        'success': True
    }
    assert webhook[1] == 200


@mock.patch('harvey.webhook.APP_MODE', 'test')
@mock.patch('harvey.webhook.Webhook.start_pipeline')
def test_parse_webhook_bad_branch(mock_start_pipeline, _mock_response):
    _mock_response.json['ref'] = 'ref/heads/bad_branch'
    webhook = Webhook.parse_webhook(_mock_response, False)
    assert webhook[0] == {
        'message': 'Harvey can only pull from the "master" or "main" branch of a repo.',
        'success': False
    }
    assert webhook[1] == 422


@mock.patch('harvey.webhook.APP_MODE', 'test')
@mock.patch('harvey.webhook.Webhook.start_pipeline')
def test_parse_webhook_no_json(mock_start_pipeline, _mock_response_no_json):
    webhook = Webhook.parse_webhook(_mock_response_no_json, False)
    assert webhook[0] == {
        'message': 'Malformed or missing JSON data in webhook.',
        'success': False
    }
    assert webhook[1] == 422


@mock.patch('harvey.webhook.WEBHOOK_SECRET', '123')
@mock.patch('harvey.webhook.APP_MODE', 'prod')
@pytest.mark.skip('Security is hard, revisit later - but this logic does work')
def test_decode_webhook():
    mock_webhook_secret = bytes('123', 'UTF-8')
    mock_signature = hashlib.sha1(mock_webhook_secret)
    decoded_webhook = Webhook.decode_webhook(_mock_webhook, mock_signature)
    assert decoded_webhook is True


def test_decode_webhook_no_signature():
    decoded_webhook = Webhook.decode_webhook(_mock_webhook, None)
    assert decoded_webhook is False


@mock.patch('harvey.utils.Utils.success')
@mock.patch('harvey.webhook.Webhook.initialize_pipeline', return_value=[_mock_config('pull'), MOCK_OUTPUT])
def test_start_pipeline_pull(mock_initialize_pipeline, mock_utils_success, _mock_webhook):
    Webhook.start_pipeline(_mock_webhook, False)
    mock_initialize_pipeline.assert_called_once_with(_mock_webhook)
    mock_utils_success.assert_called_once_with(MOCK_OUTPUT, _mock_webhook)


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('harvey.pipeline.Pipeline.test')
@mock.patch('harvey.webhook.Webhook.initialize_pipeline', return_value=[_mock_config('test'), MOCK_OUTPUT])
def test_start_pipeline_test(mock_initialize_pipeline, mock_pipeline, mock_utils_kill, _mock_webhook):
    Webhook.start_pipeline(_mock_webhook, False)
    mock_initialize_pipeline.assert_called_once_with(_mock_webhook)
    mock_pipeline.assert_called_once_with(_mock_config('test'), _mock_webhook, MOCK_OUTPUT)


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('harvey.pipeline.Pipeline.deploy')
@mock.patch('harvey.webhook.Webhook.initialize_pipeline', return_value=[_mock_config('deploy'), MOCK_OUTPUT])
def test_start_pipeline_deploy(mock_initialize_pipeline, mock_pipeline, mock_utils_kill, _mock_webhook):
    Webhook.start_pipeline(_mock_webhook, False)
    mock_initialize_pipeline.assert_called_once_with(_mock_webhook)
    mock_pipeline.assert_called_once_with(_mock_config('deploy'), _mock_webhook, MOCK_OUTPUT)


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('harvey.pipeline.Pipeline.full_compose')
@mock.patch('harvey.webhook.Webhook.initialize_pipeline', return_value=[_mock_config('full'), MOCK_OUTPUT])
def test_start_pipeline_full_compose(mock_initialize_pipeline, mock_pipeline, mock_utils_kill, _mock_webhook):
    Webhook.start_pipeline(_mock_webhook, True)
    mock_initialize_pipeline.assert_called_once_with(_mock_webhook)
    mock_pipeline.assert_called_once_with(_mock_config('full'), _mock_webhook, MOCK_OUTPUT)


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('harvey.pipeline.Pipeline.deploy_compose')
@mock.patch('harvey.webhook.Webhook.initialize_pipeline', return_value=[_mock_config('deploy'), MOCK_OUTPUT])
def test_start_pipeline_deploy_compose(mock_initialize_pipeline, mock_pipeline, mock_utils_kill, _mock_webhook):
    Webhook.start_pipeline(_mock_webhook, True)
    mock_initialize_pipeline.assert_called_once_with(_mock_webhook)
    mock_pipeline.assert_called_once_with(_mock_config('deploy'), _mock_webhook, MOCK_OUTPUT)


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('harvey.pipeline.Pipeline.full')
@mock.patch('harvey.webhook.Webhook.initialize_pipeline', return_value=[_mock_config('full'), MOCK_OUTPUT])
def test_start_pipeline_full(mock_initialize_pipeline, mock_pipeline, mock_utils_kill, _mock_webhook):
    Webhook.start_pipeline(_mock_webhook, False)
    mock_initialize_pipeline.assert_called_once_with(_mock_webhook)
    mock_pipeline.assert_called_once_with(_mock_config('full'), _mock_webhook, MOCK_OUTPUT)


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('harvey.webhook.Webhook.initialize_pipeline', return_value=[_mock_config('bad_name'), MOCK_OUTPUT])
def test_start_pipeline_bad_pipeline_name(mock_initialize_pipeline, mock_utils_kill, _mock_webhook):
    Webhook.start_pipeline(_mock_webhook, False)
    mock_initialize_pipeline.assert_called_once_with(_mock_webhook)
    mock_utils_kill.assert_called_once_with(
        f'{MOCK_OUTPUT}\nError: Harvey could not run, there was no acceptable pipeline specified.', _mock_webhook
    )

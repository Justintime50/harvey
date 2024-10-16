import subprocess
from unittest.mock import (
    ANY,
    mock_open,
    patch,
)

from harvey.deployments import Deployment
from harvey.utils.utils import get_utc_timestamp


MOCK_OUTPUT = 'mock output'
MOCK_TIME = get_utc_timestamp()


def mock_config(deployment_type='deploy', prod_compose=False):
    """A mock configuration object similar to what would be stored in `harvey.yaml`."""
    mock_config = {
        'deployment_type': deployment_type,
        'prod_compose': prod_compose,
        'healthcheck': ['mock_container_name'],
    }

    return mock_config


@patch('harvey.deployments.lookup_project_lock')
@patch('harvey.config.Config.use_slack', True)
@patch('harvey.git.Git.update_git_repo')
@patch('harvey.deployments.Deployment.open_project_config', return_value=mock_config())
@patch('harvey.messages.Message.send_slack_message')
def test_initialize_deployment_slack(
    mock_slack_message, mock_open_project_config, mock_update_git_repo, mock_project_lock, mock_webhook
):
    _, _, _ = Deployment.initialize_deployment(mock_webhook)

    mock_slack_message.assert_called_once()


@patch('harvey.deployments.lookup_project_lock')
@patch('harvey.git.Git.update_git_repo')
@patch('harvey.deployments.Deployment.open_project_config', return_value=mock_config())
def test_initialize_deployment(mock_open_project_config, mock_update_git_repo, mock_project_lock, mock_webhook):
    _, _, _ = Deployment.initialize_deployment(mock_webhook)

    mock_open_project_config.assert_called_once_with(mock_webhook)
    mock_update_git_repo.assert_called_once_with(mock_webhook)


@patch('os.path.isfile')
@patch('yaml.safe_load', return_value={'mock': 'json'})
def test_open_project_config(mock_json, mock_isfile):
    # We re-declare a basic mock webhook here because os.path.join on Python 3.7 gets
    # angry with MagicMock objects being passed in
    mock_webhook = {
        "repository": {
            "full_name": "TEST_user/TEST-repo-name",
        },
        "commits": [
            {
                "id": 123456,
                "author": {
                    "name": "test_user",
                },
            }
        ],
    }
    with patch('builtins.open', mock_open()):
        config = Deployment.open_project_config(mock_webhook)

        assert config == {'mock': 'json'}


@patch('harvey.deployments.kill_deployment')
def test_open_project_config_not_found(mock_utils_kill, mock_webhook):
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError
        _ = Deployment.open_project_config(mock_webhook)

        mock_utils_kill.assert_called_once_with(
            message='Harvey could not find a ".harvey.yaml" file!',
            webhook=mock_webhook,
        )


class StringContains(str):
    def __eq__(self, other):
        return self in other


@patch('os.path.exists', return_value=True)
@patch('harvey.deployments.succeed_deployment')
@patch('harvey.deployments.Container.run_container_healthcheck', return_value=True)
@patch('harvey.containers.Container.create_client')
@patch('harvey.deployments.Deployment.deploy', return_value='mock-output')
@patch(
    'harvey.deployments.Deployment.initialize_deployment',
    return_value=[mock_config(deployment_type='pull'), MOCK_OUTPUT, MOCK_TIME],
)
def test_run_deployment_pull(
    mock_initialize_deployment,
    mock_deploy_deployment,
    mock_client,
    mock_healthcheck,
    mock_utils_success,
    mock_path_exists,
    mock_webhook,
):
    """Test the `pull` deployment_type. Pulls happen before getting to deployments, we don't expect a deployment
    to have occured when pulling.
    """
    _ = Deployment.run_deployment(mock_webhook)

    mock_initialize_deployment.assert_called_once_with(mock_webhook)
    mock_deploy_deployment.assert_not_called()
    mock_client.assert_not_called()
    mock_healthcheck.assert_not_called()
    mock_utils_success.assert_called_once()


@patch('os.path.exists', return_value=True)
@patch('harvey.deployments.succeed_deployment')
@patch('harvey.deployments.Container.run_container_healthcheck', return_value=True)
@patch('harvey.containers.Container.create_client')
@patch('harvey.deployments.Deployment.deploy', return_value='mock-output')
@patch(
    'harvey.deployments.Deployment.initialize_deployment',
    return_value=[mock_config(deployment_type='deploy'), MOCK_OUTPUT, MOCK_TIME],
)
def test_run_deployment_deploy(
    mock_initialize_deployment,
    mock_deploy_deployment,
    mock_client,
    mock_healthcheck,
    mock_utils_success,
    mock_path_exists,
    mock_webhook,
):
    _ = Deployment.run_deployment(mock_webhook)

    mock_initialize_deployment.assert_called_once_with(mock_webhook)
    mock_deploy_deployment.assert_called_once_with(mock_config(deployment_type='deploy'), mock_webhook, MOCK_OUTPUT)
    mock_client.assert_called_once()
    mock_healthcheck.assert_called_once()
    mock_utils_success.assert_called_once()


@patch('os.path.exists', return_value=True)
@patch('harvey.deployments.Container.run_container_healthcheck', return_value=True)
@patch('subprocess.check_output')
def test_deploy_stage_success(mock_subprocess, mock_healthcheck, mock_path_exists, mock_webhook):
    _ = Deployment.deploy(mock_config('deploy'), dict(mock_webhook), MOCK_OUTPUT)

    mock_subprocess.assert_called_once_with(
        [
            'docker',
            'compose',
            '-f',
            ANY,
            'up',
            '-d',
            '--build',
            '--force-recreate',
        ],
        stderr=-2,
        text=True,
        encoding='utf8',
        timeout=300,
    )


@patch('os.path.exists', return_value=True)
@patch('harvey.deployments.kill_deployment')
@patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd='subprocess.check_output', timeout=0.1))
def test_deploy_stage_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_path_exists, mock_webhook):
    _ = Deployment.deploy(mock_config('deploy'), dict(mock_webhook), MOCK_OUTPUT)

    mock_utils_kill.assert_called_once()


@patch('os.path.exists', return_value=True)
@patch('harvey.deployments.kill_deployment')
@patch(
    'subprocess.check_output', side_effect=subprocess.CalledProcessError(cmd='subprocess.check_output', returncode=1)
)
def test_deploy_stage_subprocess_error(mock_subprocess, mock_utils_kill, mock_path_exists, mock_webhook):  # noqa
    _ = Deployment.deploy(mock_config('deploy'), dict(mock_webhook), MOCK_OUTPUT)

    mock_utils_kill.assert_called_once()


@patch('os.path.exists', return_value=True)
@patch('harvey.deployments.Container.run_container_healthcheck', return_value=True)
@patch('subprocess.check_output')
def test_deploy_stage_prod_compose_success(mock_subprocess, mock_healthcheck, mock_path_exists, mock_webhook):
    """This test simulates using the `prod_compose` flag and succeeding."""
    config = mock_config('deploy', prod_compose=True)
    _ = Deployment.deploy(config, dict(mock_webhook), MOCK_OUTPUT)

    mock_subprocess.assert_called_once_with(
        [
            'docker',
            'compose',
            '-f',
            ANY,
            '-f',
            ANY,
            'up',
            '-d',
            '--build',
            '--force-recreate',
        ],
        stderr=-2,
        text=True,
        encoding='utf8',
        timeout=300,
    )

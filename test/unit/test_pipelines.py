import subprocess
from datetime import datetime
from test.unit.conftest import mock_config  # Remove once fixtures are fixed
from unittest.mock import mock_open, patch

from harvey.globals import Global
from harvey.pipelines import Pipeline

MOCK_OUTPUT = 'mock output'
MOCK_TIME = datetime.now()


@patch('harvey.globals.Global.SLACK', True)
@patch('harvey.git.Git.update_git_repo')
@patch('harvey.pipelines.Pipeline.open_project_config', return_value=mock_config())
@patch('harvey.messages.Message.send_slack_message')
def test_initialize_pipeline_slack(mock_slack_message, mock_open_project_config, mock_update_git_repo, mock_webhook):
    _, _, _ = Pipeline.initialize_pipeline(mock_webhook)

    mock_slack_message.assert_called_once()


@patch('harvey.git.Git.update_git_repo')
@patch('harvey.pipelines.Pipeline.open_project_config', return_value=mock_config())
def test_initialize_pipeline(mock_open_project_config, mock_update_git_repo, mock_webhook):
    _, _, _ = Pipeline.initialize_pipeline(mock_webhook)

    mock_open_project_config.assert_called_once_with(mock_webhook)
    mock_update_git_repo.assert_called_once_with(mock_webhook)


@patch('json.loads', return_value={'mock': 'json'})
def test_open_project_config(mock_json):
    # We redeclare a basic mock webhook here because os.path.join on Python 3.7 gets
    # angry with MagicMock objects being passed in
    mock_webhook = {
        "repository": {
            "full_name": "TEST_user/TEST-repo-name",
        }
    }
    with patch('builtins.open', mock_open()):
        config = Pipeline.open_project_config(mock_webhook)

        assert config == {'mock': 'json'}


@patch('harvey.utils.Utils.kill')
def test_open_project_config_not_found(mock_utils_kill, mock_webhook):
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError
        _ = Pipeline.open_project_config(mock_webhook)

        mock_utils_kill.assert_called_once_with(
            f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(mock_webhook)}.', mock_webhook
        )


@patch('harvey.utils.Utils.success')
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline', return_value=[mock_config(pipeline='pull'), MOCK_OUTPUT, MOCK_TIME]
)
def test_run_pipeline_pull(mock_initialize_pipeline, mock_utils_success, mock_webhook):
    _ = Pipeline.run_pipeline(mock_webhook)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_utils_success.assert_called_once()


@patch('harvey.utils.Utils.success')
@patch('harvey.pipelines.Container.run_container_healthcheck', return_value=True)
@patch('harvey.pipelines.Pipeline.deploy', return_value='mock-output')
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline',
    return_value=[mock_config(pipeline='deploy'), MOCK_OUTPUT, MOCK_TIME],
)
def test_run_pipeline_deploy(
    mock_initialize_pipeline, mock_deploy_pipeline, mock_healthcheck, mock_utils_success, mock_webhook
):
    _ = Pipeline.run_pipeline(mock_webhook)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_deploy_pipeline.assert_called_once_with(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)
    mock_utils_success.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline',
    return_value=[mock_config(pipeline='bad_name'), MOCK_OUTPUT, MOCK_TIME],
)
def test_run_pipeline_bad_pipeline_name(mock_initialize_pipeline, mock_utils_kill, mock_webhook):
    _ = Pipeline.run_pipeline(mock_webhook)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_utils_kill.assert_called_once_with(
        f'{MOCK_OUTPUT}\nError: Harvey could not run, there was no acceptable pipeline specified.', mock_webhook
    )


@patch('harvey.pipelines.Container.run_container_healthcheck', return_value=True)
@patch('subprocess.check_output')
def test_deploy_compose_stage_success(mock_subprocess, mock_healthcheck, mock_webhook):
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    _ = Pipeline.deploy(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_subprocess.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd=subprocess.check_output, timeout=0.1))
def test_deploy_compose_stage_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):
    _ = Pipeline.deploy(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_utils_kill.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.check_output))
def test_deploy_compose_stage_process_error(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):  # noqa
    _ = Pipeline.deploy(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_utils_kill.assert_called_once()


@patch('harvey.pipelines.Container.run_container_healthcheck', return_value=True)
@patch('subprocess.check_output')
def test_deploy_compose_stage_custom_compose_success(mock_subprocess, mock_healthcheck, mock_webhook):
    """This test simulates having a custom compose command set in the Harvey config
    file - using two docker-compose files for instance
    """
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    config = mock_config('deploy', compose='docker-compose.yml -f docker-compose-prod.yml')
    _ = Pipeline.deploy(config, mock_webhook, MOCK_OUTPUT)

    mock_subprocess.assert_called_once()

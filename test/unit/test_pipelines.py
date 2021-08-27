from datetime import datetime
from test.unit.conftest import mock_config  # Remove once fixtures are fixed
from unittest.mock import mock_open, patch

from harvey.globals import Global
from harvey.pipelines import Pipeline

MOCK_OUTPUT = 'mock output'
MOCK_TIME = datetime.now()


@patch('harvey.pipelines.SLACK', True)
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
def test_open_project_config(mock_webhook):
    with patch('builtins.open', mock_open()):
        config = Pipeline.open_project_config(mock_webhook)

        assert config == {'mock': 'json'}


@patch('harvey.utils.Utils.kill')
def test_open_project_config_not_found(mock_utils_kill, mock_webhook):
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError
        Pipeline.open_project_config(mock_webhook)

        mock_utils_kill.assert_called_once_with(
            f'Error: Harvey could not find a "harvey.json" file in {Global.repo_full_name(mock_webhook)}.', mock_webhook
        )


@patch('harvey.utils.Utils.success')
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline', return_value=[mock_config(pipeline='pull'), MOCK_OUTPUT, MOCK_TIME]
)
def test_start_pipeline_pull(mock_initialize_pipeline, mock_utils_success, mock_webhook):
    _ = Pipeline.start_pipeline(mock_webhook, False)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_utils_success.assert_called_once()


@patch('harvey.utils.Utils.success')
@patch('harvey.pipelines.Pipeline.test')
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline', return_value=[mock_config(pipeline='test'), MOCK_OUTPUT, MOCK_TIME]
)
def test_start_pipeline_test(mock_initialize_pipeline, mock_test_pipeline, mock_utils_success, mock_webhook):
    _ = Pipeline.start_pipeline(mock_webhook, False)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_test_pipeline.assert_called_once_with(mock_config('test'), mock_webhook, MOCK_OUTPUT, MOCK_TIME)
    mock_utils_success.assert_called_once()


@patch('harvey.utils.Utils.success')
@patch('harvey.pipelines.Pipeline.deploy', return_value=['mock-build', 'mock-deploy', 'mock-healthcheck'])
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline',
    return_value=[mock_config(pipeline='deploy'), MOCK_OUTPUT, MOCK_TIME],
)
def test_start_pipeline_deploy(mock_initialize_pipeline, mock_deploy_pipeline, mock_utils_success, mock_webhook):
    _ = Pipeline.start_pipeline(mock_webhook, False)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_deploy_pipeline.assert_called_once_with(mock_config('deploy'), mock_webhook, MOCK_OUTPUT, MOCK_TIME, False)
    mock_utils_success.assert_called_once()


@patch('harvey.utils.Utils.success')
@patch('harvey.pipelines.Pipeline.test')
@patch('harvey.pipelines.Pipeline.deploy', return_value=['mock-build', 'mock-deploy', 'mock-healthcheck'])
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline', return_value=[mock_config(pipeline='full'), MOCK_OUTPUT, MOCK_TIME]
)
def test_start_pipeline_full(
    mock_initialize_pipeline, mock_deploy_pipeline, mock_test_pipeline, mock_utils_success, mock_webhook
):
    _ = Pipeline.start_pipeline(mock_webhook, False)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_test_pipeline.assert_called_once_with(mock_config('full'), mock_webhook, MOCK_OUTPUT, MOCK_TIME)
    mock_deploy_pipeline.assert_called_once_with(mock_config('full'), mock_webhook, MOCK_OUTPUT, MOCK_TIME, False)
    mock_utils_success.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch(
    'harvey.pipelines.Pipeline.initialize_pipeline',
    return_value=[mock_config(pipeline='bad_name'), MOCK_OUTPUT, MOCK_TIME],
)
def test_start_pipeline_bad_pipeline_name(mock_initialize_pipeline, mock_utils_kill, mock_webhook):
    _ = Pipeline.start_pipeline(mock_webhook, False)

    mock_initialize_pipeline.assert_called_once_with(mock_webhook)
    mock_utils_kill.assert_called_once_with(
        f'{MOCK_OUTPUT}\nError: Harvey could not run, there was no acceptable pipeline specified.', mock_webhook
    )


@patch('harvey.stages.TestStage.run')
def test_test_pipeline_success(mock_test_stage, mock_webhook):
    _ = Pipeline.test(mock_config('test'), mock_webhook, MOCK_OUTPUT, MOCK_TIME)

    mock_test_stage.assert_called_once_with(mock_config('test'), mock_webhook, MOCK_OUTPUT)


@patch('harvey.utils.Utils.kill')
@patch('harvey.stages.TestStage.run', return_value='Error: the above command exited with code')
def test_test_pipeline_error(mock_test_stage, mock_utils_kill, mock_webhook):
    _ = Pipeline.test(mock_config('test'), mock_webhook, MOCK_OUTPUT, MOCK_TIME)

    mock_test_stage.assert_called_once_with(mock_config('test'), mock_webhook, MOCK_OUTPUT)
    mock_utils_kill.assert_called_once()


@patch('harvey.stages.DeployStage.run_container_healthcheck', return_value=True)
@patch('harvey.stages.DeployComposeStage.run')
def test_deploy_pipeline_compose_success(mock_deploy_stage, mock_run_container_healthcheck, mock_webhook):
    _, _, healthcheck = Pipeline.deploy(mock_config('deploy'), mock_webhook, MOCK_OUTPUT, MOCK_TIME, True)

    assert healthcheck is True
    mock_deploy_stage.assert_called_once_with(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)


@patch('harvey.stages.DeployStage.run_container_healthcheck', return_value=True)
@patch('harvey.stages.BuildStage.run')
@patch('harvey.stages.DeployStage.run')
def test_deploy_pipeline_no_compose_success(
    mock_deploy_stage, mock_build_stage, mock_run_container_healthcheck, mock_webhook
):
    _, _, healthcheck = Pipeline.deploy(mock_config('deploy'), mock_webhook, MOCK_OUTPUT, MOCK_TIME, False)

    assert healthcheck is True
    mock_build_stage.assert_called_once_with(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)
    mock_deploy_stage.assert_called_once_with(mock_webhook, MOCK_OUTPUT)
    mock_run_container_healthcheck.assert_called_once_with(mock_webhook)


@patch('harvey.utils.Utils.kill')
@patch('harvey.stages.DeployStage.run_container_healthcheck', return_value=False)
@patch('harvey.stages.BuildStage.run')
@patch('harvey.stages.DeployStage.run')
def test_deploy_pipeline_no_compose_failed_healthcheck(
    mock_deploy_stage, mock_build_stage, mock_run_container_healthcheck, mock_utils_kill, mock_webhook
):
    _, _, healthcheck = Pipeline.deploy(mock_config('deploy'), mock_webhook, MOCK_OUTPUT, MOCK_TIME, False)

    assert healthcheck is False
    mock_build_stage.assert_called_once_with(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)
    mock_deploy_stage.assert_called_once_with(mock_webhook, MOCK_OUTPUT)
    mock_run_container_healthcheck.assert_called_once_with(mock_webhook)
    mock_utils_kill.assert_called_once()

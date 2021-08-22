import subprocess
from docker.models.images import ImageCollection
from test.unit.conftest import mock_config  # Remove once fixtures are fixed
from test.unit.conftest import mock_response_container
import multiprocessing
from multiprocessing.process import BaseProcess

import mock
from harvey.globals import Global
from harvey.stages import BuildStage, DeployComposeStage, DeployStage

MOCK_OUTPUT = 'mock output'


@mock.patch('harvey.images.Image.remove_image')
@mock.patch('multiprocessing.Process')
@mock.patch('harvey.utils.Utils.kill') # Need to add this not able to patch process.is_alive()
def test_build_stage_success(mock_kill, mock_build, mock_remove_image, mock_webhook):
    _ = BuildStage.run(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)
    mock_build.is_alive.return_value = False
    mock_remove_image.assert_called_once()
    mock_build.assert_called_once()


@mock.patch('harvey.images.Image.remove_image')
@mock.patch('harvey.utils.Utils.kill')
@mock.patch('multiprocessing.Process', side_effect=multiprocessing.TimeoutError)
def test_build_stage_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_remove_image, mock_project_path, mock_webhook):  # noqa
    _ = BuildStage.run(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_remove_image.assert_called_once()
    mock_utils_kill.assert_called_once()


@mock.patch('harvey.images.Image.remove_image')
@mock.patch('harvey.utils.Utils.kill')
@mock.patch('multiprocessing.Process', side_effect=multiprocessing.TimeoutError)
# @mock.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.check_output))  # noqa
def test_build_stage_process_error(mock_subprocess, mock_utils_kill, mock_remove_image, mock_project_path, mock_webhook):  # noqa
    _ = BuildStage.run(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_remove_image.assert_called_once()
    mock_utils_kill.assert_called_once()


@mock.patch('time.sleep', return_value=None)
@mock.patch('harvey.containers.Container.inspect_container',
            return_value=mock_response_container(status=200, dead=False, paused=False,
                                                 restarting=False, running=True))
def test_run_container_healthcheck_success(mock_container_json, mock_sleep, mock_webhook):
    healthcheck = DeployStage.run_container_healthcheck(mock_webhook)

    mock_container_json.assert_called_once_with(Global.docker_project_name(mock_webhook))
    assert healthcheck is True


@mock.patch('time.sleep', return_value=None)
@mock.patch('harvey.containers.Container.inspect_container',
            return_value=mock_response_container(status=500, dead=True, paused=False,
                                                 restarting=False, running=False))
def test_run_container_healthcheck_failed(mock_container_json, mock_sleep, mock_webhook):
    """This test checks that if a healthcheck fails, we properly retry
    """
    healthcheck = DeployStage.run_container_healthcheck(mock_webhook)

    mock_container_json.assert_called_with(Global.docker_project_name(mock_webhook))
    assert mock_container_json.call_count == 6
    assert healthcheck is False


@mock.patch('subprocess.check_output')
def test_deploy_compose_stage_success(mock_subprocess, mock_webhook):
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    _ = DeployComposeStage.run(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_subprocess.assert_called_once()


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd=subprocess.check_output, timeout=0.1))  # noqa
def test_deploy_compose_stage_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):  # noqa
    _ = DeployComposeStage.run(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_utils_kill.assert_called_once()


@mock.patch('harvey.utils.Utils.kill')
@mock.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.check_output))  # noqa
def test_deploy_compose_stage_process_error(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):  # noqa
    _ = DeployComposeStage.run(mock_config('deploy'), mock_webhook, MOCK_OUTPUT)

    mock_utils_kill.assert_called_once()


@mock.patch('subprocess.check_output')
def test_deploy_compose_stage_custom_compose_success(mock_subprocess, mock_webhook):
    """This test simulates having a custom compose command set in the Harvey config
    file - using two docker-compose files for instance
    """
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    config = mock_config('deploy', compose='docker-compose.yml -f docker-compose-prod.yml')
    _ = DeployComposeStage.run(config, mock_webhook, MOCK_OUTPUT)

    mock_subprocess.assert_called_once()

import os
import subprocess
from unittest.mock import patch

from harvey.git import Git


@patch('os.path.exists', return_value=True)
@patch('harvey.git.Git.pull_repo')
def test_update_git_repo_path_exists(mock_pull_repo, mock_path_exists, mock_project_path, mock_webhook):  # noqa
    Git.update_git_repo(mock_webhook)

    mock_pull_repo.assert_called_once_with(os.path.expanduser(os.path.join('~', mock_project_path)), mock_webhook)


@patch('os.path.exists', return_value=False)
@patch('harvey.git.Git.clone_repo')
def test_update_git_repo_path_does_not_exist(mock_clone_repo, mock_path_exists, mock_project_path, mock_webhook):
    Git.update_git_repo(mock_webhook)

    mock_clone_repo.assert_called_once_with(os.path.expanduser(os.path.join('~', mock_project_path)), mock_webhook)


@patch('logging.Logger.debug')
@patch('subprocess.check_output')
def test_clone_repo(mock_subprocess, mock_logger, mock_project_path, mock_webhook):
    Git.clone_repo(mock_project_path, mock_webhook)

    mock_logger.assert_called()
    mock_subprocess.assert_called_once_with(
        ['git', 'clone', '--depth=1', 'https://test-url.com', 'harvey/projects/test_user/test-repo-name'],
        stdin=None,
        stderr=None,
        timeout=300,
    )


@patch('logging.Logger.error')
@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd='subprocess.check_output', timeout=0.1))
def test_clone_repo_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_logger, mock_project_path, mock_webhook):
    Git.clone_repo(mock_project_path, mock_webhook)

    mock_logger.assert_called()
    mock_utils_kill.assert_called_once()


@patch('logging.Logger.error')
@patch('harvey.utils.Utils.kill')
@patch(
    'subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd='subprocess.check_output')
)
def test_clone_repo_process_error(mock_subprocess, mock_utils_kill, mock_logger, mock_project_path, mock_webhook):
    Git.clone_repo(mock_project_path, mock_webhook)

    mock_logger.assert_called()
    mock_utils_kill.assert_called_once()


@patch('logging.Logger.debug')
@patch('subprocess.check_output')
def test_pull_repo(mock_subprocess, mock_logger, mock_project_path, mock_webhook):
    Git.pull_repo(mock_project_path, mock_webhook)

    mock_logger.assert_called()
    mock_subprocess.assert_called_once_with(
        ['git', '-C', 'harvey/projects/test_user/test-repo-name', 'pull', '--rebase'],
        stdin=None,
        stderr=None,
        timeout=300,
    )


@patch('logging.Logger.error')
@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd='subprocess.check_output', timeout=0.1))
def test_pull_repo_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_logger, mock_project_path, mock_webhook):
    Git.pull_repo(mock_project_path, mock_webhook)

    mock_logger.assert_called()
    mock_utils_kill.assert_called_once()


@patch('logging.Logger.error')
@patch('harvey.utils.Utils.kill')
@patch(
    'subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd='subprocess.check_output')
)
def test_pull_repo_process_error(mock_subprocess, mock_utils_kill, mock_logger, mock_project_path, mock_webhook):
    # TODO: We need to test here that the `stash` command gets called, unsure how to do this since
    # we first have to make `subprocess.check_output` fail then run it again - mocking that
    # in a test seems difficult
    Git.pull_repo(mock_project_path, mock_webhook)

    mock_logger.assert_called()
    mock_utils_kill.call_count == 2  # TODO: This should really only be once if we fail to pull but stash successfully

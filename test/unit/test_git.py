import subprocess
from unittest.mock import patch

from harvey.git import Git


@patch('os.path.exists', return_value=True)
@patch('harvey.git.Git.pull_repo')
def test_update_git_repo_path_exists(mock_pull_repo, mock_path_exists, mock_project_path, mock_webhook):  # noqa
    Git.update_git_repo(mock_webhook)

    mock_pull_repo.assert_called_once_with(mock_project_path, mock_webhook)


@patch('os.path.exists', return_value=False)
@patch('harvey.git.Git.clone_repo')
def test_update_git_repo_path_does_not_exist(mock_clone_repo, mock_path_exists, mock_project_path, mock_webhook):
    Git.update_git_repo(mock_webhook)

    mock_clone_repo.assert_called_once_with(mock_project_path, mock_webhook)


@patch('subprocess.check_output')
def test_clone_repo(mock_subprocess, mock_project_path, mock_webhook):
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    Git.clone_repo(mock_project_path, mock_webhook)

    mock_subprocess.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd=subprocess.check_output, timeout=0.1))
def test_clone_repo_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):
    Git.clone_repo(mock_project_path, mock_webhook)

    mock_utils_kill.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.check_output))
def test_clone_repo_process_error(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):
    Git.clone_repo(mock_project_path, mock_webhook)

    mock_utils_kill.assert_called_once()


@patch('subprocess.check_output')
def test_pull_repo(mock_subprocess, mock_project_path, mock_webhook):
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    Git.pull_repo(mock_project_path, mock_webhook)

    mock_subprocess.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd=subprocess.check_output, timeout=0.1))
def test_pull_repo_subprocess_timeout(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):
    Git.pull_repo(mock_project_path, mock_webhook)

    mock_utils_kill.assert_called_once()


@patch('harvey.utils.Utils.kill')
@patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.check_output))
def test_pull_repo_process_error(mock_subprocess, mock_utils_kill, mock_project_path, mock_webhook):
    Git.pull_repo(mock_project_path, mock_webhook)

    mock_utils_kill.assert_called_once()

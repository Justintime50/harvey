import os
import subprocess
from typing import Any, Dict, List

import woodchips

from harvey.globals import Global
from harvey.utils import LOGGER_NAME, Utils


class Git:
    @staticmethod
    def update_git_repo(webhook: Dict[str, Any]) -> str:
        """Clone or pull repo using Git depending on if it exists or not."""
        project_path = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))

        if os.path.exists(project_path):
            output = Git.pull_repo(project_path, webhook)
        else:
            output = Git.clone_repo(project_path, webhook)

        return output

    @staticmethod
    def clone_repo(project_path: str, webhook: Dict[str, Any]) -> str:
        """Clone a repo into the Harvey projects folder."""
        logger = woodchips.get(LOGGER_NAME)
        decoded_output = ''

        try:
            command = ['git', 'clone', '--depth=1', Global.repo_url(webhook), project_path]
            command_output = Git._git_subprocess(command)
            decoded_output = command_output.decode()
            logger.debug(decoded_output)
        except subprocess.TimeoutExpired:
            final_output = 'Harvey timed out during git clone operation.'
            logger.error(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'Harvey could not clone {Global.repo_full_name(webhook)}.'
            logger.error(final_output)
            Utils.kill(final_output, webhook)

        return decoded_output

    @staticmethod
    def pull_repo(project_path: str, webhook: Dict[str, Any], pull_attempt: int = 1) -> str:
        """Pull updates for a repo in the Harvey projects folder."""
        logger = woodchips.get(LOGGER_NAME)
        decoded_output = ''

        try:
            command = ['git', '-C', project_path, 'pull', '--rebase']
            command_output = Git._git_subprocess(command)
            decoded_output = command_output.decode()
            logger.debug(f'{decoded_output}')
        except subprocess.TimeoutExpired:
            final_output = 'Harvey timed out during git pull operation.'
            logger.error(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            # The biggest offender of this action failing is local, uncommitted changes,
            # try stashing and retry again before failing.
            logger.error(f'Harvey could not pull {Global.repo_full_name(webhook)}.')
            logger.info(f'Attempting to stash {Global.repo_full_name(webhook)} before pulling again...')

            try:
                command = ['git', '-C', project_path, 'stash']
                command_output = Git._git_subprocess(command)
                decoded_output = command_output.decode()
                logger.debug(f'{decoded_output}')
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                final_output = f'Harvey could not stash {Global.repo_full_name(webhook)}.'
                logger.error(final_output)
                Utils.kill(final_output, webhook)

            # Recursively call this function again so we can try pulling after a stash when we fail the first time
            if pull_attempt == 1:
                pull_attempt += 1
                decoded_output = Git.pull_repo(project_path, webhook, pull_attempt)

        return decoded_output

    @staticmethod
    def _git_subprocess(command: List[str]) -> bytes:
        """Runs a git command via subprocess."""
        command_output = subprocess.check_output(
            command,
            stdin=None,
            stderr=None,
            timeout=Global.GIT_TIMEOUT,
        )

        return command_output

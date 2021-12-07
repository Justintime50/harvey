import os
import subprocess
from typing import Any, Dict

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
            # TODO: Fail fast if a repo doesn't exist
            output = Git.clone_repo(project_path, webhook)

        return output

    @staticmethod
    def pull_repo(project_path: str, webhook: Dict[str, Any]) -> str:
        """Pull updates for a repo in the Harvey projects folder."""
        logger = woodchips.get(LOGGER_NAME)
        decoded_output = ''

        try:
            command = ['git', '-C', project_path, 'pull', '--rebase']
            command_output = subprocess.check_output(
                command,
                stdin=None,
                stderr=None,
                timeout=Global.GIT_TIMEOUT,
            )
            decoded_output = command_output.decode()
            logger.debug(f'{decoded_output}')
        except subprocess.TimeoutExpired:
            final_output = 'Harvey timed out during git pull operation.'
            logger.error(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'Harvey could not pull {Global.repo_full_name(webhook)}.'
            logger.error(final_output)
            Utils.kill(final_output, webhook)

        return decoded_output

    @staticmethod
    def clone_repo(project_path: str, webhook: Dict[str, Any]) -> str:
        """Clone a repo into the Harvey projects folder."""
        logger = woodchips.get(LOGGER_NAME)
        decoded_output = ''

        try:
            command = ['git', 'clone', '--depth=10', Global.repo_url(webhook), project_path]
            command_output = subprocess.check_output(
                command,
                stdin=None,
                stderr=None,
                timeout=Global.GIT_TIMEOUT,
            )
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

import os
import subprocess

from harvey.globals import Global
from harvey.utils import Utils


class Git:
    @staticmethod
    def update_git_repo(webhook):
        """Clone or pull repo using Git depending on if it exists or not."""
        project_path = os.path.join(Global.PROJECTS_PATH, Global.repo_full_name(webhook))

        if os.path.exists(project_path):
            output = Git.pull_repo(project_path, webhook)
        else:
            # TODO: Fail fast if a repo doesn't exist
            output = Git.clone_repo(project_path, webhook)

        return output

    @staticmethod
    def pull_repo(project_path, webhook):
        """Pull updates for a repo in the Harvey projects folder."""
        try:
            command = ['git', '-C', project_path, 'pull', '--rebase']
            final_output = subprocess.check_output(
                command,
                stdin=None,
                stderr=None,
                timeout=Global.GIT_TIMEOUT,
            )
            decoded_output = final_output.decode('UTF-8')
            Global.LOGGER.debug(f'{decoded_output}')

            return decoded_output
        except subprocess.TimeoutExpired:
            final_output = '\nHarvey timed out during git pull operation.'
            Global.LOGGER.error(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'\nHarvey could not pull {Global.repo_full_name(webhook)}.'
            Global.LOGGER.error(final_output)
            Utils.kill(final_output, webhook)

    @staticmethod
    def clone_repo(project_path, webhook):
        """Clone a repo into the Harvey projects folder."""
        try:
            command = ['git', 'clone', '--depth=10', Global.repo_url(webhook), project_path]
            final_output = subprocess.check_output(
                command,
                stdin=None,
                stderr=None,
                timeout=Global.GIT_TIMEOUT,
            )
            decoded_output = final_output.decode('UTF-8')
            Global.LOGGER.debug(decoded_output)

            return decoded_output
        except subprocess.TimeoutExpired:
            final_output = '\nHarvey timed out during git clone operation.'
            Global.LOGGER.warning(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'\nHarvey could not clone {Global.repo_full_name(webhook)}.'
            Global.LOGGER.warning(final_output)
            Utils.kill(final_output, webhook)

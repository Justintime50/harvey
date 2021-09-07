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
            final_output = subprocess.check_output(
                f'git -C {project_path} pull --rebase',
                stdin=None,
                stderr=None,
                shell=True,
                timeout=Global.GIT_TIMEOUT,
            )
            print(final_output)

            return final_output.decode('UTF-8')
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out during git pull operation.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'\nError: Harvey could not pull {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

    @staticmethod
    def clone_repo(project_path, webhook):
        """Clone a repo into the Harvey projects folder."""
        try:
            final_output = subprocess.check_output(
                f'git clone --depth=10 {Global.repo_url(webhook)} {project_path}',
                stdin=None,
                stderr=None,
                shell=True,
                timeout=Global.GIT_TIMEOUT,
            )
            print(final_output)

            return final_output.decode('UTF-8')
        except subprocess.TimeoutExpired:
            final_output = 'Error: Harvey timed out during git clone operation.'
            print(final_output)
            Utils.kill(final_output, webhook)
        except subprocess.CalledProcessError:
            final_output = f'\nError: Harvey could not clone {Global.repo_full_name(webhook)}.'
            print(final_output)
            Utils.kill(final_output, webhook)

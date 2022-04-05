import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config


class Lock:
    @staticmethod
    def update_project_lock(project_name: str, locked: bool = False) -> bool:
        """Locks or unlocks the project's deployments to ensure we don't crash Docker with two inflight deployments.
        This function will also create locks for new projects.

        Locking should only happen once a pipeline is begun. A locked deployment should then always be
        unlocked once it's finished regardless of status so another deployment can follow.
        """
        logger = woodchips.get(Config.logger_name)

        locked_string = 'Locking' if locked is True else 'Unlocking'
        logger.info(f'{locked_string} deployments for {project_name}...')
        corrected_project_name = project_name.replace("/", "-")

        with SqliteDict(Config.locks_store_path) as mydict:
            mydict[corrected_project_name.replace("/", "-")] = {
                'locked': locked,
            }

            mydict.commit()

        return locked

    @staticmethod
    def lookup_project_lock(project_name: str) -> bool:
        """Checks if a project is locked or not by its full name."""
        locked_value = False
        corrected_project_name = project_name.replace("/", "-")

        with SqliteDict(Config.locks_store_path) as mydict:
            for key, value in mydict.iteritems():
                if key == corrected_project_name:
                    locked_value = value['locked']
                    return locked_value

        raise ValueError('Lock does not exist!')
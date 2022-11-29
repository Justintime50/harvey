from typing import (
    Any,
    Dict,
    Optional,
)

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.errors import HarveyError


DATABASE_TABLE_NAME = 'locks'


class Lock:
    @staticmethod
    def update_project_lock(project_name: str, locked: bool = False, system_lock: Optional[bool] = True) -> bool:
        """Locks or unlocks the project's deployments to ensure we don't crash Docker with two inflight deployments.
        This function will also create locks for new projects.

        Locking should only happen once a deployment has begun. A locked deployment should then always be
        unlocked once it's finished regardless of status (except for user requested locks) so another deployment can
        follow.
        """
        logger = woodchips.get(Config.logger_name)

        locked_string = 'Locking' if locked is True else 'Unlocking'
        logger.info(f'{locked_string} deployments for {project_name}...')
        formatted_project_name = project_name.replace("/", "-")
        system_lock_value = None if locked is False else system_lock  # Don't allow this to be set if unlocking

        with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
            database_table[formatted_project_name] = {
                'locked': locked,
                'system_lock': system_lock_value,
            }

            database_table.commit()

        return locked

    @staticmethod
    def lookup_project_lock(project_name: str) -> Dict[str, Any]:
        """Looks up a project's lock object by its full name."""
        formatted_project_name = project_name.replace("/", "-")

        with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
            for key, value in database_table.iteritems():
                if key == formatted_project_name:
                    return value
        raise HarveyError('Lock does not exist!')

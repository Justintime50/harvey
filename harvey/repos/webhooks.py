from typing import (
    Any,
    Dict,
)

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.errors import HarveyError


DATABASE_TABLE_NAME = 'webhooks'


def update_webhook(project_name: str, webhook: Dict[str, Any]):
    """Saves the latest webhook to the table so we can use it later for things like redeploying a project
    by pulling in the latest data without the need for GitHub to resend a webhook (we use the last copy we
    got and cache it locally).
    """
    logger = woodchips.get(Config.logger_name)
    logger.debug('Updating local webhook...')

    formatted_project_name = project_name.replace("/", "-")

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        database_table[formatted_project_name] = {
            'webhook': webhook,
        }

        database_table.commit()


def retrieve_webhook(project_name: str) -> Dict[str, Any]:
    """Retrieves a webhook previously received from GitHub stored locally in the database of a project."""
    formatted_project_name = project_name.replace("/", "-")

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        for key, value in database_table.items():
            if key == formatted_project_name:
                return value

    raise HarveyError(f'Webhook does not exist for {project_name}!')

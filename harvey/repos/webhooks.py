from typing import (
    Any,
    Dict,
    Optional,
)

import woodchips
from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config
from harvey.utils.utils import format_project_name


DATABASE_TABLE_NAME = 'webhooks'


def update_webhook(project_name: str, webhook: Dict[str, Any]):
    """Saves the latest webhook to the table so we can use it later for things like redeploying a project
    by pulling in the latest data without the need for GitHub to resend a webhook (we use the last copy we
    got and cache it locally).
    """
    logger = woodchips.get(Config.logger_name)
    logger.debug('Updating local webhook...')

    formatted_project_name = format_project_name(project_name)

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        database_table[formatted_project_name] = {
            'webhook': webhook,
        }

        database_table.commit()


def retrieve_webhook(project_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves a webhook previously received from GitHub stored locally in the database of a project."""
    formatted_project_name = format_project_name(project_name)

    with SqliteDict(filename=Config.database_file, tablename=DATABASE_TABLE_NAME) as database_table:
        for key, value in database_table.items():
            if key == formatted_project_name:
                return value['webhook']

    return None

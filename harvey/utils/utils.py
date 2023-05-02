import datetime

import woodchips

from harvey.config import Config


def format_project_name(project_name: str) -> str:
    """Formats a project name for use throughout Harvey."""
    return project_name.replace("/", "-")


def setup_logger():
    """Sets up a `woodchips` logger instance.

    Typically we would also log to a file via woodchips but logging to console
    will also log directly to uWSGI's logs so we don't do that to avoid double logging.
    """
    logger = woodchips.Logger(
        name=Config.logger_name,
        level=Config.log_level,
    )
    logger.log_to_console(formatter='%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s')


def get_utc_timestamp():
    """Returns the UTC timestamp of right now."""
    return datetime.datetime.now(datetime.timezone.utc)

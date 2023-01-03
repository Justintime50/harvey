import woodchips

from harvey.config import Config


def format_project_name(project_name: str) -> str:
    return project_name.replace("/", "-")


def setup_logger():
    """Sets up a `woodchips` logger instance."""
    logger = woodchips.Logger(
        name=Config.logger_name,
        level=Config.log_level,
    )
    logger.log_to_console()
    logger.log_to_file(location=Config.log_location)

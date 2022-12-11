from typing import Dict

from harvey.repos.locks import (
    lookup_project_lock,
    update_project_lock,
)


def retrieve_lock(project_name: str) -> Dict[str, bool]:
    """Retrieve the `lock` status of a project via its fully-qualified repo name."""
    lock_status = lookup_project_lock(project_name)

    return {'locked': lock_status['locked']}


def lock_project(project_name: str):
    """Locks the deployments of a project via user request."""
    lock_status = update_project_lock(
        project_name=project_name,
        locked=True,
        system_lock=False,
    )

    return {'locked': lock_status}


def unlock_project(project_name: str):
    """Unlocks the deployments of a project."""
    lock_status = update_project_lock(project_name=project_name, locked=False)

    return {'locked': lock_status}

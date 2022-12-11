import os
from typing import (
    Any,
    Dict,
    List,
)

import flask

from harvey.config import Config
from harvey.utils.api_utils import get_page_size


def retrieve_projects(request: flask.Request) -> Dict[str, List[Any]]:
    """Retrieve a list of projects stored in Harvey by scanning the `projects` directory."""
    projects: Dict[str, Any] = {'projects': []}
    project_owners = os.listdir(Config.projects_path)
    page_size = get_page_size(request)

    if '.DS_Store' in project_owners:
        project_owners.remove('.DS_Store')
    for project_owner in project_owners:
        project_names = os.listdir(os.path.join(Config.projects_path, project_owner))
        if '.DS_Store' in project_names:
            project_names.remove('.DS_Store')
        for project_name in project_names:
            final_project_name = f'{project_owner}-{project_name}'
            projects['projects'].append(final_project_name)

        if len(projects['projects']) > page_size:
            break

    projects['total_count'] = len(projects['projects'])

    return projects

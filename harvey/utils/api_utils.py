import flask

from harvey.config import Config


def get_page_size(request: flask.Request) -> int:
    """Return a sane page size based on the request."""
    return (
        int(request.args.get('page_size', Config.pagination_limit))
        if request.args.get('page_size')
        else Config.pagination_limit
    )

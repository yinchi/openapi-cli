"""Utility functions for the click CLI."""

from click import echo, secho, style
from requests import get


class HTTPException(Exception):
    """An HTTP exception."""
    status: int

    def __init__(self, status):
        super().__init__()
        self.status = status


def error(s: str):
    """Print an error message in red font."""
    secho(s, err=True, fg='red')


def style_method(k: str):
    """Style a method string for screen output."""
    k = k.upper()

    if k == 'GET':
        color = 'green'
    elif k == 'POST':
        color = 'cyan'
    elif k == 'PATCH':
        color = 'yellow'
    elif k == 'DELETE':
        color = 'red'
    else:
        color = 'reset'

    return style(k, fg=color)


def get_spec(url: str):
    """Get the OpenAPI specification at {url} and return the JSON object."""

    if url.endswith("/openapi.json"):
        full_url = url
    elif url.endswith("/"):
        full_url = url + "openapi.json"
    else:
        full_url = url + "/openapi.json"

    echo(f"Fetching from {full_url}...")
    echo()

    response = get(url=full_url, timeout=10)
    if (status := response.status_code) != 200:
        raise HTTPException(status)

    obj = response.json()
    _ = obj["openapi"]  # Crudely validate that this in an OpenAPI specification
    return obj


def fix_path(p: str):
    """Fix starting and ending slashes."""
    if not p.startswith('/'):
        p = f"/{p}"
    if p.endswith("/"):
        p = p[:-1]
    return p


def parse_schema(schema: dict):
    """Attempt to get a type string from a schema.

    Use this to parse the inputs of an API endpoint."""

    if 'type' in schema and (t := schema['type']):
        # TODO: show additional detail if 'array' (parse 'items' field)
        return t
    if 'anyOf' in schema and (l := schema['anyOf']):
        lst = []
        for item in l:
            lst.append(
                t if 'type' in item and (t := item['type'])
                else '<unknown type>'
            )
        return ' | '.join(lst)
    if '$ref' in schema and (ref := schema['$ref']):
        ref: str = ref.removeprefix('#/components/schemas/')
        # TODO: parse properties of this referenced schema and generate formatted output
        return ref

    return '<unknown type>'

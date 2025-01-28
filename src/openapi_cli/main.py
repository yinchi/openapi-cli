"""Main application module."""

import click
from click import echo, secho, style, wrap_text
from requests import ConnectionError, JSONDecodeError, Timeout, get

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], color=True)


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
    elif 'anyOf' in schema and (l := schema['anyOf']):
        lst = []
        for item in l:
            lst.append(
                t if 'type' in item and (t := item['type'])
                else '<unknown type>'
            )
        return ' | '.join(lst)
    elif '$ref' in schema and (ref := schema['$ref']):
        ref: str = ref.removeprefix('#/components/schemas/')
        # TODO: parse properties of this referenced schema and generate formatted output
        return ref
    else:
        return '<unknown type>'


@click.group(context_settings=CONTEXT_SETTINGS)
def api():
    """Top-level group for the `click` app."""


@api.command(name='ep')
@click.option('-u', '--url',
              default='http://localhost:8000',
              help='Location of the openapi.json file. Defaults to localhost:8000')
@click.option('-p', '--prefix', default='',
              help="Only show paths starting with <prefix>, e.g. /foo/bar. Default: empty string.")
def endpoints(url: str, prefix: str):
    """Lists all the available endpoints for the OpenAPI specification."""

    prefix = fix_path(prefix)

    try:
        obj = get_spec(url)
        paths: dict = obj["paths"]
        l = max(map(len, paths))
        for path, val in sorted(paths.items()):
            if path.startswith(prefix):
                val: dict
                click.echo(f"{path:{l}}  {', '.join(style_method(k) for k in val.keys())}")

    except HTTPException as e:
        error(f"HTTP error: status {e.status}")
    except ConnectionError:
        error(f"Could not fetch {url}.")
    except Timeout:
        error("Request timed out.")
    except JSONDecodeError:
        error('Could not parse server response as JSON.')
    except KeyError:
        error("Could not parse JSON, is URL a valid OpenAPI specification?")


@api.command(name='d')
@click.option('-u', '--url',
              default='http://localhost:8000',
              help='Location of the openapi.json file. Defaults to localhost:8000')
@click.option('-p', '--path',
              help="Path of the endpoint to query, e.g. /foo/bar.")
@click.option('-m', '--method', default='GET',
              help="Method of the endpoint to query, e.g. GET (default), POST, PATCH, DELETE.")
def describe(url: str, path: str, method: str):
    """Desribe the specified endpoint (path and method)."""

    path = fix_path(path)
    method = method.lower()

    obj = get_spec(url)

    assert path in obj["paths"], f"Path {path} not found."
    assert method in obj["paths"][path], f"Method {method.upper()} not valid for path {path}."
    endpoint = obj["paths"][path][method]

    secho(f"{style_method(method)} {path}", fg='green', nl=False)
    if summary := endpoint["summary"]:
        echo(wrap_text(f": {summary}", width=100))

    if 'tags' in endpoint and (tags := endpoint["tags"]):
        secho("Tags", fg='green', nl=False)
        echo(f": {', '.join(tags)}")

    if 'description' in endpoint and (desc := endpoint["description"]):
        echo()
        echo(wrap_text(desc, width=100))

    if 'parameters' in endpoint and (params := endpoint["parameters"]):
        echo()
        secho("Parameters", fg='yellow')
        secho("----------", fg='yellow')
        for param in params:
            echo(param['name'], nl=False)
            if s := param['schema']:
                echo(f" ({parse_schema(s)})")

                if 'title' in s and (t := s['title']):
                    echo(wrap_text(t, width=100,
                                   initial_indent=' '*4,
                                   subsequent_indent=' '*4))

    if 'requestBody' in endpoint and (body := endpoint['requestBody']):
        echo()
        secho("Request body", fg='yellow')
        secho("------------", fg='yellow')

        if 'content' in body and (c := body['content']):
            c:dict
            for k, v in c.items():
                if 'schema' in v and (s := v['schema']):
                    echo(f" {parse_schema(s)} ({k})")
                    echo()

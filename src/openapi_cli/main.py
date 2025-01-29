"""Main application module."""

import click
from click import echo, secho, wrap_text
from requests import ConnectionError, JSONDecodeError, Timeout

from .util import HTTPException, error, fix_path, get_spec, parse_schema, style_method

CONTEXT_SETTINGS = {"help_option_names": ['-h', '--help'], "color": True}


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

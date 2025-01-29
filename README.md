# CLI for working with APIs using the OpenAPI specifications

![GitHub License](https://img.shields.io/github/license/yinchi/openapi-cli)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fyinchi%2Fopenapi-cli%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/yinchi/openapi-cli/main?label=last%20commit%20(main))


Author: Yin-Chi Chan

> [!WARNING]
> This Python package is very preliminary. There will be bugs(!), and not all OpenAPI specifications will be able to be parsed.
>
> Check [TODO.md](TODO.md) for a list of features to be added.

### Running the CLI app

- Option 1: `uv run`
    ```bash
    cd /path/to/project
    uv run openapi <args>
    ```
- Option 2: global install with `pipx` (editable)
  ```bash
  cd /path/to/project
  pipx install -e .
  openapi <args>
  ```

### Documentation

Run `openapi <cmd> -h` to see usage information for each command or `openapi -h` for a list of commands.

### Screenshot

![Screenshot of the openapi CLI app](docs/img/screenshot_readme.png)

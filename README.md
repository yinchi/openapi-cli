# CLI for working with OpenAPI specifications

Author: Yin-Chi Chan

### Running the CLI app

- Option 1: `uv run`
    ```bash
    cd /path/to/project
    uv run openapi <args>
    ```
- Option 2: global install with `pipx`
  ```bash
  cd /path/to/project
  uv build
  pipx install dist/openapi<...>.whl
  openapi <args>
  ```

# Development
See the root level
## Installation
Install uv with `pip install uv`

## Type Checking
From `/backend` run `uv run mypy .`

See "tool.mypy" in `pyproject.toml` for configuration.

## Testing
Run `uv run pytest` from `/backend` to run all backend tests.

## Formatting
Run `uv run ruff format` from `/backend` to prettify all python files.

## Linting
Run `uv run ruff check`.

## Cron
Cron can be triggered manually **on local deplyoments only** by calling the `/cron` GET endpoin

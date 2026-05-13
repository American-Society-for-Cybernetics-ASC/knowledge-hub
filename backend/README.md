This is the uv workspace root.
- It makes our packages share a lock file, so we're all using the same versions of libraries
- It helps with inter-package dependencies (see the `[tool.uv.sources]` table) 
- It holds dev dependencies

# Running (Without Docker)
Run `uv run fastapi dev` from `/backend/server`
Run `uv run fastapi dev` from `/backend/auth_server`
- Replaec `dev` with `run` for a production build

Alternatively form `backend`:
- `uv run --package auth_server fastapi dev auth_server/main.py`
- `uv run --package server fastapi dev server/main.py`

# Type Checking
From `/backend`:
```bash
uv run mypy ./server
uv run mypy ./auth_server
uv run mypy ./database
```

or just run `uv run mypy .` from any package's directory.

# Testing
Run `uv run pytest` from `/backend` to run all backend tests.

Run `uv run pytest` from `/backend/<package>` to run all of that package's tests.
- This is equivalent to `uv run pytest <package>` from `/backend`

Pytest will find all files that match `test_*.py` or `*_test.py`, and then run all methods in those files that begin with the `test` prefix. Each package has a testing module to keep these tests in.
- For python/pytest namespace reasons, the testing modules have to have unique names (hence why I didn't name them all 'test')

# Formatting
Run `uv run ruff format` from `/backend` to prettify all python files.

Run `uv run ruff format` from `/backend/<package>` to format all of that package's python files.
- This is equivalent to `uv run ruff format <package>` from `/backend`

# Linting
Run `uv run ruff check`, which is called equivalently to formatting.

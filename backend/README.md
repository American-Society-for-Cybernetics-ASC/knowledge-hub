This is the uv workspace root.
- It makes our packages share a lock file, so we're all using the same versions of libraries
- It helps with inter-package dependencies (see the `[tool.uv.sources]` table) 
- It holds dev dependencies

# Running
From `/backend`:
- Run `uv run --package server server` to run the server.
- Run `uv run --package auth-server auth-server` to run the auth server.

Alternatively from a specific package
- Run `uv run server` from `/backend/server`
- Run `uv run auth-server`  from `/backend/auth_server`

# Type Checking
Run `uv run mypy -p database -p auth_server -p server` from `/backend`.

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

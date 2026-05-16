# syntax=docker/dockerfile:1
# This comes with UV:
FROM ghcr.io/astral-sh/uv:python3.14-alpine
WORKDIR /code

# Cache dependency installation
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

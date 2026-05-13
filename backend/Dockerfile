# syntax=docker/dockerfile:1
# This comes with UV:
FROM ghcr.io/astral-sh/uv:python3.14-alpine
WORKDIR /code
# Copy separately, so that we only reinstall dependencies if one of these two files change
COPY pyproject.toml .
COPY uv.lock .
COPY database .
RUN uv sync
COPY . .

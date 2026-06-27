# syntax=docker/dockerfile:1

# Use uv's official image with Python 3.13 (matches .python-version)
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# uv configuration:
#  - compile bytecode for faster startup
#  - copy packages from cache instead of symlinking (needed in a container)
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first, in a separate layer from the application code,
# so the dependency layer is cached unless pyproject.toml / uv.lock change.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the application source.
COPY . /app

# Install the project itself (now that the source is present).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Put the project's virtualenv on PATH so `fastapi`/`uvicorn` resolve directly.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Run via FastAPI's production server.
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]

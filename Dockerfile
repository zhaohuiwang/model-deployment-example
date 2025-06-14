
# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation, ensure platform-independent
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
    # The cache persists across Docker builds, in the container’s filesystem.
    # The bind binds the source file from 'host' to 'target' in the container
    # we do not need persist these file inside docker (vs COPY)
    # sync the environment with the dependencies in uv.lock and pyproject.toml.

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app 
# from current dir (where Dockerfile is) to '/app' inside the container
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev
    # This sync installs the project as a package on top of dependencies (ENV)

# Prepends /app/.venv/bin (executables in the environment) to PATH variable
ENV PATH="/app/.venv/bin:$PATH"


# Reset the entrypoint (explicitly clears any inherited ENTRYPOINT)
ENTRYPOINT []

# Run the FastAPI application by default
# Uses `--host 0.0.0.0` to allow access from outside the container
CMD ["fastapi", "run", "--host", "0.0.0.0", "src/model_demo/fast_api.py"]
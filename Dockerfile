# Pull base image
FROM python:3.12
# Compile Python files to bytecode after installation
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_COMPILE_BYTECODE=1
# Set work directory
WORKDIR /btt_app/btt
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock /btt_app/
# Install virtual environment
RUN uv sync --locked
# Set uv cache directory for subsequent uses of uv by container user
ENV UV_CACHE_DIR=/tmp/uv_cache
# Copy project
COPY ./btt /btt_app/btt
RUN mkdir -p /btt_app/btt/webserver/static

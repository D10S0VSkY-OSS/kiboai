FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy source code
COPY src/ src/
COPY examples/ examples/
COPY use_case/ use_case/
COPY main.py main.py

# Install the project
RUN uv sync --frozen

# Ensure the virtual environment is on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default command (overridden by compose)
CMD ["uv", "run", "kibo", "--help"]

FROM python:3.11-slim

WORKDIR /wrk

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files (inkl. uv.lock!)
COPY pyproject.toml uv.lock .python-version .//

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application
COPY ./app ./app

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
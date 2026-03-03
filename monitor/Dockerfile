FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./
COPY app/ ./app/
RUN uv pip install --system .

FROM base AS development
RUN uv pip install --system ".[dev]"
CMD ["python", "-m", "app.main"]

FROM base AS production
CMD ["python", "-m", "app.main"]

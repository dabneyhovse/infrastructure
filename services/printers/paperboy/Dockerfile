FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcups2-dev libcups2 ca-certificates gcc \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# separate project and depdencies sync 
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .
RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "paperboy.main"]

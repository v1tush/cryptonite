FROM ghcr.io/astral-sh/uv:0.12.24 AS uv
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:${PATH}"
WORKDIR /app

COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-cache \
    && useradd --create-home --uid 10001 cryptonite

COPY --chown=cryptonite:cryptonite cryptonite/ /app/
RUN mkdir -p /app/media && chown cryptonite:cryptonite /app/media
USER cryptonite

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

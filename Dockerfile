FROM python:3.12.8-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVICE_PORT=8000

WORKDIR /app
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/
COPY --chown=appuser:appuser pyproject.toml uv.lock README.md .env.example ./
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser main.py ./main.py
USER appuser
RUN uv sync --frozen --no-dev

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os,socket; s=socket.create_connection(('127.0.0.1', int(os.environ.get('SERVICE_PORT','8000'))), 2); s.close()"

CMD ["uv", "run", "--no-dev", "python", "-m", "app.web_server"]

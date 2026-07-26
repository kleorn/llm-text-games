FROM python:3.12.8-slim

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md .env.example ./
COPY app ./app
COPY main.py ./main.py
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--no-dev", "python", "main.py"]

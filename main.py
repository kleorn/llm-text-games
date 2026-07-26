import sys

from pydantic import ValidationError

from app.cli import run
from app.config import load_settings
from app.logging_config import configure_logging


def main() -> int:
    logger = configure_logging()
    try:
        return run(load_settings())
    except ValidationError:
        logger.exception("Configuration validation failed")
        print("Ошибка конфигурации: задайте OPENAI_API_KEY, OPENAI_BASE_URL и OPENAI_MODEL.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

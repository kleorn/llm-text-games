import sys

from pydantic import ValidationError

from app.config import load_settings
from app.logging_config import configure_logging
from app.textual_app import PrisonEscapeApp


def main() -> int:
    logger = configure_logging()
    try:
        PrisonEscapeApp(load_settings()).run()
        return 0
    except ValidationError:
        logger.exception("Configuration validation failed")
        print("Ошибка конфигурации: задайте OPENAI_API_KEY, OPENAI_BASE_URL и OPENAI_MODEL.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(log_path: str | Path = "logs/game.log") -> logging.Logger:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("llm_text_games")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    target = str(path.resolve())
    existing = next((handler for handler in logger.handlers if isinstance(handler, RotatingFileHandler)), None)
    if existing is None or existing.baseFilename != target:
        if existing is not None:
            logger.removeHandler(existing)
            existing.close()
        handler = RotatingFileHandler(path, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    return logger

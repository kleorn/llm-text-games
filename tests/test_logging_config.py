import logging
from logging.handlers import RotatingFileHandler

from app.logging_config import configure_logging


def test_configure_logging_uses_rotating_file_handler(tmp_path):
    logger = configure_logging(tmp_path / "game.log")

    handlers = [handler for handler in logger.handlers if isinstance(handler, RotatingFileHandler)]
    assert len(handlers) == 1
    assert handlers[0].maxBytes == 1024 * 1024
    assert handlers[0].backupCount > 0
    logger.info("rotation test")
    handler = handlers[0]
    handler.flush()
    assert (tmp_path / "game.log").read_text(encoding="utf-8")

"""Application logging for HI ROLEX."""

from __future__ import annotations

import logging
from logging import Logger

from utils.app_paths import LOG_DIR
from utils.validators import is_sensitive_text


LOG_FILE = LOG_DIR / "hi_rolex.log"


class SensitiveDataFilter(logging.Filter):
    """Prevents obvious secrets from being written to logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if is_sensitive_text(message):
            record.msg = "[REDACTED SENSITIVE LOG MESSAGE]"
            record.args = ()
        return True


def setup_logger() -> Logger:
    """Configure and return the app logger."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("hi_rolex")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(file_handler)
    return logger


def get_logger() -> Logger:
    """Return the configured HI ROLEX logger."""
    return setup_logger()


class AppLogger:
    """Compatibility wrapper for older imports."""

    @staticmethod
    def get_logger() -> Logger:
        """Return the configured HI ROLEX logger."""
        return get_logger()

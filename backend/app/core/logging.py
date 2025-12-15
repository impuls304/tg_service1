import logging
from logging.config import dictConfig
from typing import Literal

from .config import get_settings


def configure_logging(level: Literal[
    "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"
] = "INFO") -> None:
    """Configure structured logging for the service."""

    settings = get_settings()
    service_level = level or settings.log_level

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": service_level,
            },
        }
    )

    logging.getLogger(__name__).info(
        "Logging configured", extra={"level": service_level, "app": settings.app_name}
    )

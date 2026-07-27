import logging
import sys
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings


def setup_logging() -> None:
    logger = logging.getLogger()
    logger.handlers.clear()
    filename = "logs/app_production.log" if settings.env.environment == "prod" else "logs/app_development.log"
    handler = RotatingFileHandler(
        filename=filename,
        encoding="utf-8",
        maxBytes=1024 * 1024 // 2,
        backupCount=2,
    )
    handler.setFormatter(JsonFormatter("%(asctime)s - %(name)s - %(levelname)s -%(service)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    if settings.env.environment != "prod":
        handler_terminal = StreamHandler(stream=sys.stdout)
        handler_terminal.setFormatter(
            JsonFormatter("%(asctime)s - %(name)s - %(levelname)s -%(service)s - %(message)s")
        )
        logger.addHandler(handler_terminal)

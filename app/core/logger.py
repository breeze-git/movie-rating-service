import json
import logging
from datetime import datetime
from logging.config import dictConfig

# JSONFormatter


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        _DEFAULT_ATTRS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())

        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in _DEFAULT_ATTRS:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)


# LOGGING_CONFIG

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "class": "app.core.logger.JSONFormatter",
        },
        "uvicorn_formatter": {
            "class": "uvicorn.logging.DefaultFormatter",
            "format": "%(levelprefix)s %(message)s",
            "use_colors": True,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "uvicorn_formatter",
        },
        "json_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json",
        },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# SETUP


def setup_logger() -> None:
    dictConfig(LOGGING_CONFIG)

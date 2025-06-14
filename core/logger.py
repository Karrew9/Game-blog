import logging
from logging.config import dictConfig
from core.config import settings


logging_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "blog.log",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

dictConfig(logging_config)
logger = logging.getLogger(settings.APP_TITLE)
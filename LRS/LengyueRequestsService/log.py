"""Logger"""

import logging
import sys
from logging.config import dictConfig

LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,

    loggers={
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        },
        "LRS.error": {
            "level": "INFO",
            "handlers": ["error_console"],
        },
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "error",
            "stream": sys.stderr
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        },
        "error": {
            "format": "%(asctime)s (%(filename)s) [%(levelname)s] [%(funcName)s] [%(lineno)s]: %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        },
    }
)

dictConfig(LOGGING_CONFIG_DEFAULTS)
logger = logging.getLogger('root')
error_logger = logging.getLogger('LRS.error')
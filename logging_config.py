"""
Logging configuration for Pixel Art Converter
JSON logging format compatible with Loki
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger


LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for Loki-compatible logs"""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno
        log_record["service"] = "pixel-art-converter"

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging(app=None, log_level=None):
    """Configure application logging with JSON format for Loki"""
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    level = getattr(logging, log_level, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    json_formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s"
    )

    # Console handler with JSON format (for Docker/Loki)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)

    # File handler with JSON format
    file_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "app.json.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)

    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "error.json.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_handler)

    if app:
        app.logger.handlers = root_logger.handlers
        app.logger.setLevel(level)

    logging.info("Logging configured", extra={"action": "logging_init"})
    return root_logger


def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)


# Auto-initialize logging when module is imported
if os.environ.get("AUTO_INIT_LOGGING", "true").lower() == "true":
    setup_logging()

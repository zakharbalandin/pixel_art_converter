"""
Logging configuration for Pixel Art Converter
Provides structured logging for the application
"""

import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "ip_address"):
            log_entry["ip_address"] = record.ip_address
        if hasattr(record, "action"):
            log_entry["action"] = record.action
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        return json.dumps(log_entry)


def setup_logging(app=None, log_level=None):
    """Configure application logging"""
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    level = getattr(logging, log_level, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # File handler (JSON format)
    file_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "app.log"), maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)

    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "error.log"), maxBytes=10 * 1024 * 1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)

    # Auth log handler
    auth_logger = logging.getLogger("auth")
    auth_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "auth.log"), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    auth_handler.setLevel(logging.INFO)
    auth_handler.setFormatter(JSONFormatter())
    auth_logger.addHandler(auth_handler)

    if app:
        app.logger.handlers = root_logger.handlers
        app.logger.setLevel(level)

    logging.info("Logging configured", extra={"action": "logging_init"})
    return root_logger


def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)


auth_logger = get_logger("auth")
conversion_logger = get_logger("conversion")
api_logger = get_logger("api")


class LogContext:
    """Context manager for adding context to log messages"""

    def __init__(self, logger, **context):
        self.logger = logger
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def info(self, message, **extra):
        self.logger.info(message, extra={**self.context, **extra})

    def warning(self, message, **extra):
        self.logger.warning(message, extra={**self.context, **extra})

    def error(self, message, **extra):
        self.logger.error(message, extra={**self.context, **extra})


def log_auth_event(
    event_type, username=None, user_id=None, ip_address=None, success=True, details=None
):
    """Log authentication-related events"""
    extra = {"action": f"auth_{event_type}", "success": success}

    if username:
        extra["username"] = username
    if user_id:
        extra["user_id"] = user_id
    if ip_address:
        extra["ip_address"] = ip_address

    level = logging.INFO if success else logging.WARNING
    message = f"Auth event: {event_type} - {'success' if success else 'failed'}"

    if username:
        message += f" for user '{username}'"

    auth_logger.log(level, message, extra=extra)


def log_conversion_event(
    original_file, pixel_size, palette, duration_ms, user_id=None, success=True, error=None
):
    """Log conversion events"""
    extra = {
        "action": "image_conversion",
        "original_file": original_file,
        "pixel_size": pixel_size,
        "palette": palette,
        "duration_ms": duration_ms,
        "success": success,
    }

    if user_id:
        extra["user_id"] = user_id
    if error:
        extra["error"] = error

    level = logging.INFO if success else logging.ERROR
    message = f"Conversion {'completed' if success else 'failed'}: {original_file}"

    conversion_logger.log(level, message, extra=extra)


def log_api_request(endpoint, method, status_code, duration_ms, ip_address=None, user_id=None):
    """Log API request"""
    extra = {
        "action": "api_request",
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }

    if ip_address:
        extra["ip_address"] = ip_address
    if user_id:
        extra["user_id"] = user_id

    level = logging.INFO if status_code < 400 else logging.WARNING
    message = f"API {method} {endpoint} - {status_code} ({duration_ms}ms)"

    api_logger.log(level, message, extra=extra)


if os.environ.get("AUTO_INIT_LOGGING", "true").lower() == "true":
    setup_logging()

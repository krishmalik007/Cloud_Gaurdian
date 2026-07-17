import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pythonjsonlogger import jsonlogger


def setup_logger(log_level: str = "INFO", log_file: str = "cloudguardian.log") -> logging.Logger:
    """
    Configure and return the application logger with both console and file handlers.
    Uses JSON structured logging for machine-parseable output.

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Filename for the rotating log file.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file_path = log_dir / log_file

    # Resolve log level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    app_logger = logging.getLogger("CloudGuardian")
    app_logger.setLevel(level)

    # Prevent duplicate handlers if this function is called multiple times
    if app_logger.handlers:
        return app_logger

    # JSON formatter for structured logging
    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    # Plain-text formatter for console readability
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Console Handler (human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)

    # Rotating File Handler (JSON structured)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(json_formatter)

    # Attach handlers to logger
    app_logger.addHandler(console_handler)
    app_logger.addHandler(file_handler)

    return app_logger


# Default logger instance — will be reconfigured on startup with settings
logger = setup_logger()
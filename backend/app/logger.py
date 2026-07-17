import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Path to the log file
LOG_FILE = LOG_DIR / "cloudguardian.log"

# Create logger
logger = logging.getLogger("CloudGuardian")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if this file is imported multiple times
if not logger.handlers:

    # Log message format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Rotating File Handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Attach handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
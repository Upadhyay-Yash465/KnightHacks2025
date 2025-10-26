"""
logger.py
Centralized logging utility for the AI Speech Coach project.
Provides consistent, color-coded logs for agents, services, and API.
"""

import logging
import sys
from datetime import datetime


class LogFormatter(logging.Formatter):
    """Custom colorized log formatter with timestamps."""

    COLORS = {
        "DEBUG": "\033[36m",   # Cyan
        "INFO": "\033[32m",    # Green
        "WARNING": "\033[33m", # Yellow
        "ERROR": "\033[31m",   # Red
        "CRITICAL": "\033[41m" # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        time_str = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{time_str}] {log_color}{record.levelname:<8}{self.RESET} | {record.name}: {record.getMessage()}"
        if record.exc_info:
            log_msg += f"\n{self.formatException(record.exc_info)}"
        return log_msg


def setup_logger(name="AI-Speech-Coach", level=logging.INFO):
    """
    Creates and returns a consistent, colored logger for the given module.
    Usage:
        from .logger import setup_logger
        logger = setup_logger(__name__)
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LogFormatter())

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()  # Prevent duplicate logs
    logger.addHandler(handler)
    logger.propagate = False

    return logger


# Create a default global logger
logger = setup_logger()

# Quick test when running standalone
if __name__ == "__main__":
    logger.info("Logger initialized successfully.")
    logger.warning("This is a warning.")
    logger.error("Example error log.")

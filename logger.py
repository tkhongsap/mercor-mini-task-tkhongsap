"""
Centralized logging configuration for Airtable Contractor Application System

Provides color-coded console output with timestamps and module names.
Supports DEBUG, INFO, WARNING, ERROR levels.

Usage:
    from logger import get_logger

    logger = get_logger(__name__)
    logger.info("Processing applicant...")
    logger.error("Failed to connect to Airtable")
"""

import logging
import sys
from typing import Optional

# Color codes for terminal output
class ColorCodes:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels and bold to module names
    """

    LEVEL_COLORS = {
        logging.DEBUG: ColorCodes.CYAN,
        logging.INFO: ColorCodes.GREEN,
        logging.WARNING: ColorCodes.YELLOW,
        logging.ERROR: ColorCodes.RED,
        logging.CRITICAL: ColorCodes.BG_RED + ColorCodes.WHITE,
    }

    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        level_color = self.LEVEL_COLORS.get(record.levelno, ColorCodes.RESET)
        record.levelname = f"{level_color}{record.levelname}{ColorCodes.RESET}"

        # Make module name bold
        record.name = f"{ColorCodes.BOLD}{record.name}{ColorCodes.RESET}"

        return super().format(record)


# Global logger registry
_loggers: dict = {}


def get_logger(
    name: str,
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Get or create a logger with consistent formatting.

    Args:
        name: Logger name (usually __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Starting compression...")
    """
    # Return existing logger if already configured
    if name in _loggers:
        return _loggers[name]

    # Create new logger
    logger = logging.getLogger(name)
    logger.setLevel(level or logging.INFO)
    logger.propagate = False  # Don't propagate to root logger

    # Console handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level or logging.INFO)

    # Format: [timestamp] [LEVEL] [module] message
    console_format = ColoredFormatter(
        fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Optional file handler (no colors)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_format = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    # Cache logger
    _loggers[name] = logger

    return logger


def set_global_level(level: int) -> None:
    """
    Set logging level for all existing loggers.

    Args:
        level: Logging level constant (logging.DEBUG, logging.INFO, etc.)

    Example:
        set_global_level(logging.DEBUG)  # Enable debug logging
    """
    for logger in _loggers.values():
        logger.setLevel(level)
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)


# Convenience function for simple logging without creating a logger
def log_info(message: str) -> None:
    """Quick info log without creating a logger"""
    get_logger('main').info(message)


def log_error(message: str) -> None:
    """Quick error log without creating a logger"""
    get_logger('main').error(message)


def log_warning(message: str) -> None:
    """Quick warning log without creating a logger"""
    get_logger('main').warning(message)


def log_debug(message: str) -> None:
    """Quick debug log without creating a logger"""
    get_logger('main').debug(message)

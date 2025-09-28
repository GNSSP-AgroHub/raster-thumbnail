#!/usr/bin/env python3
"""
Logging configuration utilities for the raster thumbnail generator.

This module provides optional logging setup utilities. The library uses standard
Python logging that can be configured by the caller as needed.
"""

import logging
from pathlib import Path
from typing import Union


def get_logger(name: str = "raster_thumbnail") -> logging.Logger:
    """
    Get a logger instance for the raster thumbnail package.

    This is the main function library users should call. It returns a logger
    that they can configure however they want.

    Args:
        name: Logger name (default: 'raster_thumbnail')

    Returns:
        logging.Logger: Logger instance that caller can configure
    """
    return logging.getLogger(name)


def setup_basic_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Setup basic console logging for quick start (optional convenience function).

    This is a convenience function for users who want minimal setup.
    Advanced users should configure logging themselves.

    Args:
        level: Logging level (default: INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = get_logger()

    # Only setup if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger


def setup_file_logging(
    log_file: Union[str, Path], level: int = logging.INFO, console: bool = True
) -> logging.Logger:
    """
    Setup file-based logging (optional convenience function).

    This is a convenience function for users who want simple file logging.
    Advanced users should configure logging themselves.

    Args:
        log_file: Path to log file
        level: Logging level (default: INFO)
        console: Also log to console (default: True)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = get_logger()

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.setLevel(level)
    return logger


def silence_third_party_loggers() -> None:
    """
    Silence noisy third-party loggers (optional utility function).

    Call this if you want to reduce noise from matplotlib, PIL, etc.
    """
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("rasterio").setLevel(logging.WARNING)

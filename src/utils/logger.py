"""An utility handling logging processes."""

from __future__ import annotations

import logging
from sys import stdout


class Logger:
    """A singleton logging class."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """This method turns the class into a singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: str = "LockAndKey"):
        """Initialize the instance."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(stdout)
        stream_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%H:%M:%S"
            )
        )
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)
        self.logger.info("Initialized instance")


_logger_instance: Logger | None = None


def get_logger() -> logging.Logger:
    """Get a `logging.Logger` instance from the project's `Logger` singleton."""
    global _logger_instance  # noqa: PLW0603
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance.logger


def debug(msg, *args, **kwargs):
    """Log macro with debug level."""
    get_logger().debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """Log macro with (default) info level."""
    get_logger().info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    """Log macro with a warning."""
    get_logger().warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    """Log macro with an error."""
    get_logger().error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    """Log macro with a deadly error."""
    get_logger().critical(msg, *args, **kwargs)

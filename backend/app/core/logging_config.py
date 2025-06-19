"""
Logging configuration for the Project Overview Agent.
"""

import logging
import logging.config
from pathlib import Path
from typing import Dict, Any
from logging.handlers import RotatingFileHandler

from app.core.config import get_settings

settings = get_settings()


class CustomRotatingFileHandler(RotatingFileHandler):
    """Custom rotating file handler with better error handling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def doRollover(self):
        """Override to handle rollover errors gracefully."""
        try:
            super().doRollover()
        except Exception as e:
            # Log to stderr if rollover fails
            import sys
            print(f"Log rollover failed: {e}", file=sys.stderr)


def setup_logging() -> None:
    """Set up logging configuration with rotation."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file_rotating": {
                "()": CustomRotatingFileHandler,
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": str(log_dir / "app.log"),
                "mode": "a",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "()": CustomRotatingFileHandler,
                "level": "ERROR",
                "formatter": "detailed",
                "filename": str(log_dir / "error.log"),
                "mode": "a",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 3,
                "encoding": "utf-8",
            },
            "access_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": str(log_dir / "access.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 7,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console", "file_rotating", "error_file"],
        },
        "loggers": {
            "app": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console", "file_rotating", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "access_file"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False,
            },
            "app.database": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console", "file_rotating"],
                "propagate": False,
            },
            "app.services": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console", "file_rotating"],
                "propagate": False,
            },
            "app.api": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console", "file_rotating"],
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    
    # Log startup message
    logger = logging.getLogger("app")
    logger.info("Logging system initialized")
    logger.info(f"Log directory: {log_dir.absolute()}")
    logger.info(f"Debug mode: {settings.DEBUG}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(f"app.{name}")


def log_exception(logger: logging.Logger, exc: Exception, context: str = "") -> None:
    """Log an exception with context."""
    if context:
        logger.exception(f"{context}: {exc}")
    else:
        logger.exception(f"Exception occurred: {exc}")


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs) -> None:
    """Log performance metrics."""
    extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"PERFORMANCE: {operation} took {duration:.3f}s {extra_info}".strip())

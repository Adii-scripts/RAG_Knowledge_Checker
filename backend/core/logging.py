"""
Logging configuration for the RAG Knowledge Base
"""

import sys
from loguru import logger
from core.config import settings

# Remove default logger
logger.remove()

# Add custom logger with formatting
logger.add(
    sys.stdout,
    format=settings.log_format,
    level=settings.log_level,
    colorize=True,
    backtrace=True,
    diagnose=True
)

# Add file logger for production
logger.add(
    "logs/app.log",
    format=settings.log_format,
    level=settings.log_level,
    rotation="10 MB",
    retention="30 days",
    compression="zip"
)

# Export logger
__all__ = ["logger"]
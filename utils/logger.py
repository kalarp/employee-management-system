"""
Logging configuration for Employee Management System
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(log_file: str = "employee_management.log",
                 log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up application logger

    Args:
        log_file: Path to log file
        log_level: Logging level

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('EmployeeManagement')
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler for errors only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Log startup
    logger.info("=" * 50)
    logger.info(f"Employee Management System started at {datetime.now()}")
    logger.info("=" * 50)

    return logger


def get_logger() -> logging.Logger:
    """Get the application logger"""
    return logging.getLogger('EmployeeManagement')
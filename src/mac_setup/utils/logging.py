"""Logging utilities for mac-setup."""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

from mac_setup.config import LOGS_DIR, ensure_directories

# Module-level logger
_logger: logging.Logger | None = None


def setup_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_to_file: bool = True,
) -> logging.Logger:
    """Set up logging configuration.

    Args:
        verbose: Enable debug-level logging
        quiet: Suppress most output (only errors)
        log_to_file: Whether to also log to file

    Returns:
        Configured logger instance
    """
    global _logger

    logger = logging.getLogger("mac-setup")
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    logger.handlers.clear()

    # Determine console log level
    if quiet:
        console_level = logging.ERROR
    elif verbose:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_format = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        ensure_directories()
        log_file = LOGS_DIR / f"mac-setup-{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Get the application logger.

    Returns:
        Logger instance (creates one if not exists)
    """
    global _logger

    if _logger is None:
        _logger = setup_logging()

    return _logger


def log_install(package_id: str, success: bool, message: str = "") -> None:
    """Log an installation event.

    Args:
        package_id: The package identifier
        success: Whether the installation succeeded
        message: Optional additional message
    """
    logger = get_logger()
    if success:
        logger.info(f"Installed: {package_id} {message}")
    else:
        logger.error(f"Failed to install: {package_id} - {message}")


def log_uninstall(package_id: str, success: bool, message: str = "") -> None:
    """Log an uninstall event.

    Args:
        package_id: The package identifier
        success: Whether the uninstall succeeded
        message: Optional additional message
    """
    logger = get_logger()
    if success:
        logger.info(f"Uninstalled: {package_id} {message}")
    else:
        logger.error(f"Failed to uninstall: {package_id} - {message}")


def cleanup_old_logs(keep_days: int = 30) -> int:
    """Remove log files older than specified days.

    Args:
        keep_days: Number of days to keep logs

    Returns:
        Number of files removed
    """
    if not LOGS_DIR.exists():
        return 0

    removed = 0
    now = datetime.now()

    for log_file in LOGS_DIR.glob("*.log*"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            age_days = (now - mtime).days

            if age_days > keep_days:
                log_file.unlink()
                removed += 1
        except OSError:
            continue

    return removed

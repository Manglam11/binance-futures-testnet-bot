"""Centralized logging setup — file (full detail) + console (summary)."""

import logging
from pathlib import Path


def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """Configure and return a logger with file + console handlers.

    File handler:    DEBUG+ → logs/trading_bot.log   (full audit trail)
    Console handler: INFO+  → stderr                 (clean terminal output)
    """
    logger = logging.getLogger(name)

    # Guard against duplicate handlers if setup_logger() is called twice
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Make sure logs/ exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Shared format — easy to grep, easy to read
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. File handler — captures everything (DEBUG and up)
    file_handler = logging.FileHandler(log_dir / "trading_bot.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Console handler — only INFO and up (no DEBUG spam)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
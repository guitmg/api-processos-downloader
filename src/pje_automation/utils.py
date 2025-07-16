"""
Utility functions for PJe Automation.
"""

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def setup_logging(
    log_level: str = "INFO", log_file: Optional[str] = None
) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger("pje_automation")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        ensure_directory_exists(os.path.dirname(log_file))
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def ensure_directory_exists(directory: str) -> None:
    """Ensure that a directory exists, create if it doesn't."""
    if directory:
        Path(directory).mkdir(parents=True, exist_ok=True)


def clean_filename(filename: str) -> str:
    """Clean filename by removing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def get_timestamp() -> str:
    """Get current timestamp as string."""
    return time.strftime("%Y%m%d_%H%M%S")


def parse_process_number(process_number: str) -> Dict[str, str]:
    """Parse process number into components."""
    # Remove any non-numeric characters except hyphens and dots
    clean_number = "".join(c for c in process_number if c.isdigit() or c in ".-")

    # Expected format: NNNNNNN-DD.YYYY.J.TR.OOOO
    parts = clean_number.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid process number format: {process_number}")

    sequential = parts[0]
    remaining = parts[1]

    # Split the remaining part by dots
    remaining_parts = remaining.split(".")
    if len(remaining_parts) != 5:
        raise ValueError(f"Invalid process number format: {process_number}")

    return {
        "sequential": sequential,
        "digit": remaining_parts[0],
        "year": remaining_parts[1],
        "court": remaining_parts[4],
    }


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def get_latest_file(directory: str, pattern: str = "*") -> Optional[str]:
    """Get the most recently created file in a directory."""
    directory_path = Path(directory)
    if not directory_path.exists():
        return None

    files = list(directory_path.glob(pattern))
    if not files:
        return None

    return str(max(files, key=lambda f: f.stat().st_ctime))


def cleanup_old_files(directory: str, pattern: str = "*", max_age_days: int = 7) -> int:
    """Clean up old files in a directory."""
    directory_path = Path(directory)
    if not directory_path.exists():
        return 0

    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    files_deleted = 0

    for file_path in directory_path.glob(pattern):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                files_deleted += 1
            except OSError:
                pass  # Ignore errors when deleting files

    return files_deleted

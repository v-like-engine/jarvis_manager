"""Path resolution and validation."""

import os
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class PathResolver:
    """
    Resolve and validate file paths.

    Features:
    - Expand environment variables
    - Resolve relative paths
    - Validate paths
    - Check if path is in protected directory
    """

    # Protected system paths
    PROTECTED_PATHS = [
        'C:\\Windows',
        'C:\\Windows\\System32',
        'C:\\Program Files',
        'C:\\Program Files (x86)',
        'C:\\ProgramData',
    ]

    @staticmethod
    def resolve(path: str, base_dir: Optional[str] = None) -> Path:
        """
        Resolve a path, expanding variables and making it absolute.

        Args:
            path: Path to resolve
            base_dir: Base directory for relative paths

        Returns:
            Resolved Path object
        """
        # Expand environment variables
        expanded = os.path.expandvars(path)

        # Expand user home directory
        expanded = os.path.expanduser(expanded)

        # Convert to Path
        path_obj = Path(expanded)

        # Make absolute
        if not path_obj.is_absolute():
            if base_dir:
                path_obj = Path(base_dir) / path_obj
            else:
                path_obj = path_obj.resolve()

        return path_obj

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Check if path is valid.

        Args:
            path: Path to check

        Returns:
            True if valid
        """
        try:
            Path(path)
            return True
        except (ValueError, OSError):
            return False

    @staticmethod
    def is_protected(path: str) -> bool:
        """
        Check if path is in a protected directory.

        Args:
            path: Path to check

        Returns:
            True if path is protected
        """
        try:
            path_obj = PathResolver.resolve(path)
            path_str = str(path_obj).lower()

            for protected in PathResolver.PROTECTED_PATHS:
                if path_str.startswith(protected.lower()):
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking if path is protected: {e}")
            # If we can't determine, assume protected for safety
            return True

    @staticmethod
    def exists(path: str) -> bool:
        """
        Check if path exists.

        Args:
            path: Path to check

        Returns:
            True if exists
        """
        try:
            return PathResolver.resolve(path).exists()
        except Exception:
            return False

    @staticmethod
    def is_file(path: str) -> bool:
        """
        Check if path is a file.

        Args:
            path: Path to check

        Returns:
            True if file
        """
        try:
            return PathResolver.resolve(path).is_file()
        except Exception:
            return False

    @staticmethod
    def is_directory(path: str) -> bool:
        """
        Check if path is a directory.

        Args:
            path: Path to check

        Returns:
            True if directory
        """
        try:
            return PathResolver.resolve(path).is_dir()
        except Exception:
            return False

    @staticmethod
    def get_size(path: str) -> Optional[int]:
        """
        Get file/directory size in bytes.

        Args:
            path: Path to check

        Returns:
            Size in bytes or None
        """
        try:
            path_obj = PathResolver.resolve(path)

            if path_obj.is_file():
                return path_obj.stat().st_size
            elif path_obj.is_dir():
                # Calculate directory size
                total = 0
                for item in path_obj.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
                return total
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting size of {path}: {e}")
            return None

    @staticmethod
    def normalize(path: str) -> str:
        """
        Normalize a path (remove .. and . components).

        Args:
            path: Path to normalize

        Returns:
            Normalized path string
        """
        try:
            return str(PathResolver.resolve(path))
        except Exception:
            return path

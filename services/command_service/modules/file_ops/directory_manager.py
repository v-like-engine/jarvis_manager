"""Directory operations manager."""

import shutil
import logging
from pathlib import Path
from typing import Dict, Any

from .path_resolver import PathResolver

logger = logging.getLogger(__name__)


class DirectoryManager:
    """
    Manage directory operations.

    Features:
    - Create directories
    - Delete directories
    - Navigate directories
    - Safety checks
    """

    def __init__(self, enable_safety_checks: bool = True):
        """
        Initialize directory manager.

        Args:
            enable_safety_checks: Enable safety checks
        """
        self.enable_safety_checks = enable_safety_checks
        self.current_dir = Path.cwd()
        logger.info("Directory manager initialized")

    def create_directory(
        self,
        dir_path: str,
        parents: bool = True
    ) -> Dict[str, Any]:
        """
        Create a directory.

        Args:
            dir_path: Path to directory
            parents: Create parent directories if needed

        Returns:
            Result dictionary
        """
        try:
            path = PathResolver.resolve(dir_path)

            # Check if in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(path)):
                return {
                    'success': False,
                    'error': 'Cannot create directory in protected location'
                }

            # Check if exists
            if path.exists():
                return {
                    'success': False,
                    'error': 'Directory already exists'
                }

            # Create directory
            path.mkdir(parents=parents, exist_ok=False)

            logger.info(f"Created directory: {path}")
            return {
                'success': True,
                'path': str(path),
                'message': f'Directory created: {path.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied: {dir_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to create directory: {str(e)}'
            }

    def delete_directory(
        self,
        dir_path: str,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a directory.

        Args:
            dir_path: Path to directory
            recursive: Delete recursively (with contents)

        Returns:
            Result dictionary
        """
        try:
            path = PathResolver.resolve(dir_path)

            # Check if exists
            if not path.exists():
                return {
                    'success': False,
                    'error': 'Directory not found'
                }

            # Check if it's a directory
            if not path.is_dir():
                return {
                    'success': False,
                    'error': 'Path is not a directory'
                }

            # Check if in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(path)):
                return {
                    'success': False,
                    'error': 'Cannot delete protected directory'
                }

            # Check if directory is empty
            if not recursive and any(path.iterdir()):
                return {
                    'success': False,
                    'error': 'Directory is not empty (use recursive=True to delete)'
                }

            # Delete directory
            if recursive:
                shutil.rmtree(path)
            else:
                path.rmdir()

            logger.info(f"Deleted directory: {path}")
            return {
                'success': True,
                'path': str(path),
                'message': f'Directory deleted: {path.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied: {dir_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to delete directory {dir_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to delete directory: {str(e)}'
            }

    def navigate(self, dir_path: str) -> Dict[str, Any]:
        """
        Navigate to a directory (change current directory).

        Args:
            dir_path: Path to directory

        Returns:
            Result dictionary
        """
        try:
            path = PathResolver.resolve(dir_path)

            # Check if exists
            if not path.exists():
                return {
                    'success': False,
                    'error': 'Directory not found'
                }

            # Check if it's a directory
            if not path.is_dir():
                return {
                    'success': False,
                    'error': 'Path is not a directory'
                }

            # Navigate
            self.current_dir = path

            logger.info(f"Navigated to: {path}")
            return {
                'success': True,
                'path': str(path),
                'message': f'Current directory: {path}'
            }

        except Exception as e:
            logger.error(f"Failed to navigate to {dir_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to navigate: {str(e)}'
            }

    def get_current_directory(self) -> Dict[str, Any]:
        """
        Get current directory.

        Returns:
            Result dictionary
        """
        return {
            'success': True,
            'path': str(self.current_dir)
        }

    def copy_directory(
        self,
        source_path: str,
        dest_path: str
    ) -> Dict[str, Any]:
        """
        Copy a directory.

        Args:
            source_path: Source directory path
            dest_path: Destination path

        Returns:
            Result dictionary
        """
        try:
            src = PathResolver.resolve(source_path)
            dst = PathResolver.resolve(dest_path)

            # Check source exists
            if not src.exists():
                return {
                    'success': False,
                    'error': 'Source directory not found'
                }

            # Check source is a directory
            if not src.is_dir():
                return {
                    'success': False,
                    'error': 'Source is not a directory'
                }

            # Check destination
            if dst.exists():
                return {
                    'success': False,
                    'error': 'Destination already exists'
                }

            # Check if destination is in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(dst)):
                return {
                    'success': False,
                    'error': 'Cannot copy to protected directory'
                }

            # Copy directory
            shutil.copytree(src, dst)

            logger.info(f"Copied directory {src} to {dst}")
            return {
                'success': True,
                'source': str(src),
                'destination': str(dst),
                'message': f'Directory copied to {dst.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied copying {source_path} to {dest_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to copy directory: {e}")
            return {
                'success': False,
                'error': f'Failed to copy directory: {str(e)}'
            }

    def move_directory(
        self,
        source_path: str,
        dest_path: str
    ) -> Dict[str, Any]:
        """
        Move a directory.

        Args:
            source_path: Source directory path
            dest_path: Destination path

        Returns:
            Result dictionary
        """
        try:
            src = PathResolver.resolve(source_path)
            dst = PathResolver.resolve(dest_path)

            # Check source exists
            if not src.exists():
                return {
                    'success': False,
                    'error': 'Source directory not found'
                }

            # Check source is a directory
            if not src.is_dir():
                return {
                    'success': False,
                    'error': 'Source is not a directory'
                }

            # Check if source is in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(src)):
                return {
                    'success': False,
                    'error': 'Cannot move directory from protected location'
                }

            # Check destination
            if dst.exists():
                return {
                    'success': False,
                    'error': 'Destination already exists'
                }

            # Check if destination is in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(dst)):
                return {
                    'success': False,
                    'error': 'Cannot move to protected directory'
                }

            # Move directory
            shutil.move(src, dst)

            logger.info(f"Moved directory {src} to {dst}")
            return {
                'success': True,
                'source': str(src),
                'destination': str(dst),
                'message': f'Directory moved to {dst.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied moving {source_path} to {dest_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to move directory: {e}")
            return {
                'success': False,
                'error': f'Failed to move directory: {str(e)}'
            }

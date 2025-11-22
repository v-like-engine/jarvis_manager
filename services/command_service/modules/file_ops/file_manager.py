"""File operations manager."""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .path_resolver import PathResolver

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manage file operations.

    Features:
    - Create files
    - Delete files
    - Copy files
    - Move files
    - Safety checks
    """

    def __init__(self, enable_safety_checks: bool = True):
        """
        Initialize file manager.

        Args:
            enable_safety_checks: Enable safety checks
        """
        self.enable_safety_checks = enable_safety_checks
        logger.info("File manager initialized")

    def create_file(
        self,
        file_path: str,
        content: str = '',
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new file.

        Args:
            file_path: Path to file
            content: File content
            overwrite: Overwrite if exists

        Returns:
            Result dictionary
        """
        try:
            path = PathResolver.resolve(file_path)

            # Check if in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(path)):
                return {
                    'success': False,
                    'error': 'Cannot create file in protected directory'
                }

            # Check if file exists
            if path.exists() and not overwrite:
                return {
                    'success': False,
                    'error': 'File already exists'
                }

            # Create parent directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Created file: {path}")
            return {
                'success': True,
                'path': str(path),
                'message': f'File created: {path.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to create file: {str(e)}'
            }

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file.

        Args:
            file_path: Path to file

        Returns:
            Result dictionary
        """
        try:
            path = PathResolver.resolve(file_path)

            # Check if exists
            if not path.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }

            # Check if it's a file
            if not path.is_file():
                return {
                    'success': False,
                    'error': 'Path is not a file'
                }

            # Check if in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(path)):
                return {
                    'success': False,
                    'error': 'Cannot delete file in protected directory'
                }

            # Delete file
            path.unlink()

            logger.info(f"Deleted file: {path}")
            return {
                'success': True,
                'path': str(path),
                'message': f'File deleted: {path.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to delete file: {str(e)}'
            }

    def copy_file(
        self,
        source_path: str,
        dest_path: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Copy a file.

        Args:
            source_path: Source file path
            dest_path: Destination path
            overwrite: Overwrite if exists

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
                    'error': 'Source file not found'
                }

            # Check source is a file
            if not src.is_file():
                return {
                    'success': False,
                    'error': 'Source is not a file'
                }

            # Check destination
            if dst.exists() and not overwrite:
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

            # Create destination directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(src, dst)

            logger.info(f"Copied {src} to {dst}")
            return {
                'success': True,
                'source': str(src),
                'destination': str(dst),
                'message': f'File copied to {dst.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied copying {source_path} to {dest_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to copy file: {e}")
            return {
                'success': False,
                'error': f'Failed to copy file: {str(e)}'
            }

    def move_file(
        self,
        source_path: str,
        dest_path: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Move a file.

        Args:
            source_path: Source file path
            dest_path: Destination path
            overwrite: Overwrite if exists

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
                    'error': 'Source file not found'
                }

            # Check source is a file
            if not src.is_file():
                return {
                    'success': False,
                    'error': 'Source is not a file'
                }

            # Check if source is in protected directory
            if self.enable_safety_checks and PathResolver.is_protected(str(src)):
                return {
                    'success': False,
                    'error': 'Cannot move file from protected directory'
                }

            # Check destination
            if dst.exists() and not overwrite:
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

            # Create destination directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(src, dst)

            logger.info(f"Moved {src} to {dst}")
            return {
                'success': True,
                'source': str(src),
                'destination': str(dst),
                'message': f'File moved to {dst.name}'
            }

        except PermissionError:
            logger.error(f"Permission denied moving {source_path} to {dest_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
            return {
                'success': False,
                'error': f'Failed to move file: {str(e)}'
            }

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read file contents.

        Args:
            file_path: Path to file

        Returns:
            Result dictionary with file content
        """
        try:
            path = PathResolver.resolve(file_path)

            if not path.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }

            if not path.is_file():
                return {
                    'success': False,
                    'error': 'Path is not a file'
                }

            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'success': True,
                'path': str(path),
                'content': content,
                'size': len(content)
            }

        except PermissionError:
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except UnicodeDecodeError:
            return {
                'success': False,
                'error': 'File is not a text file (binary content)'
            }
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to read file: {str(e)}'
            }

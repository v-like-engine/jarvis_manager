"""File browser for listing directory contents."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .path_resolver import PathResolver

logger = logging.getLogger(__name__)


class FileBrowser:
    """
    Browse and list directory contents.

    Features:
    - List files and directories
    - Filter by type
    - Sort by various criteria
    - Get file details
    """

    @staticmethod
    def list_directory(
        dir_path: str,
        show_hidden: bool = False,
        files_only: bool = False,
        dirs_only: bool = False,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List directory contents.

        Args:
            dir_path: Path to directory
            show_hidden: Show hidden files
            files_only: Show only files
            dirs_only: Show only directories
            pattern: Filter by pattern (e.g., "*.txt")

        Returns:
            Result dictionary with file/directory list
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

            # List items
            items = []

            if pattern:
                # Use glob pattern
                iterator = path.glob(pattern)
            else:
                # List all items
                iterator = path.iterdir()

            for item in iterator:
                # Skip hidden files if requested
                if not show_hidden and item.name.startswith('.'):
                    continue

                # Filter by type
                if files_only and not item.is_file():
                    continue
                if dirs_only and not item.is_dir():
                    continue

                # Get item info
                item_info = FileBrowser._get_item_info(item)
                items.append(item_info)

            # Sort by name
            items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))

            return {
                'success': True,
                'path': str(path),
                'count': len(items),
                'items': items
            }

        except PermissionError:
            logger.error(f"Permission denied: {dir_path}")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to list directory {dir_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to list directory: {str(e)}'
            }

    @staticmethod
    def _get_item_info(path: Path) -> Dict[str, Any]:
        """
        Get detailed information about a file/directory.

        Args:
            path: Path object

        Returns:
            Item information dictionary
        """
        try:
            stat = path.stat()

            info = {
                'name': path.name,
                'path': str(path),
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'size': stat.st_size if path.is_file() else None,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            }

            # Add extension for files
            if path.is_file():
                info['extension'] = path.suffix.lower()

            return info

        except Exception as e:
            logger.error(f"Failed to get info for {path}: {e}")
            return {
                'name': path.name,
                'path': str(path),
                'error': str(e)
            }

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file.

        Args:
            file_path: Path to file

        Returns:
            File information dictionary
        """
        try:
            path = PathResolver.resolve(file_path)

            if not path.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }

            info = FileBrowser._get_item_info(path)
            info['success'] = True

            return info

        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {
                'success': False,
                'error': f'Failed to get file info: {str(e)}'
            }

    @staticmethod
    def search_files(
        dir_path: str,
        pattern: str,
        recursive: bool = True,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search for files matching a pattern.

        Args:
            dir_path: Directory to search in
            pattern: Search pattern (glob)
            recursive: Search recursively
            max_results: Maximum number of results

        Returns:
            Result dictionary with matching files
        """
        try:
            path = PathResolver.resolve(dir_path)

            if not path.exists():
                return {
                    'success': False,
                    'error': 'Directory not found'
                }

            if not path.is_dir():
                return {
                    'success': False,
                    'error': 'Path is not a directory'
                }

            # Search
            results = []

            if recursive:
                iterator = path.rglob(pattern)
            else:
                iterator = path.glob(pattern)

            for item in iterator:
                if len(results) >= max_results:
                    break

                results.append(FileBrowser._get_item_info(item))

            return {
                'success': True,
                'path': str(path),
                'pattern': pattern,
                'count': len(results),
                'truncated': len(results) >= max_results,
                'results': results
            }

        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return {
                'success': False,
                'error': f'Failed to search files: {str(e)}'
            }

    @staticmethod
    def get_tree(
        dir_path: str,
        max_depth: int = 3,
        show_hidden: bool = False
    ) -> Dict[str, Any]:
        """
        Get directory tree structure.

        Args:
            dir_path: Directory path
            max_depth: Maximum depth to traverse
            show_hidden: Show hidden files

        Returns:
            Result dictionary with tree structure
        """
        try:
            path = PathResolver.resolve(dir_path)

            if not path.exists():
                return {
                    'success': False,
                    'error': 'Directory not found'
                }

            if not path.is_dir():
                return {
                    'success': False,
                    'error': 'Path is not a directory'
                }

            tree = FileBrowser._build_tree(path, max_depth, show_hidden, 0)

            return {
                'success': True,
                'path': str(path),
                'tree': tree
            }

        except Exception as e:
            logger.error(f"Failed to get directory tree: {e}")
            return {
                'success': False,
                'error': f'Failed to get directory tree: {str(e)}'
            }

    @staticmethod
    def _build_tree(
        path: Path,
        max_depth: int,
        show_hidden: bool,
        current_depth: int
    ) -> Dict[str, Any]:
        """
        Recursively build directory tree.

        Args:
            path: Current path
            max_depth: Maximum depth
            show_hidden: Show hidden files
            current_depth: Current depth

        Returns:
            Tree node dictionary
        """
        node = {
            'name': path.name,
            'path': str(path),
            'is_directory': path.is_dir(),
        }

        if path.is_dir() and current_depth < max_depth:
            children = []
            try:
                for item in path.iterdir():
                    # Skip hidden files if requested
                    if not show_hidden and item.name.startswith('.'):
                        continue

                    child = FileBrowser._build_tree(
                        item,
                        max_depth,
                        show_hidden,
                        current_depth + 1
                    )
                    children.append(child)

                node['children'] = children
            except PermissionError:
                node['error'] = 'Permission denied'

        return node

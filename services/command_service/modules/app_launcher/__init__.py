"""App launcher module for discovering and launching Windows applications."""

from .app_finder import AppFinder
from .app_database import AppDatabase
from .app_launcher import AppLauncher
from .app_closer import AppCloser

__all__ = [
    'AppFinder',
    'AppDatabase',
    'AppLauncher',
    'AppCloser',
]

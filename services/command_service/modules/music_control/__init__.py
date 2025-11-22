"""Music control module."""

from .music_controller import MusicController
from .app_interfaces import YandexMusicInterface, SpotifyInterface, GenericMusicInterface

__all__ = [
    'MusicController',
    'YandexMusicInterface',
    'SpotifyInterface',
    'GenericMusicInterface',
]

"""Interfaces for specific music applications."""

import logging
import sys
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    try:
        import win32api
        import win32con
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False


class GenericMusicInterface:
    """
    Generic music player interface using media keys.

    Works with most music players that respond to media keys.
    """

    @staticmethod
    def play_pause() -> Dict[str, Any]:
        """Send play/pause media key."""
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows API not available'
            }

        try:
            # Send VK_MEDIA_PLAY_PAUSE key
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)

            return {
                'success': True,
                'action': 'play_pause',
                'message': 'Sent play/pause command'
            }

        except Exception as e:
            logger.error(f"Failed to send play/pause: {e}")
            return {
                'success': False,
                'error': f'Failed to send play/pause: {str(e)}'
            }

    @staticmethod
    def next_track() -> Dict[str, Any]:
        """Send next track media key."""
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows API not available'
            }

        try:
            win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)

            return {
                'success': True,
                'action': 'next',
                'message': 'Sent next track command'
            }

        except Exception as e:
            logger.error(f"Failed to send next track: {e}")
            return {
                'success': False,
                'error': f'Failed to send next track: {str(e)}'
            }

    @staticmethod
    def previous_track() -> Dict[str, Any]:
        """Send previous track media key."""
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows API not available'
            }

        try:
            win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)

            return {
                'success': True,
                'action': 'previous',
                'message': 'Sent previous track command'
            }

        except Exception as e:
            logger.error(f"Failed to send previous track: {e}")
            return {
                'success': False,
                'error': f'Failed to send previous track: {str(e)}'
            }

    @staticmethod
    def stop() -> Dict[str, Any]:
        """Send stop media key."""
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows API not available'
            }

        try:
            win32api.keybd_event(win32con.VK_MEDIA_STOP, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MEDIA_STOP, 0, win32con.KEYEVENTF_KEYUP, 0)

            return {
                'success': True,
                'action': 'stop',
                'message': 'Sent stop command'
            }

        except Exception as e:
            logger.error(f"Failed to send stop: {e}")
            return {
                'success': False,
                'error': f'Failed to send stop: {str(e)}'
            }


class YandexMusicInterface(GenericMusicInterface):
    """
    Interface for Yandex Music.

    Currently uses generic media keys.
    Could be extended with Yandex Music API if available.
    """

    @staticmethod
    def play() -> Dict[str, Any]:
        """Start playback."""
        return YandexMusicInterface.play_pause()

    @staticmethod
    def pause() -> Dict[str, Any]:
        """Pause playback."""
        return YandexMusicInterface.play_pause()


class SpotifyInterface(GenericMusicInterface):
    """
    Interface for Spotify.

    Currently uses generic media keys.
    Could be extended with Spotify Web API if needed.
    """

    @staticmethod
    def play() -> Dict[str, Any]:
        """Start playback."""
        return SpotifyInterface.play_pause()

    @staticmethod
    def pause() -> Dict[str, Any]:
        """Pause playback."""
        return SpotifyInterface.play_pause()

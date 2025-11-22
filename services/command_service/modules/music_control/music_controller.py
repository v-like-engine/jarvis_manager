"""Music playback controller."""

import logging
import sys
from typing import Dict, Any, Optional

from .app_interfaces import GenericMusicInterface, YandexMusicInterface, SpotifyInterface

if sys.platform == 'win32':
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
        PYCAW_AVAILABLE = True
    except ImportError:
        PYCAW_AVAILABLE = False
        logging.warning("pycaw not available, volume control disabled")
else:
    PYCAW_AVAILABLE = False

logger = logging.getLogger(__name__)


class MusicController:
    """
    Control music playback and volume.

    Features:
    - Play/pause/next/previous/stop
    - Volume control
    - Support for multiple music players
    """

    MUSIC_INTERFACES = {
        'yandex_music': YandexMusicInterface,
        'spotify': SpotifyInterface,
        'generic': GenericMusicInterface,
    }

    def __init__(self, preferred_player: str = 'generic'):
        """
        Initialize music controller.

        Args:
            preferred_player: Preferred music player
        """
        self.preferred_player = preferred_player
        self.interface = self._get_interface(preferred_player)
        logger.info(f"Music controller initialized (player: {preferred_player})")

    def _get_interface(self, player: str):
        """
        Get music player interface.

        Args:
            player: Player name

        Returns:
            Interface class
        """
        return self.MUSIC_INTERFACES.get(player, GenericMusicInterface)

    def play_pause(self) -> Dict[str, Any]:
        """
        Toggle play/pause.

        Returns:
            Result dictionary
        """
        return self.interface.play_pause()

    def play(self) -> Dict[str, Any]:
        """
        Start playback.

        Returns:
            Result dictionary
        """
        if hasattr(self.interface, 'play'):
            return self.interface.play()
        else:
            return self.play_pause()

    def pause(self) -> Dict[str, Any]:
        """
        Pause playback.

        Returns:
            Result dictionary
        """
        if hasattr(self.interface, 'pause'):
            return self.interface.pause()
        else:
            return self.play_pause()

    def next_track(self) -> Dict[str, Any]:
        """
        Skip to next track.

        Returns:
            Result dictionary
        """
        return self.interface.next_track()

    def previous_track(self) -> Dict[str, Any]:
        """
        Go to previous track.

        Returns:
            Result dictionary
        """
        return self.interface.previous_track()

    def stop(self) -> Dict[str, Any]:
        """
        Stop playback.

        Returns:
            Result dictionary
        """
        return self.interface.stop()

    def volume_up(self, step: int = 5) -> Dict[str, Any]:
        """
        Increase volume.

        Args:
            step: Volume step (0-100)

        Returns:
            Result dictionary
        """
        if not PYCAW_AVAILABLE:
            return {
                'success': False,
                'error': 'Volume control not available (pycaw not installed)'
            }

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            # Get current volume (0.0 to 1.0)
            current = volume.GetMasterVolumeLevelScalar()

            # Increase by step
            new_volume = min(current + (step / 100.0), 1.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)

            return {
                'success': True,
                'action': 'volume_up',
                'volume': int(new_volume * 100),
                'message': f'Volume increased to {int(new_volume * 100)}%'
            }

        except Exception as e:
            logger.error(f"Failed to increase volume: {e}")
            return {
                'success': False,
                'error': f'Failed to increase volume: {str(e)}'
            }

    def volume_down(self, step: int = 5) -> Dict[str, Any]:
        """
        Decrease volume.

        Args:
            step: Volume step (0-100)

        Returns:
            Result dictionary
        """
        if not PYCAW_AVAILABLE:
            return {
                'success': False,
                'error': 'Volume control not available (pycaw not installed)'
            }

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            # Get current volume (0.0 to 1.0)
            current = volume.GetMasterVolumeLevelScalar()

            # Decrease by step
            new_volume = max(current - (step / 100.0), 0.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)

            return {
                'success': True,
                'action': 'volume_down',
                'volume': int(new_volume * 100),
                'message': f'Volume decreased to {int(new_volume * 100)}%'
            }

        except Exception as e:
            logger.error(f"Failed to decrease volume: {e}")
            return {
                'success': False,
                'error': f'Failed to decrease volume: {str(e)}'
            }

    def set_volume(self, level: int) -> Dict[str, Any]:
        """
        Set volume to specific level.

        Args:
            level: Volume level (0-100)

        Returns:
            Result dictionary
        """
        if not PYCAW_AVAILABLE:
            return {
                'success': False,
                'error': 'Volume control not available (pycaw not installed)'
            }

        if not 0 <= level <= 100:
            return {
                'success': False,
                'error': 'Volume level must be between 0 and 100'
            }

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            # Set volume (0.0 to 1.0)
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)

            return {
                'success': True,
                'action': 'set_volume',
                'volume': level,
                'message': f'Volume set to {level}%'
            }

        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return {
                'success': False,
                'error': f'Failed to set volume: {str(e)}'
            }

    def get_volume(self) -> Dict[str, Any]:
        """
        Get current volume level.

        Returns:
            Result dictionary with current volume
        """
        if not PYCAW_AVAILABLE:
            return {
                'success': False,
                'error': 'Volume control not available (pycaw not installed)'
            }

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            # Get current volume (0.0 to 1.0)
            current = volume.GetMasterVolumeLevelScalar()

            return {
                'success': True,
                'volume': int(current * 100),
                'is_muted': volume.GetMute() == 1
            }

        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return {
                'success': False,
                'error': f'Failed to get volume: {str(e)}'
            }

    def mute(self) -> Dict[str, Any]:
        """
        Mute audio.

        Returns:
            Result dictionary
        """
        if not PYCAW_AVAILABLE:
            return {
                'success': False,
                'error': 'Volume control not available (pycaw not installed)'
            }

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            volume.SetMute(1, None)

            return {
                'success': True,
                'action': 'mute',
                'message': 'Audio muted'
            }

        except Exception as e:
            logger.error(f"Failed to mute: {e}")
            return {
                'success': False,
                'error': f'Failed to mute: {str(e)}'
            }

    def unmute(self) -> Dict[str, Any]:
        """
        Unmute audio.

        Returns:
            Result dictionary
        """
        if not PYCAW_AVAILABLE:
            return {
                'success': False,
                'error': 'Volume control not available (pycaw not installed)'
            }

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            volume.SetMute(0, None)

            return {
                'success': True,
                'action': 'unmute',
                'message': 'Audio unmuted'
            }

        except Exception as e:
            logger.error(f"Failed to unmute: {e}")
            return {
                'success': False,
                'error': f'Failed to unmute: {str(e)}'
            }

    def toggle_mute(self) -> Dict[str, Any]:
        """
        Toggle mute/unmute.

        Returns:
            Result dictionary
        """
        volume_info = self.get_volume()
        if volume_info['success']:
            if volume_info.get('is_muted'):
                return self.unmute()
            else:
                return self.mute()
        else:
            return volume_info

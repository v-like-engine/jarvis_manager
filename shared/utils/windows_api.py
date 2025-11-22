"""Windows API utilities using pywin32."""

import sys
import logging
from typing import Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Windows-specific imports (will only work on Windows)
if sys.platform == 'win32':
    try:
        import win32api
        import win32con
        import win32gui
        import win32process
        import win32com.client
        import winreg
        WINDOWS_AVAILABLE = True
    except ImportError:
        logger.warning("pywin32 not available, Windows API features disabled")
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False
    logger.info("Not running on Windows, Windows API features disabled")


class WindowsAPI:
    """Windows API wrapper for common operations."""

    @staticmethod
    def is_available() -> bool:
        """Check if Windows API is available."""
        return WINDOWS_AVAILABLE

    @staticmethod
    def get_foreground_window() -> Optional[int]:
        """
        Get handle of foreground window.

        Returns:
            Window handle or None
        """
        if not WINDOWS_AVAILABLE:
            return None
        try:
            return win32gui.GetForegroundWindow()
        except Exception as e:
            logger.error(f"Failed to get foreground window: {e}")
            return None

    @staticmethod
    def get_window_text(hwnd: int) -> str:
        """
        Get window title text.

        Args:
            hwnd: Window handle

        Returns:
            Window title
        """
        if not WINDOWS_AVAILABLE:
            return ""
        try:
            return win32gui.GetWindowText(hwnd)
        except Exception as e:
            logger.error(f"Failed to get window text: {e}")
            return ""

    @staticmethod
    def find_window_by_title(title: str, partial: bool = True) -> Optional[int]:
        """
        Find window by title.

        Args:
            title: Window title to search for
            partial: Allow partial matches

        Returns:
            Window handle or None
        """
        if not WINDOWS_AVAILABLE:
            return None

        title_lower = title.lower()
        found_hwnd = None

        def callback(hwnd, _):
            nonlocal found_hwnd
            window_text = WindowsAPI.get_window_text(hwnd)
            if partial:
                if title_lower in window_text.lower():
                    found_hwnd = hwnd
                    return False  # Stop enumeration
            else:
                if title_lower == window_text.lower():
                    found_hwnd = hwnd
                    return False
            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            logger.error(f"Failed to enumerate windows: {e}")

        return found_hwnd

    @staticmethod
    def close_window(hwnd: int) -> bool:
        """
        Close a window by sending WM_CLOSE message.

        Args:
            hwnd: Window handle

        Returns:
            True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to close window: {e}")
            return False

    @staticmethod
    def read_registry_value(
        key_path: str,
        value_name: str,
        hive=None
    ) -> Optional[str]:
        """
        Read a value from Windows registry.

        Args:
            key_path: Registry key path
            value_name: Value name
            hive: Registry hive (defaults to HKEY_LOCAL_MACHINE)

        Returns:
            Registry value or None
        """
        if not WINDOWS_AVAILABLE:
            return None

        if hive is None:
            hive = winreg.HKEY_LOCAL_MACHINE

        try:
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except Exception as e:
            logger.debug(f"Failed to read registry value {key_path}\\{value_name}: {e}")
            return None

    @staticmethod
    def write_registry_value(
        key_path: str,
        value_name: str,
        value: str,
        hive=None,
        value_type=None
    ) -> bool:
        """
        Write a value to Windows registry.

        Args:
            key_path: Registry key path
            value_name: Value name
            value: Value to write
            hive: Registry hive (defaults to HKEY_CURRENT_USER)
            value_type: Value type (defaults to REG_SZ)

        Returns:
            True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False

        if hive is None:
            hive = winreg.HKEY_CURRENT_USER
        if value_type is None:
            value_type = winreg.REG_SZ

        try:
            key = winreg.OpenKey(
                hive,
                key_path,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, value_name, 0, value_type, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            logger.error(f"Failed to write registry value {key_path}\\{value_name}: {e}")
            return False

    @staticmethod
    def delete_registry_value(
        key_path: str,
        value_name: str,
        hive=None
    ) -> bool:
        """
        Delete a value from Windows registry.

        Args:
            key_path: Registry key path
            value_name: Value name
            hive: Registry hive (defaults to HKEY_CURRENT_USER)

        Returns:
            True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False

        if hive is None:
            hive = winreg.HKEY_CURRENT_USER

        try:
            key = winreg.OpenKey(
                hive,
                key_path,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, value_name)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete registry value {key_path}\\{value_name}: {e}")
            return False

    @staticmethod
    def get_special_folder(folder_id: int) -> Optional[Path]:
        """
        Get path to a special Windows folder.

        Args:
            folder_id: CSIDL folder ID (e.g., CSIDL_STARTMENU)

        Returns:
            Folder path or None
        """
        if not WINDOWS_AVAILABLE:
            return None

        try:
            from win32com.shell import shell, shellcon
            path = shell.SHGetFolderPath(0, folder_id, None, 0)
            return Path(path)
        except Exception as e:
            logger.error(f"Failed to get special folder {folder_id}: {e}")
            return None

    @staticmethod
    def send_media_key(key: str) -> bool:
        """
        Send a media key press (play/pause/next/previous).

        Args:
            key: Key name ('play', 'pause', 'next', 'previous', 'stop')

        Returns:
            True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False

        key_codes = {
            'play': win32con.VK_MEDIA_PLAY_PAUSE,
            'pause': win32con.VK_MEDIA_PLAY_PAUSE,
            'next': win32con.VK_MEDIA_NEXT_TRACK,
            'previous': win32con.VK_MEDIA_PREV_TRACK,
            'stop': win32con.VK_MEDIA_STOP,
        }

        key_code = key_codes.get(key.lower())
        if not key_code:
            logger.error(f"Unknown media key: {key}")
            return False

        try:
            # Simulate key press
            win32api.keybd_event(key_code, 0, 0, 0)
            # Simulate key release
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to send media key {key}: {e}")
            return False

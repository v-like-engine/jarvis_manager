"""Screen and power control for Windows."""

import logging
import subprocess
import platform
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ScreenController:
    """
    Control screen and power operations.

    Provides:
    - Lock screen
    - Sleep
    - Shutdown
    - Restart
    - Monitor on/off
    """

    def __init__(self):
        """Initialize screen controller."""
        self.is_windows = platform.system() == 'Windows'
        logger.info(f"ScreenController initialized (Windows: {self.is_windows})")

    def lock_screen(self) -> Dict[str, Any]:
        """
        Lock the screen.

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                # Use rundll32 to lock workstation
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)

                return {
                    'success': True,
                    'message': 'Screen locked'
                }
            else:
                # For Linux (if needed for testing)
                logger.warning("Lock screen not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Lock screen only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error locking screen: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def sleep(self) -> Dict[str, Any]:
        """
        Put computer to sleep.

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                # Use rundll32 to sleep
                subprocess.Popen(
                    ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0', '1', '0'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                return {
                    'success': True,
                    'message': 'Computer going to sleep'
                }
            else:
                logger.warning("Sleep not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Sleep only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error sleeping computer: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def shutdown(self, force: bool = False, timeout: int = 60) -> Dict[str, Any]:
        """
        Shutdown the computer.

        Args:
            force: Force shutdown even if apps are open
            timeout: Seconds until shutdown (default: 60)

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                # Build shutdown command
                cmd = ['shutdown', '/s', '/t', str(timeout)]

                if force:
                    cmd.append('/f')  # Force close applications

                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

                return {
                    'success': True,
                    'timeout': timeout,
                    'force': force,
                    'message': f'Computer will shutdown in {timeout} seconds'
                }
            else:
                logger.warning("Shutdown not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Shutdown only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error shutting down: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def restart(self, force: bool = False, timeout: int = 60) -> Dict[str, Any]:
        """
        Restart the computer.

        Args:
            force: Force restart even if apps are open
            timeout: Seconds until restart (default: 60)

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                # Build restart command
                cmd = ['shutdown', '/r', '/t', str(timeout)]

                if force:
                    cmd.append('/f')  # Force close applications

                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

                return {
                    'success': True,
                    'timeout': timeout,
                    'force': force,
                    'message': f'Computer will restart in {timeout} seconds'
                }
            else:
                logger.warning("Restart not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Restart only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error restarting: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def cancel_shutdown(self) -> Dict[str, Any]:
        """
        Cancel a pending shutdown or restart.

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                subprocess.run(['shutdown', '/a'], check=True)

                return {
                    'success': True,
                    'message': 'Shutdown/restart cancelled'
                }
            else:
                logger.warning("Cancel shutdown not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Cancel shutdown only available on Windows'
                }

        except subprocess.CalledProcessError:
            return {
                'success': False,
                'error': 'No shutdown to cancel'
            }
        except Exception as e:
            logger.error(f"Error cancelling shutdown: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def turn_off_monitor(self) -> Dict[str, Any]:
        """
        Turn off monitor(s).

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                # Send monitor off command
                # WM_SYSCOMMAND = 0x0112, SC_MONITORPOWER = 0xF170, 2 = off
                import ctypes
                ctypes.windll.user32.SendMessageW(
                    0xFFFF,  # HWND_BROADCAST
                    0x0112,  # WM_SYSCOMMAND
                    0xF170,  # SC_MONITORPOWER
                    2        # Power off
                )

                return {
                    'success': True,
                    'message': 'Monitor turned off'
                }
            else:
                logger.warning("Monitor control not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Monitor control only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error turning off monitor: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def turn_on_monitor(self) -> Dict[str, Any]:
        """
        Turn on monitor(s).

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                # Send monitor on command
                # WM_SYSCOMMAND = 0x0112, SC_MONITORPOWER = 0xF170, -1 = on
                import ctypes
                ctypes.windll.user32.SendMessageW(
                    0xFFFF,  # HWND_BROADCAST
                    0x0112,  # WM_SYSCOMMAND
                    0xF170,  # SC_MONITORPOWER
                    -1       # Power on
                )

                return {
                    'success': True,
                    'message': 'Monitor turned on'
                }
            else:
                logger.warning("Monitor control not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Monitor control only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error turning on monitor: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def hibernate(self) -> Dict[str, Any]:
        """
        Hibernate the computer.

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                # Use shutdown command for hibernate
                subprocess.Popen(
                    ['shutdown', '/h'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                return {
                    'success': True,
                    'message': 'Computer hibernating'
                }
            else:
                logger.warning("Hibernate not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Hibernate only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error hibernating: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def log_off(self) -> Dict[str, Any]:
        """
        Log off current user.

        Returns:
            Dictionary with result
        """
        try:
            if self.is_windows:
                subprocess.Popen(
                    ['shutdown', '/l'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                return {
                    'success': True,
                    'message': 'Logging off'
                }
            else:
                logger.warning("Log off not implemented for non-Windows")
                return {
                    'success': False,
                    'error': 'Log off only available on Windows'
                }

        except Exception as e:
            logger.error(f"Error logging off: {e}")
            return {
                'success': False,
                'error': str(e)
            }

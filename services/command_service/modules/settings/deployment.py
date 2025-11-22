"""Deployment utilities for Gerald Desktop Manager."""

import os
import sys
import logging
import winreg
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Manage deployment, installation, and Windows service integration.

    Features:
    - System tray icon setup
    - Windows service wrapper
    - Startup configuration
    - Uninstallation
    """

    def __init__(self):
        """Initialize deployment manager."""
        self.app_name = "Gerald Desktop Manager"
        self.service_name = "GeraldDesktopManager"
        self.install_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent.parent.parent.parent.parent

        logger.info("DeploymentManager initialized")

    def check_admin_rights(self) -> bool:
        """
        Check if running with administrator privileges.

        Returns:
            True if admin, False otherwise
        """
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def create_start_menu_shortcut(self) -> Dict[str, Any]:
        """
        Create Start Menu shortcut.

        Returns:
            Dictionary with result
        """
        try:
            import win32com.client

            # Get Start Menu path
            start_menu = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
            shortcut_path = start_menu / f"{self.app_name}.lnk"

            # Create shortcut
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = sys.executable
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = sys.executable
            shortcut.Description = self.app_name
            shortcut.save()

            return {
                'success': True,
                'path': str(shortcut_path),
                'message': 'Start Menu shortcut created'
            }

        except Exception as e:
            logger.error(f"Error creating shortcut: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_desktop_shortcut(self) -> Dict[str, Any]:
        """
        Create Desktop shortcut.

        Returns:
            Dictionary with result
        """
        try:
            import win32com.client

            # Get Desktop path
            desktop = Path(os.environ['USERPROFILE']) / 'Desktop'
            shortcut_path = desktop / f"{self.app_name}.lnk"

            # Create shortcut
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = sys.executable
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = sys.executable
            shortcut.Description = self.app_name
            shortcut.save()

            return {
                'success': True,
                'path': str(shortcut_path),
                'message': 'Desktop shortcut created'
            }

        except Exception as e:
            logger.error(f"Error creating desktop shortcut: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def install_windows_service(self) -> Dict[str, Any]:
        """
        Install as Windows service.

        Requires administrator privileges.

        Returns:
            Dictionary with result
        """
        if not self.check_admin_rights():
            return {
                'success': False,
                'error': 'Administrator privileges required'
            }

        try:
            # Path to service wrapper script
            service_script = self.install_dir / 'windows_service.py'

            if not service_script.exists():
                return {
                    'success': False,
                    'error': 'Service wrapper script not found'
                }

            # Install service using pywin32
            cmd = [
                sys.executable,
                str(service_script),
                '--startup', 'auto',
                'install'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Windows service installed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Service installation failed: {result.stderr}'
                }

        except Exception as e:
            logger.error(f"Error installing service: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def uninstall_windows_service(self) -> Dict[str, Any]:
        """
        Uninstall Windows service.

        Requires administrator privileges.

        Returns:
            Dictionary with result
        """
        if not self.check_admin_rights():
            return {
                'success': False,
                'error': 'Administrator privileges required'
            }

        try:
            service_script = self.install_dir / 'windows_service.py'

            if not service_script.exists():
                return {
                    'success': False,
                    'error': 'Service wrapper script not found'
                }

            # Uninstall service
            cmd = [sys.executable, str(service_script), 'remove']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Windows service uninstalled successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Service uninstallation failed: {result.stderr}'
                }

        except Exception as e:
            logger.error(f"Error uninstalling service: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def start_service(self) -> Dict[str, Any]:
        """
        Start Windows service.

        Returns:
            Dictionary with result
        """
        try:
            result = subprocess.run(
                ['sc', 'start', self.service_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Service started'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }

        except Exception as e:
            logger.error(f"Error starting service: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def stop_service(self) -> Dict[str, Any]:
        """
        Stop Windows service.

        Returns:
            Dictionary with result
        """
        try:
            result = subprocess.run(
                ['sc', 'stop', self.service_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Service stopped'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }

        except Exception as e:
            logger.error(f"Error stopping service: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get Windows service status.

        Returns:
            Dictionary with status
        """
        try:
            result = subprocess.run(
                ['sc', 'query', self.service_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Parse output for status
                status = 'UNKNOWN'
                for line in result.stdout.split('\n'):
                    if 'STATE' in line:
                        if 'RUNNING' in line:
                            status = 'RUNNING'
                        elif 'STOPPED' in line:
                            status = 'STOPPED'
                        break

                return {
                    'success': True,
                    'status': status,
                    'installed': True
                }
            else:
                return {
                    'success': True,
                    'status': 'NOT_INSTALLED',
                    'installed': False
                }

        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def remove_shortcuts(self) -> Dict[str, Any]:
        """
        Remove all shortcuts.

        Returns:
            Dictionary with result
        """
        try:
            removed = []

            # Remove Start Menu shortcut
            start_menu = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
            start_shortcut = start_menu / f"{self.app_name}.lnk"
            if start_shortcut.exists():
                start_shortcut.unlink()
                removed.append(str(start_shortcut))

            # Remove Desktop shortcut
            desktop = Path(os.environ['USERPROFILE']) / 'Desktop'
            desktop_shortcut = desktop / f"{self.app_name}.lnk"
            if desktop_shortcut.exists():
                desktop_shortcut.unlink()
                removed.append(str(desktop_shortcut))

            return {
                'success': True,
                'removed': removed,
                'message': f'Removed {len(removed)} shortcut(s)'
            }

        except Exception as e:
            logger.error(f"Error removing shortcuts: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_uninstaller(self, uninstall_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Create uninstaller script/registry entry.

        Args:
            uninstall_path: Path where uninstall.py is located

        Returns:
            Dictionary with result
        """
        try:
            if uninstall_path is None:
                uninstall_path = self.install_dir / 'uninstall.py'

            # Add to Windows Uninstall Programs registry
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\GeraldDesktopManager"

            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)

            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, self.app_name)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{sys.executable}" "{uninstall_path}"')
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, sys.executable)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Gerald AI")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")

            winreg.CloseKey(key)

            return {
                'success': True,
                'message': 'Uninstaller registered'
            }

        except Exception as e:
            logger.error(f"Error creating uninstaller: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def remove_uninstaller(self) -> Dict[str, Any]:
        """
        Remove uninstaller registry entry.

        Returns:
            Dictionary with result
        """
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\GeraldDesktopManager"

            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)

            return {
                'success': True,
                'message': 'Uninstaller registry entry removed'
            }

        except FileNotFoundError:
            return {
                'success': True,
                'message': 'Uninstaller was not registered'
            }
        except Exception as e:
            logger.error(f"Error removing uninstaller: {e}")
            return {
                'success': False,
                'error': str(e)
            }

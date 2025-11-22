"""Manage Windows startup configuration."""

import sys
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

if sys.platform == 'win32':
    try:
        import winreg
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
        logging.warning("Windows registry module not available")
else:
    WINDOWS_AVAILABLE = False

logger = logging.getLogger(__name__)


class StartupManager:
    """
    Manage Windows startup configuration.

    Features:
    - Enable/disable startup via Registry
    - Enable/disable startup via Task Scheduler (more reliable)
    - Check startup status
    """

    REGISTRY_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "GeraldDesktopManager"

    def __init__(self, executable_path: Optional[str] = None):
        """
        Initialize startup manager.

        Args:
            executable_path: Path to main executable (defaults to current Python script)
        """
        if executable_path:
            self.executable_path = executable_path
        else:
            # Default to current Python executable + main script
            self.executable_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

        logger.info("Startup manager initialized")

    def enable_startup_registry(self) -> Dict[str, Any]:
        """
        Enable startup via Windows Registry (User-level).

        Returns:
            Result dictionary
        """
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows registry not available'
            }

        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )

            # Set value
            winreg.SetValueEx(
                key,
                self.APP_NAME,
                0,
                winreg.REG_SZ,
                self.executable_path
            )

            winreg.CloseKey(key)

            logger.info(f"Enabled startup via registry: {self.executable_path}")
            return {
                'success': True,
                'method': 'registry',
                'message': 'Startup enabled (Registry)'
            }

        except PermissionError:
            logger.error("Permission denied accessing registry")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to enable startup via registry: {e}")
            return {
                'success': False,
                'error': f'Failed to enable startup: {str(e)}'
            }

    def disable_startup_registry(self) -> Dict[str, Any]:
        """
        Disable startup via Windows Registry.

        Returns:
            Result dictionary
        """
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows registry not available'
            }

        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )

            # Delete value
            try:
                winreg.DeleteValue(key, self.APP_NAME)
                winreg.CloseKey(key)

                logger.info("Disabled startup via registry")
                return {
                    'success': True,
                    'method': 'registry',
                    'message': 'Startup disabled (Registry)'
                }

            except FileNotFoundError:
                winreg.CloseKey(key)
                return {
                    'success': True,
                    'message': 'Startup was not enabled'
                }

        except PermissionError:
            logger.error("Permission denied accessing registry")
            return {
                'success': False,
                'error': 'Permission denied'
            }
        except Exception as e:
            logger.error(f"Failed to disable startup via registry: {e}")
            return {
                'success': False,
                'error': f'Failed to disable startup: {str(e)}'
            }

    def is_startup_enabled_registry(self) -> bool:
        """
        Check if startup is enabled via Registry.

        Returns:
            True if enabled
        """
        if not WINDOWS_AVAILABLE:
            return False

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY_PATH,
                0,
                winreg.KEY_READ
            )

            try:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False

        except Exception as e:
            logger.debug(f"Error checking startup status: {e}")
            return False

    def enable_startup_task_scheduler(self) -> Dict[str, Any]:
        """
        Enable startup via Task Scheduler (more reliable).

        Returns:
            Result dictionary
        """
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows not available'
            }

        try:
            import subprocess

            # Build schtasks command
            # Create a task that runs at user logon
            task_name = self.APP_NAME
            command = [
                'schtasks',
                '/create',
                '/tn', task_name,
                '/tr', self.executable_path,
                '/sc', 'onlogon',
                '/rl', 'highest',
                '/f'  # Force create (overwrite if exists)
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Enabled startup via Task Scheduler")
                return {
                    'success': True,
                    'method': 'task_scheduler',
                    'message': 'Startup enabled (Task Scheduler)'
                }
            else:
                logger.error(f"Failed to create scheduled task: {result.stderr}")
                return {
                    'success': False,
                    'error': f'Failed to create scheduled task: {result.stderr}'
                }

        except Exception as e:
            logger.error(f"Failed to enable startup via Task Scheduler: {e}")
            return {
                'success': False,
                'error': f'Failed to enable startup: {str(e)}'
            }

    def disable_startup_task_scheduler(self) -> Dict[str, Any]:
        """
        Disable startup via Task Scheduler.

        Returns:
            Result dictionary
        """
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': 'Windows not available'
            }

        try:
            import subprocess

            task_name = self.APP_NAME
            command = [
                'schtasks',
                '/delete',
                '/tn', task_name,
                '/f'  # Force delete
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Disabled startup via Task Scheduler")
                return {
                    'success': True,
                    'method': 'task_scheduler',
                    'message': 'Startup disabled (Task Scheduler)'
                }
            else:
                # Task might not exist
                if 'cannot find' in result.stderr.lower():
                    return {
                        'success': True,
                        'message': 'Startup was not enabled'
                    }
                else:
                    logger.error(f"Failed to delete scheduled task: {result.stderr}")
                    return {
                        'success': False,
                        'error': f'Failed to delete scheduled task: {result.stderr}'
                    }

        except Exception as e:
            logger.error(f"Failed to disable startup via Task Scheduler: {e}")
            return {
                'success': False,
                'error': f'Failed to disable startup: {str(e)}'
            }

    def get_startup_status(self) -> Dict[str, Any]:
        """
        Get current startup status.

        Returns:
            Status dictionary
        """
        registry_enabled = self.is_startup_enabled_registry()

        # Check Task Scheduler
        task_scheduler_enabled = False
        if WINDOWS_AVAILABLE:
            try:
                import subprocess
                result = subprocess.run(
                    ['schtasks', '/query', '/tn', self.APP_NAME],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                task_scheduler_enabled = result.returncode == 0
            except Exception:
                pass

        return {
            'success': True,
            'registry': registry_enabled,
            'task_scheduler': task_scheduler_enabled,
            'enabled': registry_enabled or task_scheduler_enabled
        }

"""Windows application finder and discoverer."""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

if sys.platform == 'win32':
    try:
        import winreg
        from win32com.shell import shell, shellcon
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
        logging.warning("Windows modules not available")
else:
    WINDOWS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AppFinder:
    """
    Find and discover installed Windows applications.

    Scans multiple locations:
    - Start Menu
    - Program Files
    - Registry App Paths
    - Windows Store apps
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize app finder.

        Args:
            config_path: Path to app_aliases.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "app_aliases.yaml"

        self.config_path = config_path
        self.aliases = self._load_aliases()
        logger.info("App finder initialized")

    def _load_aliases(self) -> Dict[str, List[str]]:
        """Load application aliases from config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('aliases', {})
        except Exception as e:
            logger.error(f"Failed to load app aliases: {e}")
            return {}

    def discover_apps(self) -> List[Dict[str, Any]]:
        """
        Discover all installed applications.

        Returns:
            List of application info dictionaries
        """
        apps = []

        # Scan Start Menu
        apps.extend(self._scan_start_menu())

        # Scan Program Files
        apps.extend(self._scan_program_files())

        # Scan Registry
        apps.extend(self._scan_registry())

        # Remove duplicates based on exe path
        unique_apps = {}
        for app in apps:
            exe_path = app.get('exe_path', '').lower()
            if exe_path and exe_path not in unique_apps:
                unique_apps[exe_path] = app

        result = list(unique_apps.values())
        logger.info(f"Discovered {len(result)} unique applications")
        return result

    def _scan_start_menu(self) -> List[Dict[str, Any]]:
        """Scan Start Menu for applications."""
        if not WINDOWS_AVAILABLE:
            logger.debug("Windows API not available, skipping Start Menu scan")
            return []

        apps = []

        try:
            # Get Start Menu paths
            start_menu_paths = [
                shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_STARTMENU, None, 0),
                shell.SHGetFolderPath(0, shellcon.CSIDL_STARTMENU, None, 0),
            ]

            for start_menu in start_menu_paths:
                start_path = Path(start_menu)
                if not start_path.exists():
                    continue

                # Find all .lnk files
                for lnk_file in start_path.rglob("*.lnk"):
                    try:
                        # Get shortcut target
                        from win32com.client import Dispatch
                        shell_obj = Dispatch("WScript.Shell")
                        shortcut = shell_obj.CreateShortcut(str(lnk_file))
                        target = shortcut.TargetPath

                        if target and target.lower().endswith('.exe'):
                            apps.append({
                                'name': lnk_file.stem,
                                'exe_path': target,
                                'shortcut_path': str(lnk_file),
                                'location': 'start_menu',
                            })
                    except Exception as e:
                        logger.debug(f"Failed to process shortcut {lnk_file}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Failed to scan Start Menu: {e}")

        logger.debug(f"Found {len(apps)} apps in Start Menu")
        return apps

    def _scan_program_files(self) -> List[Dict[str, Any]]:
        """Scan Program Files directories for executables."""
        apps = []

        # Common program directories
        program_dirs = [
            Path("C:\\Program Files"),
            Path("C:\\Program Files (x86)"),
        ]

        for program_dir in program_dirs:
            if not program_dir.exists():
                continue

            try:
                # Scan top-level directories only (to avoid deep recursion)
                for app_dir in program_dir.iterdir():
                    if not app_dir.is_dir():
                        continue

                    # Look for .exe files in this directory and one level deep
                    exe_files = list(app_dir.glob("*.exe"))
                    exe_files.extend(app_dir.glob("*/*.exe"))

                    for exe_file in exe_files:
                        # Skip installers and uninstallers
                        name_lower = exe_file.name.lower()
                        if any(skip in name_lower for skip in [
                            'uninstall', 'uninst', 'setup', 'install',
                            'update', 'crash', 'helper'
                        ]):
                            continue

                        apps.append({
                            'name': exe_file.stem,
                            'exe_path': str(exe_file),
                            'location': 'program_files',
                        })

            except PermissionError:
                logger.debug(f"No permission to scan {program_dir}")
                continue
            except Exception as e:
                logger.error(f"Failed to scan {program_dir}: {e}")
                continue

        logger.debug(f"Found {len(apps)} apps in Program Files")
        return apps

    def _scan_registry(self) -> List[Dict[str, Any]]:
        """Scan Windows Registry for registered applications."""
        if not WINDOWS_AVAILABLE:
            logger.debug("Windows API not available, skipping Registry scan")
            return []

        apps = []

        # Registry paths to check
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        ]

        for hive, path in registry_paths:
            try:
                key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)

                        # Get default value (executable path)
                        exe_path, _ = winreg.QueryValueEx(subkey, "")
                        winreg.CloseKey(subkey)

                        if exe_path and os.path.exists(exe_path):
                            apps.append({
                                'name': Path(subkey_name).stem,
                                'exe_path': exe_path,
                                'location': 'registry',
                            })

                        i += 1
                    except OSError:
                        break

                winreg.CloseKey(key)

            except Exception as e:
                logger.debug(f"Failed to scan registry path {path}: {e}")
                continue

        logger.debug(f"Found {len(apps)} apps in Registry")
        return apps

    def get_aliases_for_app(self, app_name: str) -> List[str]:
        """
        Get all aliases for an application.

        Args:
            app_name: Application name

        Returns:
            List of aliases
        """
        app_key = app_name.lower().replace(' ', '_')

        # Check if we have aliases for this app
        for key, aliases in self.aliases.items():
            if key == app_key or app_name.lower() in [a.lower() for a in aliases]:
                return aliases

        return [app_name]

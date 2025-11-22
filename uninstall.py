#!/usr/bin/env python3
"""
Gerald Desktop Manager - Uninstaller

This script removes Gerald Desktop Manager from the system.
"""

import os
import sys
import shutil
import winreg
from pathlib import Path


class Colors:
    """Terminal colors."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def remove_shortcuts():
    """Remove Start Menu and Desktop shortcuts."""
    print_info("Removing shortcuts...")

    removed = []
    failed = []

    # Start Menu shortcut
    try:
        start_menu = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
        shortcut = start_menu / "Gerald Desktop Manager.lnk"
        if shortcut.exists():
            shortcut.unlink()
            removed.append(str(shortcut))
    except Exception as e:
        failed.append(f"Start Menu shortcut: {e}")

    # Desktop shortcut
    try:
        desktop = Path(os.environ['USERPROFILE']) / 'Desktop'
        shortcut = desktop / "Gerald Desktop Manager.lnk"
        if shortcut.exists():
            shortcut.unlink()
            removed.append(str(shortcut))
    except Exception as e:
        failed.append(f"Desktop shortcut: {e}")

    if removed:
        for path in removed:
            print_success(f"Removed {path}")

    if failed:
        for error in failed:
            print_warning(error)

    return True


def remove_startup_entry():
    """Remove Windows startup entry."""
    print_info("Removing startup entry...")

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        try:
            winreg.DeleteValue(key, "GeraldDesktopManager")
            print_success("Removed startup entry")
        except FileNotFoundError:
            print_info("No startup entry found")

        winreg.CloseKey(key)

        return True

    except Exception as e:
        print_error(f"Failed to remove startup entry: {e}")
        return False


def remove_uninstall_entry():
    """Remove uninstall registry entry."""
    print_info("Removing uninstall registry entry...")

    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\GeraldDesktopManager"

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            print_success("Removed uninstall entry")
        except FileNotFoundError:
            print_info("No uninstall entry found")

        return True

    except Exception as e:
        print_error(f"Failed to remove uninstall entry: {e}")
        return False


def stop_services():
    """Stop any running Gerald services."""
    print_info("Stopping services...")

    try:
        import subprocess

        # Try to stop Windows service if installed
        try:
            subprocess.run(
                ['sc', 'stop', 'GeraldDesktopManager'],
                capture_output=True,
                timeout=5
            )
            print_success("Stopped Windows service")
        except:
            pass

        print_success("Services stopped")
        return True

    except Exception as e:
        print_warning(f"Could not stop services: {e}")
        return True


def remove_user_data():
    """Remove user data (cache, logs, preferences)."""
    print_info("Removing user data...")

    response = input(f"\n{Colors.OKCYAN}Remove user data (logs, cache, preferences)? (y/n): {Colors.ENDC}").lower()

    if response != 'y':
        print_info("Keeping user data")
        return True

    removed = []
    failed = []

    # Directories to remove
    data_dirs = [
        'logs',
        'services/asr_service/logs',
        'services/llm_service/logs',
        'services/command_service/logs',
        'services/command_service/cache',
        'services/command_service/data',
    ]

    for directory in data_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                removed.append(directory)
            except Exception as e:
                failed.append(f"{directory}: {e}")

    if removed:
        for path in removed:
            print_success(f"Removed {path}")

    if failed:
        for error in failed:
            print_warning(error)

    return True


def remove_config():
    """Remove configuration files."""
    print_info("Removing configuration...")

    response = input(f"\n{Colors.OKCYAN}Remove configuration files? (y/n): {Colors.ENDC}").lower()

    if response != 'y':
        print_info("Keeping configuration files")
        return True

    try:
        config_dir = Path('config')
        if config_dir.exists():
            shutil.rmtree(config_dir)
            print_success("Removed configuration directory")

        return True

    except Exception as e:
        print_error(f"Failed to remove configuration: {e}")
        return False


def uninstall_windows_service():
    """Uninstall Windows service if installed."""
    print_info("Checking for Windows service...")

    try:
        import subprocess

        # Check if service exists
        result = subprocess.run(
            ['sc', 'query', 'GeraldDesktopManager'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_info("Windows service found")

            response = input(f"\n{Colors.OKCYAN}Uninstall Windows service? (requires admin) (y/n): {Colors.ENDC}").lower()

            if response == 'y':
                # Stop service
                subprocess.run(['sc', 'stop', 'GeraldDesktopManager'], capture_output=True)

                # Delete service
                result = subprocess.run(
                    ['sc', 'delete', 'GeraldDesktopManager'],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print_success("Windows service uninstalled")
                else:
                    print_error(f"Failed to uninstall service: {result.stderr}")
        else:
            print_info("No Windows service installed")

        return True

    except Exception as e:
        print_warning(f"Could not check/remove Windows service: {e}")
        return True


def main():
    """Main uninstallation routine."""
    print_header("Gerald Desktop Manager - Uninstallation")

    print(f"{Colors.WARNING}This will remove Gerald Desktop Manager from your system.{Colors.ENDC}\n")

    response = input(f"{Colors.OKCYAN}Are you sure you want to uninstall? (y/n): {Colors.ENDC}").lower()

    if response != 'y':
        print_info("Uninstallation cancelled")
        return

    print()

    # Stop services
    stop_services()

    # Remove Windows service
    uninstall_windows_service()

    # Remove shortcuts
    remove_shortcuts()

    # Remove startup entry
    remove_startup_entry()

    # Remove uninstall entry
    remove_uninstall_entry()

    # Remove user data
    remove_user_data()

    # Remove configuration
    remove_config()

    # Final message
    print_header("Uninstallation Complete")

    print(f"{Colors.OKGREEN}Gerald Desktop Manager has been uninstalled.{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}Note:{Colors.ENDC}")
    print(f"  - The installation directory was not removed")
    print(f"  - You can manually delete it if desired")
    print(f"  - To reinstall, run: python install.py\n")

    print(f"{Colors.OKCYAN}Thank you for using Gerald Desktop Manager!{Colors.ENDC}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Uninstallation cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Uninstallation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

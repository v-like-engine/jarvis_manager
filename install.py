#!/usr/bin/env python3
"""
Gerald Desktop Manager - Interactive Installer

This script installs Gerald Desktop Manager with voice control capabilities.
"""

import os
import sys
import subprocess
from pathlib import Path
import platform


class Colors:
    """Terminal colors for better output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


def check_python_version():
    """Check Python version."""
    print_info("Checking Python version...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8 or higher required (found {version.major}.{version.minor})")
        return False

    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_platform():
    """Check if running on Windows."""
    print_info("Checking platform...")

    if platform.system() != 'Windows':
        print_error("Gerald Desktop Manager requires Windows")
        print_warning("Some features will not work on non-Windows platforms")
        return False

    print_success(f"Windows {platform.release()}")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print_info("Installing dependencies...")

    requirements_files = [
        'requirements.txt',
        'services/asr_service/requirements.txt',
        'services/llm_service/requirements.txt',
        'services/command_service/requirements.txt',
    ]

    for req_file in requirements_files:
        req_path = Path(req_file)
        if req_path.exists():
            print_info(f"Installing from {req_file}...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '-r', str(req_path),
                    '--quiet'
                ])
                print_success(f"Installed dependencies from {req_file}")
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install dependencies from {req_file}")
                return False

    return True


def create_directories():
    """Create necessary directories."""
    print_info("Creating directories...")

    directories = [
        'logs',
        'services/asr_service/logs',
        'services/llm_service/logs',
        'services/command_service/logs',
        'services/command_service/cache',
        'services/command_service/data',
        'data/characters',
    ]

    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print_success(f"Created {directory}")

    return True


def create_shortcuts():
    """Create Start Menu and Desktop shortcuts."""
    print_info("Creating shortcuts...")

    try:
        import win32com.client

        # Get paths
        install_dir = Path(__file__).parent.absolute()
        start_menu = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
        desktop = Path(os.environ['USERPROFILE']) / 'Desktop'

        # Create main launcher script if it doesn't exist
        launcher_script = install_dir / 'launch_gerald.py'
        if not launcher_script.exists():
            with open(launcher_script, 'w') as f:
                f.write('''#!/usr/bin/env python3
"""Launch Gerald Desktop Manager."""
import subprocess
import sys
from pathlib import Path

# Start all services
services = [
    'services/asr_service/src/main.py',
    'services/llm_service/src/main.py',
    'services/command_service/src/main.py',
]

for service in services:
    subprocess.Popen([sys.executable, service])

print("Gerald Desktop Manager started!")
''')

        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")

        # Start Menu shortcut
        shortcut_path = start_menu / "Gerald Desktop Manager.lnk"
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = sys.executable
        shortcut.Arguments = f'"{launcher_script}"'
        shortcut.WorkingDirectory = str(install_dir)
        shortcut.IconLocation = sys.executable
        shortcut.Description = "Gerald Desktop Manager - Voice Controlled AI Assistant"
        shortcut.save()
        print_success(f"Created Start Menu shortcut")

        # Desktop shortcut (optional)
        response = input(f"\n{Colors.OKCYAN}Create Desktop shortcut? (y/n): {Colors.ENDC}").lower()
        if response == 'y':
            shortcut_path = desktop / "Gerald Desktop Manager.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f'"{launcher_script}"'
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.IconLocation = sys.executable
            shortcut.Description = "Gerald Desktop Manager - Voice Controlled AI Assistant"
            shortcut.save()
            print_success(f"Created Desktop shortcut")

        return True

    except ImportError:
        print_warning("Could not create shortcuts (pywin32 not installed)")
        return True
    except Exception as e:
        print_error(f"Failed to create shortcuts: {e}")
        return False


def configure_startup():
    """Configure Windows startup."""
    print_info("Configure Windows startup...")

    response = input(f"\n{Colors.OKCYAN}Start Gerald automatically on Windows startup? (y/n): {Colors.ENDC}").lower()

    if response != 'y':
        return True

    try:
        import winreg

        install_dir = Path(__file__).parent.absolute()
        launcher_script = install_dir / 'launch_gerald.py'

        # Add to registry
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(
            key,
            "GeraldDesktopManager",
            0,
            winreg.REG_SZ,
            f'"{sys.executable}" "{launcher_script}"'
        )

        winreg.CloseKey(key)

        print_success("Added to Windows startup")
        return True

    except Exception as e:
        print_error(f"Failed to configure startup: {e}")
        return False


def create_config_wizard():
    """Run configuration wizard."""
    print_header("Configuration Wizard")

    print(f"{Colors.OKCYAN}This wizard will help you configure Gerald Desktop Manager.{Colors.ENDC}\n")

    # Ask for language preference
    print_info("Language Configuration:")
    print("1. English")
    print("2. Russian (Русский)")
    print("3. Bilingual (Both)")

    lang_choice = input(f"\n{Colors.OKCYAN}Select language (1-3): {Colors.ENDC}")

    lang_map = {
        '1': 'en',
        '2': 'ru',
        '3': 'both'
    }

    language = lang_map.get(lang_choice, 'en')

    # Create config file
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)

    config_content = f"""# Gerald Desktop Manager Configuration

language: {language}
voice_activation: true
hotword: "Gerald"

# Character settings
default_character: "Gerald"

# Service ports
asr_service_port: 8000
llm_service_port: 8001
command_service_port: 8002
"""

    with open(config_dir / 'gerald_config.yaml', 'w') as f:
        f.write(config_content)

    print_success("Configuration saved")

    return True


def install_windows_service():
    """Install as Windows service (optional)."""
    print_info("Windows Service Installation (Optional)...")

    response = input(f"\n{Colors.OKCYAN}Install as Windows service? (requires admin) (y/n): {Colors.ENDC}").lower()

    if response != 'y':
        return True

    print_warning("Windows service installation requires administrator privileges")
    print_info("You can install the service later by running windows_service.py install")

    return True


def main():
    """Main installation routine."""
    print_header("Gerald Desktop Manager - Installation")

    print(f"{Colors.OKCYAN}Welcome to Gerald Desktop Manager installation!{Colors.ENDC}")
    print(f"{Colors.OKCYAN}This will install a voice-controlled virtual desktop manager.{Colors.ENDC}\n")

    # Check requirements
    if not check_python_version():
        sys.exit(1)

    is_windows = check_platform()

    # Install dependencies
    response = input(f"\n{Colors.OKCYAN}Install Python dependencies? (y/n): {Colors.ENDC}").lower()
    if response == 'y':
        if not install_dependencies():
            print_error("Dependency installation failed")
            sys.exit(1)

    # Create directories
    if not create_directories():
        print_error("Failed to create directories")
        sys.exit(1)

    # Configuration wizard
    if not create_config_wizard():
        print_error("Configuration failed")
        sys.exit(1)

    # Windows-specific setup
    if is_windows:
        # Create shortcuts
        if not create_shortcuts():
            print_warning("Shortcut creation failed, but installation can continue")

        # Configure startup
        if not configure_startup():
            print_warning("Startup configuration failed, but installation can continue")

        # Windows service (optional)
        install_windows_service()

    # Installation complete
    print_header("Installation Complete!")

    print(f"{Colors.OKGREEN}Gerald Desktop Manager has been installed successfully!{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}Next steps:{Colors.ENDC}")
    print(f"  1. Configure your API keys in config/gerald_config.yaml")
    print(f"  2. Run: python launch_gerald.py")
    print(f"  3. Say: 'Gerald, what can you do?'")

    print(f"\n{Colors.OKCYAN}For uninstallation, run: python uninstall.py{Colors.ENDC}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Installation cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Installation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

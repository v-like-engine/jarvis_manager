#!/usr/bin/env python3
"""
Gerald Desktop Manager - Simple Launcher
=========================================

A user-friendly launcher for Gerald Desktop Manager with GUI.
This script provides an easy way to start Gerald with various options.

Usage:
    python start_gerald.py              # Start with default settings
    python start_gerald.py --character winnie_pooh  # Start with different character
    python start_gerald.py --lang ru    # Start with Russian language
    python start_gerald.py --help       # Show help
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path


def print_banner():
    """Print Gerald welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🎙️  GERALD DESKTOP MANAGER 🖥️                     ║
    ║                                                           ║
    ║        Voice-Controlled Desktop Manager                   ║
    ║        Windows 10/11 - Offline & Private                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_requirements():
    """Check if requirements are met"""
    print("🔍 Checking requirements...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("❌ Python 3.10 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False

    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check if models exist
    models_dir = Path(__file__).parent / "shared" / "models"
    if not models_dir.exists():
        print("⚠️  Models directory not found!")
        print("   Please run: python setup_models.py")
        return False

    print("✅ Models directory found")

    # Check if services exist
    services_dir = Path(__file__).parent / "services"
    required_services = ["asr_service", "llm_service", "command_service"]

    for service in required_services:
        service_path = services_dir / service
        if not service_path.exists():
            print(f"❌ Service not found: {service}")
            return False

    print(f"✅ All services found ({len(required_services)} services)")

    return True


def check_dependencies():
    """Check if Python dependencies are installed"""
    print("\n🔍 Checking dependencies...")

    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "loguru",
        "PyYAML"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_").lower())
        except ImportError:
            missing.append(package)

    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("\n   To install dependencies, run:")
        print("   pip install -r services/asr_service/requirements.txt")
        print("   pip install -r services/llm_service/requirements.txt")
        print("   pip install -r services/command_service/requirements.txt")
        return False

    print(f"✅ All required packages installed")
    return True


def start_gerald(character="gerald", language="en", debug=False):
    """
    Start Gerald Desktop Manager

    Args:
        character: Character to use (gerald, winnie_pooh, etc.)
        language: Default language (en or ru)
        debug: Enable debug mode
    """
    print("\n🚀 Starting Gerald Desktop Manager...")
    print(f"   Character: {character}")
    print(f"   Language: {language}")
    print(f"   Debug: {debug}")

    # Path to main launcher
    main_launcher = Path(__file__).parent / "run_gerald.py"

    if not main_launcher.exists():
        print(f"❌ Main launcher not found: {main_launcher}")
        return False

    # Build command
    cmd = [sys.executable, str(main_launcher)]

    if character != "gerald":
        cmd.extend(["--character", character])

    if language != "en":
        cmd.extend(["--language", language])

    if debug:
        cmd.append("--debug")

    try:
        print("\n" + "="*60)
        print("Starting services... Please wait...")
        print("="*60 + "\n")

        # Start the main launcher
        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n\n⚠️  Gerald shutdown requested by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting Gerald: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

    return True


def show_quick_help():
    """Show quick help for voice commands"""
    help_text = """
    🎤 QUICK START - VOICE COMMANDS
    ═══════════════════════════════════════════════════════════

    📱 APPLICATION CONTROL:
        "Open Chrome"           - Launch Chrome browser
        "Open Notepad"          - Launch Notepad
        "Close Chrome"          - Close Chrome browser

    📂 FILE OPERATIONS:
        "Create folder test"    - Create a new folder
        "Delete file test.txt"  - Delete a file (with confirmation)

    🎵 MUSIC CONTROL:
        "Play music"            - Play/resume playback
        "Pause"                 - Pause playback
        "Next track"            - Skip to next track
        "Volume up"             - Increase volume

    ⚙️ SYSTEM COMMANDS:
        "Who are you?"          - Gerald introduces himself
        "Change language"       - Switch between English/Russian
        "Exit Gerald"           - Shutdown Gerald

    🇷🇺 RUSSIAN COMMANDS:
        "Открой Хром"           - Запустить Chrome
        "Закрой Хром"           - Закрыть Chrome
        "Кто ты?"              - Информация о Gerald
        "Выключись"            - Выключить Gerald

    ═══════════════════════════════════════════════════════════

    For full command list, see: docs/COMMANDS.md

    Press Ctrl+C to stop Gerald
    """
    print(help_text)


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="Gerald Desktop Manager - Simple Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--character",
        "-c",
        default="gerald",
        choices=["gerald", "winnie_pooh"],
        help="Character to use (default: gerald)"
    )

    parser.add_argument(
        "--language",
        "--lang",
        "-l",
        default="en",
        choices=["en", "ru"],
        help="Default language (default: en)"
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "--no-check",
        action="store_true",
        help="Skip requirements check"
    )

    parser.add_argument(
        "--help-commands",
        action="store_true",
        help="Show quick command reference"
    )

    args = parser.parse_args()

    # Show banner
    print_banner()

    # Show quick help if requested
    if args.help_commands:
        show_quick_help()
        return 0

    # Check requirements
    if not args.no_check:
        if not check_requirements():
            print("\n❌ Requirements check failed!")
            print("   Please fix the issues above and try again.")
            return 1

        if not check_dependencies():
            print("\n❌ Dependencies check failed!")
            print("   Please install required packages and try again.")
            return 1

    print("\n✅ All checks passed!\n")
    time.sleep(1)

    # Show quick help
    show_quick_help()

    # Start Gerald
    success = start_gerald(
        character=args.character,
        language=args.language,
        debug=args.debug
    )

    if success:
        print("\n✅ Gerald shutdown complete")
        return 0
    else:
        print("\n❌ Gerald encountered an error")
        return 1


if __name__ == "__main__":
    sys.exit(main())

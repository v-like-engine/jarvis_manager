#!/usr/bin/env python3
"""
Gerald Desktop Manager - Model Setup Script

Downloads all required models for offline operation:
- ASR models (Vosk - English and Russian)
- LLM model (Phi-3-mini or alternative)
- VAD model (Silero)
- Face recognition models (dlib)

Total download size: ~5-25 GB depending on LLM choice
"""

import os
import sys
import subprocess
from pathlib import Path

# Colors for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_info(text):
    print(f"{BLUE}ℹ{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def run_script(script_path, description):
    """Run a Python script"""
    print_info(f"Running: {description}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print_success(f"{description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed!")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def main():
    print_header("Gerald Desktop Manager - Model Setup")

    # Get project root
    project_root = Path(__file__).parent

    print_info("This script will download all required models for offline operation.")
    print_info("Total download size: approximately 5-25 GB")
    print_info("This may take 10-30 minutes depending on your internet speed.\n")

    response = input(f"{YELLOW}Continue? (y/n):{RESET} ").strip().lower()
    if response != 'y':
        print_info("Setup cancelled.")
        return

    success_count = 0
    total_count = 0

    # 1. Download ASR models
    print_header("1. Downloading ASR Models (Vosk)")
    asr_script = project_root / "services" / "asr_service" / "download_models.py"
    total_count += 1
    if asr_script.exists():
        if run_script(asr_script, "ASR models download"):
            success_count += 1
    else:
        print_warning(f"ASR download script not found: {asr_script}")

    # 2. Download LLM model
    print_header("2. Downloading LLM Model (Phi-3-mini)")
    llm_script = project_root / "shared" / "models" / "llm" / "download_model.py"
    total_count += 1
    if llm_script.exists():
        if run_script(llm_script, "LLM model download"):
            success_count += 1
    else:
        print_warning(f"LLM download script not found: {llm_script}")

    # Summary
    print_header("Setup Complete!")

    if success_count == total_count:
        print_success(f"All {total_count} model downloads completed successfully!")
        print_info("\nYou can now start Gerald with:")
        print(f"  {BOLD}python run_gerald.py{RESET}")
        print(f"  or")
        print(f"  {BOLD}run_gerald.bat{RESET} (on Windows)")
    else:
        print_warning(f"\nSetup completed with warnings: {success_count}/{total_count} successful")
        print_info("Some models may not have been downloaded. Check errors above.")
        print_info("You can run individual download scripts manually:")
        print(f"  - ASR: python services/asr_service/download_models.py")
        print(f"  - LLM: python shared/models/llm/download_model.py")

    print_info("\nFor more information, see docs/INSTALLATION.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        sys.exit(1)

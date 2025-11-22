#!/usr/bin/env python3
"""
Gerald Desktop Manager - Main Launcher

Starts all microservices and coordinates the Gerald voice assistant:
- ASR Service (port 8001): Speech recognition, TTS, face/voice recognition
- LLM Service (port 8002): Natural language generation with Gerald's personality
- Command Service (port 8003): System command execution

Usage:
    python run_gerald.py [--dev] [--no-asr] [--no-llm] [--no-commands]

Options:
    --dev              Run in development mode (verbose logging)
    --no-asr          Skip ASR service startup
    --no-llm          Skip LLM service startup
    --no-commands     Skip Command service startup
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from pathlib import Path
import yaml
import requests

# Colors for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

class GeraldLauncher:
    def __init__(self, dev_mode=False):
        self.dev_mode = dev_mode
        self.project_root = Path(__file__).parent
        self.config = self._load_config()
        self.processes = {}

    def _load_config(self):
        """Load main configuration"""
        config_path = self.project_root / "config" / "main_config.yaml"
        if not config_path.exists():
            self.print_error(f"Configuration file not found: {config_path}")
            sys.exit(1)

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def print_header(self, text):
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}{text:^60}{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

    def print_success(self, text):
        print(f"{GREEN}✓{RESET} {text}")

    def print_info(self, text):
        print(f"{BLUE}ℹ{RESET} {text}")

    def print_warning(self, text):
        print(f"{YELLOW}⚠{RESET} {text}")

    def print_error(self, text):
        print(f"{RED}✗{RESET} {text}")

    def check_models_downloaded(self):
        """Check if models are downloaded"""
        self.print_info("Checking for required models...")

        models_dir = self.project_root / "shared" / "models"
        issues = []

        # Check ASR models
        asr_dir = models_dir / "asr"
        if not asr_dir.exists() or not any(asr_dir.glob("vosk-model-*")):
            issues.append("ASR models not found")

        # Check LLM models
        llm_dir = models_dir / "llm"
        if not llm_dir.exists() or not any(llm_dir.glob("*.gguf")):
            issues.append("LLM model not found")

        if issues:
            self.print_warning("Missing models detected:")
            for issue in issues:
                print(f"  - {issue}")
            print()
            self.print_info("Run the following command to download models:")
            print(f"  {BOLD}python setup_models.py{RESET}\n")

            response = input(f"{YELLOW}Continue anyway? (y/n):{RESET} ").strip().lower()
            if response != 'y':
                self.print_info("Startup cancelled.")
                sys.exit(0)
        else:
            self.print_success("All models found!")

    def start_service(self, name, service_dir, main_script, port):
        """Start a microservice"""
        self.print_info(f"Starting {name}...")

        script_path = self.project_root / service_dir / main_script
        if not script_path.exists():
            self.print_error(f"Service script not found: {script_path}")
            return False

        try:
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'

            if self.dev_mode:
                env['LOG_LEVEL'] = 'DEBUG'

            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                env=env,
                stdout=subprocess.PIPE if not self.dev_mode else None,
                stderr=subprocess.PIPE if not self.dev_mode else None,
                cwd=str(script_path.parent)
            )

            self.processes[name] = process

            # Wait a bit for service to start
            time.sleep(2)

            # Check if service is responding
            if self._check_service_health(port, timeout=10):
                self.print_success(f"{name} started on port {port}")
                return True
            else:
                self.print_warning(f"{name} started but not responding yet")
                return True

        except Exception as e:
            self.print_error(f"Failed to start {name}: {e}")
            return False

    def _check_service_health(self, port, timeout=5):
        """Check if service is responding"""
        url = f"http://localhost:{port}/status"
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    return True
            except:
                time.sleep(0.5)

        return False

    def stop_all_services(self):
        """Stop all running services"""
        self.print_info("\nShutting down services...")

        for name, process in self.processes.items():
            try:
                self.print_info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                self.print_success(f"{name} stopped")
            except subprocess.TimeoutExpired:
                self.print_warning(f"{name} did not stop gracefully, forcing...")
                process.kill()
            except Exception as e:
                self.print_error(f"Error stopping {name}: {e}")

        self.print_success("All services stopped")

    def run(self, skip_services=None):
        """Main run loop"""
        skip_services = skip_services or set()

        self.print_header("Gerald Desktop Manager")

        # ASCII art
        print(f"{BLUE}")
        print("    _____ ______ _____         _      _____  ")
        print("   / ____|  ____|  __ \\       / \\    |  __ \\ ")
        print("  | |  __| |__  | |__) |     / _ \\   | |  | |")
        print("  | | |_ |  __| |  _  /     / ___ \\  | |  | |")
        print("  | |__| | |____| | \\ \\    / /   \\ \\ | |__| |")
        print("   \\_____|______|_|  \\_\\  /_/     \\_\\|_____/ ")
        print(f"{RESET}")
        print(f"{BOLD}  Your Loyal Knight of the Computer{RESET}\n")

        # Check models
        self.check_models_downloaded()

        # Start services
        print()
        self.print_header("Starting Services")

        services = []

        if 'asr' not in skip_services and self.config['services']['asr']['enabled']:
            services.append(('ASR Service', 'services/asr_service', 'src/main.py', 8001))

        if 'llm' not in skip_services and self.config['services']['llm']['enabled']:
            services.append(('LLM Service', 'services/llm_service', 'src/main.py', 8002))

        if 'command' not in skip_services and self.config['services']['command']['enabled']:
            services.append(('Command Service', 'services/command_service', 'src/main.py', 8003))

        success = True
        for name, service_dir, main_script, port in services:
            if not self.start_service(name, service_dir, main_script, port):
                success = False

        if not success:
            self.print_warning("\nSome services failed to start. Check logs for details.")

        # Ready message
        print()
        self.print_header("Gerald is Ready!")

        print(f"{GREEN}Gerald is now listening and ready to serve!{RESET}\n")
        print("Voice Commands:")
        print(f"  • {BOLD}English:{RESET} \"Open Yandex Browser\" / \"Who are you?\" / \"Exit Gerald\"")
        print(f"  • {BOLD}Russian:{RESET} \"Открой Яндекс браузер\" / \"Кто ты?\" / \"Выключись\"\n")

        print("Service Endpoints:")
        if 'asr' not in skip_services:
            print(f"  • ASR Service: http://localhost:8001/docs")
        if 'llm' not in skip_services:
            print(f"  • LLM Service: http://localhost:8002/docs")
        if 'command' not in skip_services:
            print(f"  • Command Service: http://localhost:8003/docs")

        print(f"\n{YELLOW}Press Ctrl+C to stop Gerald{RESET}\n")

        # Keep running
        try:
            while True:
                time.sleep(1)

                # Check if any process died
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        self.print_error(f"{name} has stopped unexpectedly!")
                        del self.processes[name]

        except KeyboardInterrupt:
            print("\n")
            self.print_info("Shutdown signal received")
        finally:
            self.stop_all_services()

        self.print_success("\nGerald has shut down. Stay safe!")

def main():
    parser = argparse.ArgumentParser(description='Gerald Desktop Manager Launcher')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    parser.add_argument('--no-asr', action='store_true', help='Skip ASR service')
    parser.add_argument('--no-llm', action='store_true', help='Skip LLM service')
    parser.add_argument('--no-commands', action='store_true', help='Skip Command service')

    args = parser.parse_args()

    skip_services = set()
    if args.no_asr:
        skip_services.add('asr')
    if args.no_llm:
        skip_services.add('llm')
    if args.no_commands:
        skip_services.add('command')

    launcher = GeraldLauncher(dev_mode=args.dev)
    launcher.run(skip_services=skip_services)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{RED}✗{RESET} Fatal error: {e}")
        sys.exit(1)

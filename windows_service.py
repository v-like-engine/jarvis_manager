#!/usr/bin/env python3
"""
Gerald Desktop Manager - Windows Service Wrapper

This module allows Gerald to run as a Windows service.

Installation:
    python windows_service.py install

Start service:
    python windows_service.py start

Stop service:
    python windows_service.py stop

Uninstall service:
    python windows_service.py remove
"""

import sys
import os
import time
import subprocess
import logging
from pathlib import Path

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    print("ERROR: pywin32 is required for Windows service functionality")
    print("Install it with: pip install pywin32")


class GeraldService(win32serviceutil.ServiceFramework):
    """
    Windows Service wrapper for Gerald Desktop Manager.
    """

    _svc_name_ = "GeraldDesktopManager"
    _svc_display_name_ = "Gerald Desktop Manager"
    _svc_description_ = "Voice-controlled virtual desktop manager with AI assistant"

    def __init__(self, args):
        """Initialize the service."""
        win32serviceutil.ServiceFramework.__init__(self, args)

        # Create a stop event
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

        # Service processes
        self.processes = []

        # Setup logging
        self.log_file = Path(__file__).parent / "logs" / "service.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=str(self.log_file),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger('GeraldService')

    def SvcStop(self):
        """
        Called when the service is being stopped.
        """
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # Signal the stop event
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        """
        Called when the service is started.
        """
        self.logger.info("Service starting...")

        # Log service start
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        # Run the service
        self.main()

    def main(self):
        """
        Main service loop.
        """
        try:
            self.logger.info("Starting Gerald Desktop Manager services...")

            # Get installation directory
            install_dir = Path(__file__).parent.absolute()

            # Services to start
            services = [
                {
                    'name': 'ASR Service',
                    'script': install_dir / 'services' / 'asr_service' / 'src' / 'main.py',
                    'port': 8000
                },
                {
                    'name': 'LLM Service',
                    'script': install_dir / 'services' / 'llm_service' / 'src' / 'main.py',
                    'port': 8001
                },
                {
                    'name': 'Command Service',
                    'script': install_dir / 'services' / 'command_service' / 'src' / 'main.py',
                    'port': 8002
                },
            ]

            # Start each service
            for service_info in services:
                script_path = service_info['script']

                if not script_path.exists():
                    self.logger.error(f"Service script not found: {script_path}")
                    continue

                try:
                    self.logger.info(f"Starting {service_info['name']}...")

                    # Start the service process
                    process = subprocess.Popen(
                        [sys.executable, str(script_path)],
                        cwd=str(install_dir),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    self.processes.append({
                        'name': service_info['name'],
                        'process': process,
                        'script': script_path
                    })

                    self.logger.info(f"{service_info['name']} started (PID: {process.pid})")

                except Exception as e:
                    self.logger.error(f"Failed to start {service_info['name']}: {e}")

            # Wait for stop signal
            self.logger.info("All services started, waiting for stop signal...")

            # Service main loop
            while True:
                # Wait for stop event (check every 5 seconds)
                rc = win32event.WaitForSingleObject(self.stop_event, 5000)

                if rc == win32event.WAIT_OBJECT_0:
                    # Stop signal received
                    self.logger.info("Stop signal received, shutting down...")
                    break

                # Check if any processes have died
                for proc_info in self.processes:
                    process = proc_info['process']
                    if process.poll() is not None:
                        # Process has died
                        self.logger.warning(
                            f"{proc_info['name']} has stopped unexpectedly (exit code: {process.returncode})"
                        )

                        # Try to restart it
                        self.logger.info(f"Attempting to restart {proc_info['name']}...")

                        try:
                            new_process = subprocess.Popen(
                                [sys.executable, str(proc_info['script'])],
                                cwd=str(install_dir),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )

                            proc_info['process'] = new_process
                            self.logger.info(f"{proc_info['name']} restarted (PID: {new_process.pid})")

                        except Exception as e:
                            self.logger.error(f"Failed to restart {proc_info['name']}: {e}")

            # Shutdown
            self.shutdown()

        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)

            # Log error to Windows Event Log
            servicemanager.LogErrorMsg(f"Gerald Service error: {e}")

    def shutdown(self):
        """
        Shutdown all service processes.
        """
        self.logger.info("Shutting down all services...")

        for proc_info in self.processes:
            try:
                process = proc_info['process']
                name = proc_info['name']

                if process.poll() is None:
                    # Process is still running
                    self.logger.info(f"Stopping {name}...")

                    # Terminate the process
                    process.terminate()

                    # Wait for process to exit (max 10 seconds)
                    try:
                        process.wait(timeout=10)
                        self.logger.info(f"{name} stopped")
                    except subprocess.TimeoutExpired:
                        # Force kill
                        self.logger.warning(f"{name} did not stop gracefully, force killing...")
                        process.kill()
                        process.wait()
                        self.logger.info(f"{name} force killed")

            except Exception as e:
                self.logger.error(f"Error stopping {proc_info['name']}: {e}")

        self.logger.info("All services stopped")

        # Log service stop
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )


def main():
    """
    Main entry point for service management.
    """
    if not PYWIN32_AVAILABLE:
        print("\nERROR: pywin32 is not installed")
        print("Install it with: pip install pywin32")
        print("\nAfter installation, run: python -m win32com.client.makepy")
        sys.exit(1)

    if len(sys.argv) == 1:
        # No arguments - print usage
        print("\nGerald Desktop Manager - Windows Service")
        print("\nUsage:")
        print("  python windows_service.py install    - Install service")
        print("  python windows_service.py start      - Start service")
        print("  python windows_service.py stop       - Stop service")
        print("  python windows_service.py restart    - Restart service")
        print("  python windows_service.py remove     - Uninstall service")
        print("  python windows_service.py debug      - Run in debug mode")
        print("\nNote: Install, remove, start, and stop require administrator privileges")
        sys.exit(0)

    try:
        # Handle service commands
        win32serviceutil.HandleCommandLine(GeraldService)

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you are running as administrator for install/remove/start/stop commands")
        sys.exit(1)


if __name__ == '__main__':
    main()

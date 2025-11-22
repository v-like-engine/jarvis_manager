"""Launch Windows applications."""

import subprocess
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import time

logger = logging.getLogger(__name__)


class AppLauncher:
    """Launch Windows applications."""

    @staticmethod
    def launch(
        exe_path: str,
        args: Optional[list] = None,
        working_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Launch an application.

        Args:
            exe_path: Path to executable
            args: Command-line arguments (optional)
            working_dir: Working directory (optional)

        Returns:
            Result dictionary with success status and details
        """
        try:
            # Validate executable exists
            if not os.path.exists(exe_path):
                return {
                    'success': False,
                    'error': f"Executable not found: {exe_path}"
                }

            # Build command
            cmd = [exe_path]
            if args:
                cmd.extend(args)

            logger.info(f"Launching: {' '.join(cmd)}")

            # Launch process
            if sys.platform == 'win32':
                # Use shell=False for better security, but set CREATE_NEW_CONSOLE
                # to launch in separate window
                process = subprocess.Popen(
                    cmd,
                    cwd=working_dir,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
                )
            else:
                # Non-Windows fallback
                process = subprocess.Popen(
                    cmd,
                    cwd=working_dir,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            # Wait a bit to see if process starts successfully
            time.sleep(0.5)

            # Check if process is still running
            if process.poll() is not None:
                # Process terminated immediately
                stdout, stderr = process.communicate()
                return {
                    'success': False,
                    'error': f"Process terminated immediately. Exit code: {process.returncode}",
                    'stderr': stderr.decode('utf-8', errors='ignore') if stderr else None
                }

            return {
                'success': True,
                'pid': process.pid,
                'exe_path': exe_path,
                'message': f"Application launched successfully (PID: {process.pid})"
            }

        except FileNotFoundError:
            logger.error(f"Executable not found: {exe_path}")
            return {
                'success': False,
                'error': f"Executable not found: {exe_path}"
            }

        except PermissionError:
            logger.error(f"Permission denied: {exe_path}")
            return {
                'success': False,
                'error': f"Permission denied: {exe_path}"
            }

        except Exception as e:
            logger.error(f"Failed to launch {exe_path}: {e}")
            return {
                'success': False,
                'error': f"Failed to launch application: {str(e)}"
            }

    @staticmethod
    def launch_with_protocol(protocol_url: str) -> Dict[str, Any]:
        """
        Launch an application using a protocol URL (e.g., http://, mailto:, etc.).

        Args:
            protocol_url: Protocol URL

        Returns:
            Result dictionary
        """
        try:
            if sys.platform == 'win32':
                os.startfile(protocol_url)
            else:
                # Fallback for non-Windows
                subprocess.Popen(['xdg-open', protocol_url])

            return {
                'success': True,
                'message': f"Opened protocol: {protocol_url}"
            }

        except Exception as e:
            logger.error(f"Failed to open protocol {protocol_url}: {e}")
            return {
                'success': False,
                'error': f"Failed to open protocol: {str(e)}"
            }

    @staticmethod
    def launch_file(file_path: str) -> Dict[str, Any]:
        """
        Open a file with its default application.

        Args:
            file_path: Path to file

        Returns:
            Result dictionary
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f"File not found: {file_path}"
                }

            if sys.platform == 'win32':
                os.startfile(file_path)
            else:
                # Fallback for non-Windows
                subprocess.Popen(['xdg-open', file_path])

            return {
                'success': True,
                'message': f"Opened file: {file_path}"
            }

        except Exception as e:
            logger.error(f"Failed to open file {file_path}: {e}")
            return {
                'success': False,
                'error': f"Failed to open file: {str(e)}"
            }

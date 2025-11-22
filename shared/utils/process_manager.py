"""Process management utilities for Windows."""

import psutil
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manage Windows processes."""

    @staticmethod
    def get_running_processes() -> List[Dict[str, Any]]:
        """
        Get list of all running processes.

        Returns:
            List of process information dictionaries
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    @staticmethod
    def find_process_by_name(name: str) -> List[psutil.Process]:
        """
        Find processes by name (case-insensitive partial match).

        Args:
            name: Process name to search for

        Returns:
            List of matching processes
        """
        name_lower = name.lower()
        matching = []

        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if name_lower in proc.info['name'].lower():
                    matching.append(proc)
                elif proc.info['exe'] and name_lower in proc.info['exe'].lower():
                    matching.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return matching

    @staticmethod
    def terminate_process(process: psutil.Process, timeout: int = 5) -> bool:
        """
        Terminate a process gracefully, with force if needed.

        Args:
            process: Process to terminate
            timeout: Timeout in seconds

        Returns:
            True if terminated successfully
        """
        try:
            process.terminate()
            process.wait(timeout=timeout)
            return True
        except psutil.TimeoutExpired:
            logger.warning(f"Process {process.pid} didn't terminate, killing...")
            try:
                process.kill()
                process.wait(timeout=2)
                return True
            except Exception as e:
                logger.error(f"Failed to kill process {process.pid}: {e}")
                return False
        except Exception as e:
            logger.error(f"Failed to terminate process {process.pid}: {e}")
            return False

    @staticmethod
    def terminate_by_name(name: str) -> int:
        """
        Terminate all processes matching the name.

        Args:
            name: Process name to terminate

        Returns:
            Number of processes terminated
        """
        processes = ProcessManager.find_process_by_name(name)
        count = 0

        for proc in processes:
            if ProcessManager.terminate_process(proc):
                count += 1

        return count

    @staticmethod
    def is_process_running(name: str) -> bool:
        """
        Check if a process with the given name is running.

        Args:
            name: Process name

        Returns:
            True if process is running
        """
        return len(ProcessManager.find_process_by_name(name)) > 0

    @staticmethod
    def launch_process(
        executable: Path,
        args: Optional[List[str]] = None,
        working_dir: Optional[Path] = None
    ) -> subprocess.Popen:
        """
        Launch a new process.

        Args:
            executable: Path to executable
            args: Command-line arguments
            working_dir: Working directory

        Returns:
            Popen object
        """
        cmd = [str(executable)]
        if args:
            cmd.extend(args)

        return subprocess.Popen(
            cmd,
            cwd=str(working_dir) if working_dir else None,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    @staticmethod
    def get_process_info(pid: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a process.

        Args:
            pid: Process ID

        Returns:
            Process information dictionary or None if not found
        """
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'exe': proc.exe(),
                'cmdline': proc.cmdline(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_mb': proc.memory_info().rss / (1024 * 1024),
                'create_time': proc.create_time(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to get info for PID {pid}: {e}")
            return None

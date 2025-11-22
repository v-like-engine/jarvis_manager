"""Close running Windows applications."""

import logging
import sys
from typing import Dict, Any, List
import psutil

if sys.platform == 'win32':
    try:
        import win32gui
        import win32con
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
        logging.warning("Windows modules not available")
else:
    WINDOWS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AppCloser:
    """Close running Windows applications."""

    @staticmethod
    def close_by_name(
        app_name: str,
        force: bool = False,
        timeout: int = 5
    ) -> Dict[str, Any]:
        """
        Close application(s) by name.

        Args:
            app_name: Application name or process name
            force: Force kill if graceful close fails
            timeout: Timeout in seconds for graceful close

        Returns:
            Result dictionary
        """
        try:
            # Find matching processes
            matching_procs = []
            app_name_lower = app_name.lower()

            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info.get('exe', '').lower() if proc.info.get('exe') else ''

                    if (app_name_lower in proc_name or
                        app_name_lower in proc_exe):
                        matching_procs.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not matching_procs:
                return {
                    'success': False,
                    'error': f"No running application found matching: {app_name}"
                }

            # Close each matching process
            closed_count = 0
            failed = []

            for proc in matching_procs:
                try:
                    proc_name = proc.name()
                    pid = proc.pid

                    logger.info(f"Closing {proc_name} (PID: {pid})")

                    # Try graceful termination first
                    proc.terminate()

                    try:
                        proc.wait(timeout=timeout)
                        closed_count += 1
                        logger.info(f"Successfully closed {proc_name} (PID: {pid})")
                    except psutil.TimeoutExpired:
                        if force:
                            # Force kill if graceful close failed
                            logger.warning(f"Force killing {proc_name} (PID: {pid})")
                            proc.kill()
                            proc.wait(timeout=2)
                            closed_count += 1
                        else:
                            failed.append(f"{proc_name} (PID: {pid})")

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.error(f"Failed to close process {proc.pid}: {e}")
                    failed.append(f"{proc.name()} (PID: {proc.pid})")

            # Build result
            if closed_count > 0:
                message = f"Closed {closed_count} process(es)"
                if failed:
                    message += f", failed to close {len(failed)} process(es)"

                return {
                    'success': True,
                    'closed_count': closed_count,
                    'failed': failed if failed else None,
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to close any processes. Failed: {', '.join(failed)}"
                }

        except Exception as e:
            logger.error(f"Error closing app {app_name}: {e}")
            return {
                'success': False,
                'error': f"Failed to close application: {str(e)}"
            }

    @staticmethod
    def close_by_window_title(
        window_title: str,
        partial_match: bool = True
    ) -> Dict[str, Any]:
        """
        Close application by window title.

        Args:
            window_title: Window title to search for
            partial_match: Allow partial title matches

        Returns:
            Result dictionary
        """
        if not WINDOWS_AVAILABLE:
            return {
                'success': False,
                'error': "Windows API not available"
            }

        try:
            title_lower = window_title.lower()
            found_windows = []

            def enum_callback(hwnd, _):
                """Callback for enumerating windows."""
                if win32gui.IsWindowVisible(hwnd):
                    text = win32gui.GetWindowText(hwnd)
                    if text:
                        if partial_match:
                            if title_lower in text.lower():
                                found_windows.append((hwnd, text))
                        else:
                            if title_lower == text.lower():
                                found_windows.append((hwnd, text))
                return True

            # Enumerate all windows
            win32gui.EnumWindows(enum_callback, None)

            if not found_windows:
                return {
                    'success': False,
                    'error': f"No window found with title: {window_title}"
                }

            # Close each found window
            closed_count = 0
            for hwnd, title in found_windows:
                try:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    closed_count += 1
                    logger.info(f"Closed window: {title}")
                except Exception as e:
                    logger.error(f"Failed to close window {title}: {e}")

            return {
                'success': True,
                'closed_count': closed_count,
                'message': f"Closed {closed_count} window(s)"
            }

        except Exception as e:
            logger.error(f"Error closing window by title: {e}")
            return {
                'success': False,
                'error': f"Failed to close window: {str(e)}"
            }

    @staticmethod
    def close_by_pid(pid: int, force: bool = False, timeout: int = 5) -> Dict[str, Any]:
        """
        Close application by process ID.

        Args:
            pid: Process ID
            force: Force kill if graceful close fails
            timeout: Timeout in seconds for graceful close

        Returns:
            Result dictionary
        """
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()

            logger.info(f"Closing {proc_name} (PID: {pid})")

            # Try graceful termination
            proc.terminate()

            try:
                proc.wait(timeout=timeout)
                return {
                    'success': True,
                    'message': f"Successfully closed {proc_name} (PID: {pid})"
                }
            except psutil.TimeoutExpired:
                if force:
                    # Force kill
                    logger.warning(f"Force killing {proc_name} (PID: {pid})")
                    proc.kill()
                    proc.wait(timeout=2)
                    return {
                        'success': True,
                        'message': f"Force killed {proc_name} (PID: {pid})"
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Process {proc_name} (PID: {pid}) didn't terminate within timeout"
                    }

        except psutil.NoSuchProcess:
            return {
                'success': False,
                'error': f"No process found with PID: {pid}"
            }
        except psutil.AccessDenied:
            return {
                'success': False,
                'error': f"Access denied to close process with PID: {pid}"
            }
        except Exception as e:
            logger.error(f"Error closing process {pid}: {e}")
            return {
                'success': False,
                'error': f"Failed to close process: {str(e)}"
            }

    @staticmethod
    def get_running_apps() -> List[Dict[str, Any]]:
        """
        Get list of all running applications (with visible windows).

        Returns:
            List of running app info
        """
        apps = []

        try:
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                try:
                    # Filter out system processes and background services
                    if proc.info['exe']:
                        apps.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'exe': proc.info['exe'],
                            'create_time': proc.info['create_time'],
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            logger.error(f"Error getting running apps: {e}")

        return apps

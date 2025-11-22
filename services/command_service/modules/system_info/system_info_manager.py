"""System information manager for querying system details."""

import platform
import socket
import psutil
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemInfoManager:
    """
    Manage system information queries.

    Provides information about:
    - Computer name
    - CPU usage
    - Memory (RAM) usage
    - Disk space
    - Operating system
    - Network information
    """

    def __init__(self):
        """Initialize system info manager."""
        logger.info("SystemInfoManager initialized")

    def get_computer_name(self) -> Dict[str, Any]:
        """
        Get computer name.

        Returns:
            Dictionary with computer name
        """
        try:
            computer_name = socket.gethostname()

            return {
                'success': True,
                'computer_name': computer_name,
                'message': f"Computer name is: {computer_name}"
            }

        except Exception as e:
            logger.error(f"Error getting computer name: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get memory (RAM) information.

        Returns:
            Dictionary with memory details
        """
        try:
            mem = psutil.virtual_memory()

            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            used_gb = mem.used / (1024 ** 3)
            percent = mem.percent

            return {
                'success': True,
                'total_gb': round(total_gb, 2),
                'available_gb': round(available_gb, 2),
                'used_gb': round(used_gb, 2),
                'percent_used': percent,
                'message': f"RAM: {used_gb:.1f}GB / {total_gb:.1f}GB used ({percent}%)"
            }

        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_cpu_usage(self, interval: float = 1.0) -> Dict[str, Any]:
        """
        Get CPU usage information.

        Args:
            interval: Measurement interval in seconds

        Returns:
            Dictionary with CPU usage
        """
        try:
            # Get CPU usage over interval
            cpu_percent = psutil.cpu_percent(interval=interval)
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()

            result = {
                'success': True,
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_count_physical': cpu_count_physical,
                'message': f"CPU usage: {cpu_percent}%"
            }

            if cpu_freq:
                result['cpu_freq_mhz'] = cpu_freq.current
                result['cpu_freq_max_mhz'] = cpu_freq.max

            return result

        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_disk_space(self, path: str = 'C:\\') -> Dict[str, Any]:
        """
        Get disk space information.

        Args:
            path: Path to check (default: C:\)

        Returns:
            Dictionary with disk space info
        """
        try:
            disk = psutil.disk_usage(path)

            total_gb = disk.total / (1024 ** 3)
            used_gb = disk.used / (1024 ** 3)
            free_gb = disk.free / (1024 ** 3)
            percent = disk.percent

            return {
                'success': True,
                'path': path,
                'total_gb': round(total_gb, 2),
                'used_gb': round(used_gb, 2),
                'free_gb': round(free_gb, 2),
                'percent_used': percent,
                'message': f"Disk {path}: {free_gb:.1f}GB free of {total_gb:.1f}GB ({percent}% used)"
            }

        except Exception as e:
            logger.error(f"Error getting disk space: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_os_info(self) -> Dict[str, Any]:
        """
        Get operating system information.

        Returns:
            Dictionary with OS details
        """
        try:
            os_name = platform.system()
            os_version = platform.version()
            os_release = platform.release()
            machine = platform.machine()
            processor = platform.processor()

            return {
                'success': True,
                'os_name': os_name,
                'os_version': os_version,
                'os_release': os_release,
                'machine': machine,
                'processor': processor,
                'message': f"OS: {os_name} {os_release}, {machine}"
            }

        except Exception as e:
            logger.error(f"Error getting OS info: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information.

        Returns:
            Dictionary with network details
        """
        try:
            hostname = socket.gethostname()

            # Try to get local IP
            try:
                # Create a socket to get the IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except:
                local_ip = "Unknown"

            # Get network stats
            net_io = psutil.net_io_counters()

            return {
                'success': True,
                'hostname': hostname,
                'local_ip': local_ip,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'message': f"Network: {hostname} ({local_ip})"
            }

        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_uptime(self) -> Dict[str, Any]:
        """
        Get system uptime.

        Returns:
            Dictionary with uptime information
        """
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time

            # Convert to human-readable format
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            uptime_str = f"{days}d {hours}h {minutes}m"

            return {
                'success': True,
                'uptime_seconds': int(uptime_seconds),
                'uptime_days': days,
                'uptime_hours': hours,
                'uptime_minutes': minutes,
                'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
                'message': f"Uptime: {uptime_str}"
            }

        except Exception as e:
            logger.error(f"Error getting uptime: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_all_info(self) -> Dict[str, Any]:
        """
        Get all system information.

        Returns:
            Dictionary with all system info
        """
        try:
            return {
                'success': True,
                'computer_name': self.get_computer_name(),
                'os': self.get_os_info(),
                'cpu': self.get_cpu_usage(),
                'memory': self.get_memory_info(),
                'disk': self.get_disk_space(),
                'network': self.get_network_info(),
                'uptime': self.get_uptime()
            }

        except Exception as e:
            logger.error(f"Error getting all info: {e}")
            return {
                'success': False,
                'error': str(e)
            }

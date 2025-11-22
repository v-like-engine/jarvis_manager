"""
Unit tests for SystemInfoManager
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

from system_info import SystemInfoManager


@pytest.fixture
def system_info_manager():
    """Create SystemInfoManager instance"""
    return SystemInfoManager()


def test_initialization(system_info_manager):
    """Test SystemInfoManager initialization"""
    assert system_info_manager is not None


def test_get_computer_name(system_info_manager):
    """Test getting computer name"""
    result = system_info_manager.get_computer_name()

    assert result is not None
    assert result['success'] is True
    assert 'computer_name' in result
    assert len(result['computer_name']) > 0
    assert 'message' in result


def test_get_memory_info(system_info_manager):
    """Test getting memory information"""
    result = system_info_manager.get_memory_info()

    assert result is not None
    assert result['success'] is True
    assert 'total_gb' in result
    assert 'available_gb' in result
    assert 'used_gb' in result
    assert 'percent_used' in result
    assert result['total_gb'] > 0
    assert result['percent_used'] >= 0
    assert result['percent_used'] <= 100


def test_get_cpu_usage(system_info_manager):
    """Test getting CPU usage"""
    result = system_info_manager.get_cpu_usage(interval=0.1)

    assert result is not None
    assert result['success'] is True
    assert 'cpu_percent' in result
    assert 'cpu_count' in result
    assert result['cpu_count'] > 0
    assert result['cpu_percent'] >= 0
    assert result['cpu_percent'] <= 100


def test_get_disk_space(system_info_manager):
    """Test getting disk space"""
    # Use root on Linux, C: on Windows
    import platform
    path = 'C:\\' if platform.system() == 'Windows' else '/'

    result = system_info_manager.get_disk_space(path)

    assert result is not None
    assert result['success'] is True
    assert 'total_gb' in result
    assert 'free_gb' in result
    assert 'used_gb' in result
    assert 'percent_used' in result
    assert result['total_gb'] > 0


def test_get_os_info(system_info_manager):
    """Test getting OS information"""
    result = system_info_manager.get_os_info()

    assert result is not None
    assert result['success'] is True
    assert 'os_name' in result
    assert 'os_version' in result
    assert 'os_release' in result
    assert 'machine' in result
    assert len(result['os_name']) > 0


def test_get_network_info(system_info_manager):
    """Test getting network information"""
    result = system_info_manager.get_network_info()

    assert result is not None
    assert result['success'] is True
    assert 'hostname' in result
    assert 'local_ip' in result
    assert len(result['hostname']) > 0


def test_get_uptime(system_info_manager):
    """Test getting system uptime"""
    result = system_info_manager.get_uptime()

    assert result is not None
    assert result['success'] is True
    assert 'uptime_seconds' in result
    assert 'uptime_days' in result
    assert 'uptime_hours' in result
    assert 'uptime_minutes' in result
    assert result['uptime_seconds'] > 0


def test_get_all_info(system_info_manager):
    """Test getting all system information"""
    result = system_info_manager.get_all_info()

    assert result is not None
    assert result['success'] is True
    assert 'computer_name' in result
    assert 'os' in result
    assert 'cpu' in result
    assert 'memory' in result
    assert 'disk' in result
    assert 'network' in result
    assert 'uptime' in result


def test_error_handling_invalid_disk_path(system_info_manager):
    """Test error handling for invalid disk path"""
    result = system_info_manager.get_disk_space('/invalid/path/that/does/not/exist')

    # Should either succeed with error or return error
    assert result is not None
    assert 'success' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Tests for safety checker."""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.command_service.src.safety_checker import SafetyChecker, SafetyLevel


class TestSafetyChecker:
    """Test safety checker functionality."""

    @pytest.fixture
    def checker(self):
        """Create safety checker instance."""
        return SafetyChecker()

    def test_safe_commands(self, checker):
        """Test that safe commands are recognized."""
        # App launch should be safe
        level, msg = checker.check_command_safety('app_launch', {'app_name': 'notepad'})
        assert level == SafetyLevel.SAFE

        # Directory listing should be safe
        level, msg = checker.check_command_safety('dir_list', {'dir_path': '.'})
        assert level == SafetyLevel.SAFE

        # Music control should be safe
        level, msg = checker.check_command_safety('music_play', {})
        assert level == SafetyLevel.SAFE

    def test_confirmation_required(self, checker):
        """Test that dangerous commands require confirmation."""
        # File deletion requires confirmation
        level, msg = checker.check_command_safety(
            'file_delete',
            {'file_path': 'C:\\Users\\test\\test.txt'}
        )
        assert level == SafetyLevel.NEEDS_CONFIRMATION
        assert 'test.txt' in msg

        # Terminal commands require confirmation
        level, msg = checker.check_command_safety(
            'terminal',
            {'terminal_command': 'some-unknown-command'}
        )
        assert level == SafetyLevel.NEEDS_CONFIRMATION

    def test_forbidden_commands(self, checker):
        """Test that forbidden commands are blocked."""
        # Deleting system files is forbidden
        level, msg = checker.check_command_safety(
            'file_delete',
            {'file_path': 'C:\\Windows\\System32\\important.dll'}
        )
        assert level == SafetyLevel.FORBIDDEN
        assert 'protected' in msg.lower()

        # Format command is forbidden
        level, msg = checker.check_command_safety(
            'terminal',
            {'terminal_command': 'format C:'}
        )
        assert level == SafetyLevel.FORBIDDEN

    def test_whitelisted_terminal_commands(self, checker):
        """Test that whitelisted terminal commands are safe."""
        # 'dir' is whitelisted
        level, msg = checker.check_command_safety(
            'terminal',
            {'terminal_command': 'dir'}
        )
        assert level == SafetyLevel.SAFE

        # 'echo' is whitelisted
        level, msg = checker.check_command_safety(
            'terminal',
            {'terminal_command': 'echo Hello'}
        )
        assert level == SafetyLevel.SAFE

    def test_protected_processes(self, checker):
        """Test that protected processes cannot be killed."""
        # explorer.exe is protected
        level, msg = checker.check_command_safety(
            'app_close',
            {'app_name': 'explorer.exe', 'process_name': 'explorer.exe'}
        )
        assert level == SafetyLevel.FORBIDDEN
        assert 'protected' in msg.lower()

    def test_is_safe_helper(self, checker):
        """Test is_safe helper method."""
        assert checker.is_safe('app_launch', {'app_name': 'notepad'})
        assert not checker.is_safe('file_delete', {'file_path': 'test.txt'})

    def test_is_forbidden_helper(self, checker):
        """Test is_forbidden helper method."""
        assert checker.is_forbidden('file_delete', {'file_path': 'C:\\Windows\\test.txt'})
        assert not checker.is_forbidden('app_launch', {'app_name': 'notepad'})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

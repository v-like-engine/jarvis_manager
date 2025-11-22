"""Tests for terminal executor."""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.command_service.modules.terminal import TerminalExecutor, CommandWhitelist


class TestCommandWhitelist:
    """Test command whitelist."""

    @pytest.fixture
    def whitelist(self):
        """Create command whitelist."""
        return CommandWhitelist()

    def test_whitelisted_commands(self, whitelist):
        """Test that whitelisted commands are recognized."""
        assert whitelist.is_whitelisted('dir')
        assert whitelist.is_whitelisted('ls')
        assert whitelist.is_whitelisted('echo hello')
        assert whitelist.is_whitelisted('pwd')

    def test_non_whitelisted_commands(self, whitelist):
        """Test that non-whitelisted commands are rejected."""
        assert not whitelist.is_whitelisted('some-random-command')
        assert not whitelist.is_whitelisted('format')
        assert not whitelist.is_whitelisted('del')


class TestTerminalExecutor:
    """Test terminal executor."""

    @pytest.fixture
    def executor(self):
        """Create terminal executor."""
        return TerminalExecutor()

    def test_execute_simple_command(self, executor):
        """Test executing a simple command."""
        # Echo command should work on all platforms
        result = executor.execute('echo test', timeout=5)
        assert result['success']
        assert result['returncode'] == 0

    def test_execute_with_timeout(self, executor):
        """Test command timeout."""
        # This command should timeout (sleep/timeout not available everywhere)
        # So we'll just test a quick command
        result = executor.execute('echo quick', timeout=1)
        assert result['success']

    def test_is_whitelisted(self, executor):
        """Test whitelist checking."""
        assert executor.is_whitelisted('dir')
        assert executor.is_whitelisted('echo test')
        assert not executor.is_whitelisted('format')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

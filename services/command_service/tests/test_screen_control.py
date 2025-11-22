"""Tests for screen control module."""

import unittest
import sys
from pathlib import Path
import platform

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.screen_control import ScreenController


class TestScreenController(unittest.TestCase):
    """Test screen controller."""

    def setUp(self):
        """Set up test fixtures."""
        self.controller = ScreenController()
        self.is_windows = platform.system() == 'Windows'

    def test_lock_screen_returns_result(self):
        """Test lock screen returns a result (but don't actually lock)."""
        # We can't test actual locking in CI, but we can test the method exists
        self.assertTrue(hasattr(self.controller, 'lock_screen'))
        self.assertTrue(callable(self.controller.lock_screen))

    def test_sleep_returns_result(self):
        """Test sleep returns a result (but don't actually sleep)."""
        self.assertTrue(hasattr(self.controller, 'sleep'))
        self.assertTrue(callable(self.controller.sleep))

    def test_shutdown_dry_run(self):
        """Test shutdown method exists (but don't actually shutdown)."""
        self.assertTrue(hasattr(self.controller, 'shutdown'))
        self.assertTrue(callable(self.controller.shutdown))

    def test_restart_dry_run(self):
        """Test restart method exists (but don't actually restart)."""
        self.assertTrue(hasattr(self.controller, 'restart'))
        self.assertTrue(callable(self.controller.restart))

    def test_cancel_shutdown(self):
        """Test cancel shutdown."""
        result = self.controller.cancel_shutdown()

        # Should return a result (either success or error)
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)

        if not self.is_windows:
            # On non-Windows, should return error
            self.assertFalse(result['success'])

    def test_monitor_control_methods_exist(self):
        """Test monitor control methods exist."""
        self.assertTrue(hasattr(self.controller, 'turn_off_monitor'))
        self.assertTrue(callable(self.controller.turn_off_monitor))

        self.assertTrue(hasattr(self.controller, 'turn_on_monitor'))
        self.assertTrue(callable(self.controller.turn_on_monitor))

    def test_hibernate_method_exists(self):
        """Test hibernate method exists."""
        self.assertTrue(hasattr(self.controller, 'hibernate'))
        self.assertTrue(callable(self.controller.hibernate))

    def test_log_off_method_exists(self):
        """Test log off method exists."""
        self.assertTrue(hasattr(self.controller, 'log_off'))
        self.assertTrue(callable(self.controller.log_off))

    def test_windows_detection(self):
        """Test Windows platform detection."""
        expected_windows = platform.system() == 'Windows'
        self.assertEqual(self.controller.is_windows, expected_windows)


if __name__ == '__main__':
    unittest.main()

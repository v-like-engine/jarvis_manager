"""Tests for time and date module."""

import unittest
import sys
from pathlib import Path
from datetime import datetime
import tempfile

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.time_date import TimeDateManager


class TestTimeDateManager(unittest.TestCase):
    """Test time and date manager."""

    def setUp(self):
        """Set up test fixtures."""
        # Use temporary file for alarms
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = TimeDateManager(alarms_file=self.temp_file.name)

    def tearDown(self):
        """Clean up test fixtures."""
        import os
        try:
            os.unlink(self.temp_file.name)
        except:
            pass

    def test_get_current_time(self):
        """Test getting current time."""
        result = self.manager.get_current_time()

        self.assertTrue(result['success'])
        self.assertIn('time', result)
        self.assertIn('hour', result)
        self.assertIn('minute', result)

        # Hour should be 0-23
        self.assertGreaterEqual(result['hour'], 0)
        self.assertLessEqual(result['hour'], 23)

        # Minute should be 0-59
        self.assertGreaterEqual(result['minute'], 0)
        self.assertLessEqual(result['minute'], 59)

    def test_get_current_date(self):
        """Test getting current date."""
        result = self.manager.get_current_date()

        self.assertTrue(result['success'])
        self.assertIn('date', result)
        self.assertIn('year', result)
        self.assertIn('month', result)
        self.assertIn('day', result)
        self.assertIn('weekday', result)

        # Check current year is reasonable
        current_year = datetime.now().year
        self.assertEqual(result['year'], current_year)

        # Month should be 1-12
        self.assertGreaterEqual(result['month'], 1)
        self.assertLessEqual(result['month'], 12)

    def test_get_current_datetime(self):
        """Test getting current date and time."""
        result = self.manager.get_current_datetime()

        self.assertTrue(result['success'])
        self.assertIn('datetime', result)
        self.assertIn('date', result)
        self.assertIn('time', result)

    def test_get_weekday(self):
        """Test getting weekday."""
        result = self.manager.get_weekday()

        self.assertTrue(result['success'])
        self.assertIn('weekday', result)
        self.assertIn('weekday_number', result)

        # Weekday number should be 0-6 (Monday-Sunday)
        self.assertGreaterEqual(result['weekday_number'], 0)
        self.assertLessEqual(result['weekday_number'], 6)

        # Weekday should be a day name
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.assertIn(result['weekday'], valid_days)

    def test_set_alarm(self):
        """Test setting an alarm."""
        result = self.manager.set_alarm('14:30', 'Test alarm')

        self.assertTrue(result['success'])
        self.assertIn('alarm_id', result)
        self.assertIn('alarm_time', result)
        self.assertIn('seconds_until', result)

    def test_set_alarm_invalid_format(self):
        """Test setting alarm with invalid format."""
        result = self.manager.set_alarm('invalid', 'Test alarm')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_list_alarms(self):
        """Test listing alarms."""
        # Set an alarm first
        self.manager.set_alarm('15:00', 'Test alarm')

        result = self.manager.list_alarms()

        self.assertTrue(result['success'])
        self.assertIn('count', result)
        self.assertIn('alarms', result)
        self.assertGreaterEqual(result['count'], 1)

    def test_cancel_alarm(self):
        """Test cancelling an alarm."""
        # Set an alarm first
        set_result = self.manager.set_alarm('16:00', 'Test alarm')
        alarm_id = set_result['alarm_id']

        # Cancel it
        result = self.manager.cancel_alarm(alarm_id)

        self.assertTrue(result['success'])

    def test_cancel_nonexistent_alarm(self):
        """Test cancelling a non-existent alarm."""
        result = self.manager.cancel_alarm('nonexistent_id')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_start_timer(self):
        """Test starting a timer."""
        result = self.manager.start_timer(5, 'Test timer')

        self.assertTrue(result['success'])
        self.assertIn('timer_id', result)
        self.assertIn('duration_minutes', result)
        self.assertEqual(result['duration_minutes'], 5)


if __name__ == '__main__':
    unittest.main()

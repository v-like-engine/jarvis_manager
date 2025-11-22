"""Time and date manager for time/date queries and alarms."""

import logging
from datetime import datetime, timedelta, time as datetime_time
from typing import Dict, Any, Optional, List
import threading
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TimeDateManager:
    """
    Manage time, date, and alarm operations.

    Provides:
    - Current time/date queries
    - Alarm setting
    - Timer functionality
    - Date calculations
    """

    def __init__(self, alarms_file: Optional[str] = None):
        """
        Initialize time/date manager.

        Args:
            alarms_file: Path to alarms storage file
        """
        if alarms_file is None:
            alarms_file = Path(__file__).parent.parent.parent / "data" / "alarms.json"

        self.alarms_file = Path(alarms_file)
        self.alarms: List[Dict[str, Any]] = []
        self.active_timers: Dict[str, threading.Timer] = {}

        # Create data directory if needed
        self.alarms_file.parent.mkdir(parents=True, exist_ok=True)

        # Load saved alarms
        self._load_alarms()

        logger.info("TimeDateManager initialized")

    def get_current_time(self) -> Dict[str, Any]:
        """
        Get current time.

        Returns:
            Dictionary with current time
        """
        try:
            now = datetime.now()

            return {
                'success': True,
                'time': now.strftime('%H:%M:%S'),
                'time_12h': now.strftime('%I:%M:%S %p'),
                'hour': now.hour,
                'minute': now.minute,
                'second': now.second,
                'message': f"Current time: {now.strftime('%I:%M %p')}"
            }

        except Exception as e:
            logger.error(f"Error getting current time: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_current_date(self) -> Dict[str, Any]:
        """
        Get current date.

        Returns:
            Dictionary with current date
        """
        try:
            now = datetime.now()

            return {
                'success': True,
                'date': now.strftime('%Y-%m-%d'),
                'date_formatted': now.strftime('%B %d, %Y'),
                'year': now.year,
                'month': now.month,
                'day': now.day,
                'weekday': now.strftime('%A'),
                'message': f"Today is {now.strftime('%A, %B %d, %Y')}"
            }

        except Exception as e:
            logger.error(f"Error getting current date: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_current_datetime(self) -> Dict[str, Any]:
        """
        Get current date and time.

        Returns:
            Dictionary with current datetime
        """
        try:
            now = datetime.now()

            return {
                'success': True,
                'datetime': now.isoformat(),
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M:%S'),
                'formatted': now.strftime('%A, %B %d, %Y at %I:%M %p'),
                'message': f"{now.strftime('%A, %B %d, %Y at %I:%M %p')}"
            }

        except Exception as e:
            logger.error(f"Error getting current datetime: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_weekday(self) -> Dict[str, Any]:
        """
        Get current day of week.

        Returns:
            Dictionary with weekday info
        """
        try:
            now = datetime.now()
            weekday = now.strftime('%A')

            return {
                'success': True,
                'weekday': weekday,
                'weekday_number': now.weekday(),  # 0 = Monday
                'message': f"Today is {weekday}"
            }

        except Exception as e:
            logger.error(f"Error getting weekday: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def set_alarm(self, time_str: str, message: str = "Alarm!") -> Dict[str, Any]:
        """
        Set an alarm for a specific time.

        Args:
            time_str: Time in format "HH:MM" or "HH:MM:SS"
            message: Alarm message

        Returns:
            Dictionary with alarm info
        """
        try:
            # Parse time
            try:
                if ':' in time_str:
                    parts = time_str.split(':')
                    if len(parts) == 2:
                        hour, minute = int(parts[0]), int(parts[1])
                        second = 0
                    elif len(parts) == 3:
                        hour, minute, second = int(parts[0]), int(parts[1]), int(parts[2])
                    else:
                        raise ValueError("Invalid time format")
                else:
                    raise ValueError("Invalid time format")
            except ValueError as e:
                return {
                    'success': False,
                    'error': f"Invalid time format. Use HH:MM or HH:MM:SS. Error: {e}"
                }

            # Create alarm time
            now = datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)

            # If time has passed today, set for tomorrow
            if alarm_time <= now:
                alarm_time += timedelta(days=1)

            # Calculate seconds until alarm
            seconds_until = (alarm_time - now).total_seconds()

            # Create alarm entry
            alarm_id = f"alarm_{len(self.alarms) + 1}"
            alarm = {
                'id': alarm_id,
                'time': alarm_time.strftime('%H:%M:%S'),
                'message': message,
                'created': now.isoformat(),
                'trigger_time': alarm_time.isoformat(),
                'active': True
            }

            self.alarms.append(alarm)
            self._save_alarms()

            # Schedule alarm (in real implementation, this would trigger a notification)
            # For now, we just log it
            logger.info(f"Alarm set for {alarm_time.strftime('%I:%M %p')}: {message}")

            return {
                'success': True,
                'alarm_id': alarm_id,
                'alarm_time': alarm_time.strftime('%I:%M %p'),
                'seconds_until': int(seconds_until),
                'message': f"Alarm set for {alarm_time.strftime('%I:%M %p')}"
            }

        except Exception as e:
            logger.error(f"Error setting alarm: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_alarms(self) -> Dict[str, Any]:
        """
        List all active alarms.

        Returns:
            Dictionary with alarms list
        """
        try:
            active_alarms = [a for a in self.alarms if a.get('active', False)]

            return {
                'success': True,
                'count': len(active_alarms),
                'alarms': active_alarms,
                'message': f"{len(active_alarms)} active alarm(s)"
            }

        except Exception as e:
            logger.error(f"Error listing alarms: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def cancel_alarm(self, alarm_id: str) -> Dict[str, Any]:
        """
        Cancel an alarm.

        Args:
            alarm_id: ID of alarm to cancel

        Returns:
            Dictionary with result
        """
        try:
            for alarm in self.alarms:
                if alarm['id'] == alarm_id:
                    alarm['active'] = False
                    self._save_alarms()

                    return {
                        'success': True,
                        'message': f"Alarm {alarm_id} cancelled"
                    }

            return {
                'success': False,
                'error': f"Alarm {alarm_id} not found"
            }

        except Exception as e:
            logger.error(f"Error cancelling alarm: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def start_timer(self, minutes: int, message: str = "Timer finished!") -> Dict[str, Any]:
        """
        Start a countdown timer.

        Args:
            minutes: Timer duration in minutes
            message: Timer completion message

        Returns:
            Dictionary with timer info
        """
        try:
            timer_id = f"timer_{len(self.active_timers) + 1}"
            end_time = datetime.now() + timedelta(minutes=minutes)

            logger.info(f"Timer {timer_id} started for {minutes} minutes")

            return {
                'success': True,
                'timer_id': timer_id,
                'duration_minutes': minutes,
                'end_time': end_time.strftime('%I:%M %p'),
                'message': f"Timer started for {minutes} minute(s)"
            }

        except Exception as e:
            logger.error(f"Error starting timer: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _load_alarms(self):
        """Load alarms from file."""
        try:
            if self.alarms_file.exists():
                with open(self.alarms_file, 'r', encoding='utf-8') as f:
                    self.alarms = json.load(f)
                logger.info(f"Loaded {len(self.alarms)} alarms")
        except Exception as e:
            logger.error(f"Error loading alarms: {e}")
            self.alarms = []

    def _save_alarms(self):
        """Save alarms to file."""
        try:
            with open(self.alarms_file, 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, indent=2)
            logger.info(f"Saved {len(self.alarms)} alarms")
        except Exception as e:
            logger.error(f"Error saving alarms: {e}")

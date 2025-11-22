# Gerald Desktop Manager - New Commands Added

## Overview

This document lists all new commands added to the Command Service (Agent 3) for extended functionality.

## Character Switching Commands

**Command Type:** `character_switch`

Allows switching between different character personalities for both ASR and LLM services.

### Examples:
- "Switch to Rapunzel" / "Переключись на Рапунцель"
- "Change to Winnie Pooh" / "Смени персонажа на Винни Пуха"
- "Activate Terminator mode" / "Активируй режим Терминатора"
- "Who are you now?" / "Кто ты сейчас?"

### API:
```python
{
    "command_type": "character_switch",
    "params": {
        "character_name": "Rapunzel"
    }
}
```

---

## System Information Commands

**Module:** `modules/system_info/system_info_manager.py`

Read-only system queries (all safe - no confirmation required).

### Computer Name
**Command Type:** `system_info_computer_name`

Get the computer's hostname.

**Example:** "What's my computer name?" / "Как зовут мой компьютер?"

### Memory (RAM) Information
**Command Type:** `system_info_memory`

Get RAM usage and availability.

**Example:** "How much RAM?" / "Сколько оперативной памяти?"

**Response:**
```json
{
    "total_gb": 16.0,
    "available_gb": 8.5,
    "used_gb": 7.5,
    "percent_used": 47.0,
    "message": "RAM: 7.5GB / 16.0GB used (47%)"
}
```

### CPU Usage
**Command Type:** `system_info_cpu`

Get current CPU usage and info.

**Example:** "CPU usage?" / "Загрузка процессора?"

**Response:**
```json
{
    "cpu_percent": 35.2,
    "cpu_count": 8,
    "cpu_count_physical": 4,
    "cpu_freq_mhz": 3600
}
```

### Disk Space
**Command Type:** `system_info_disk`

Get disk space information.

**Example:** "Disk space?" / "Свободное место на диске?"

**Parameters:**
- `path` (optional): Disk path to check (default: "C:\\")

### Operating System Info
**Command Type:** `system_info_os`

Get OS version and details.

### Network Information
**Command Type:** `system_info_network`

Get hostname and IP address.

### System Uptime
**Command Type:** `system_info_uptime`

Get how long the system has been running.

### All System Info
**Command Type:** `system_info_all`

Get all system information in one call.

---

## Time and Date Commands

**Module:** `modules/time_date/time_date_manager.py`

### Current Time
**Command Type:** `time_get`

Get current time.

**Example:** "What time is it?" / "Который час?"

**Response:**
```json
{
    "time": "14:30:45",
    "time_12h": "02:30:45 PM",
    "hour": 14,
    "minute": 30,
    "second": 45,
    "message": "Current time: 02:30 PM"
}
```

### Current Date
**Command Type:** `date_get`

Get current date.

**Example:** "What's the date?" / "Какое сегодня число?"

**Response:**
```json
{
    "date": "2025-11-22",
    "date_formatted": "November 22, 2025",
    "year": 2025,
    "month": 11,
    "day": 22,
    "weekday": "Friday"
}
```

### Weekday
**Command Type:** `weekday_get`

Get current day of the week.

**Example:** "What day is today?" / "Какой сегодня день?"

### Date and Time
**Command Type:** `datetime_get`

Get both date and time.

### Set Alarm
**Command Type:** `alarm_set`

Set an alarm for a specific time.

**Example:** "Set alarm for 5 PM" / "Поставь будильник на 5 вечера"

**Parameters:**
- `time`: Time in "HH:MM" format (e.g., "17:00")
- `message` (optional): Alarm message

**Response:**
```json
{
    "alarm_id": "alarm_1",
    "alarm_time": "05:00 PM",
    "seconds_until": 18000,
    "message": "Alarm set for 05:00 PM"
}
```

### List Alarms
**Command Type:** `alarm_list`

List all active alarms.

### Cancel Alarm
**Command Type:** `alarm_cancel`

Cancel a specific alarm.

**Parameters:**
- `alarm_id`: ID of alarm to cancel

### Start Timer
**Command Type:** `timer_start`

Start a countdown timer.

**Parameters:**
- `minutes`: Timer duration in minutes
- `message` (optional): Completion message

---

## Calculator Commands

**Module:** `modules/calculator/calculator.py`

Safe mathematical computations with natural language support.

### Calculate Expression
**Command Type:** `calculate`

Evaluate a mathematical expression.

**Examples:**
- "Calculate 5 plus 3" / "Посчитай 5 плюс 3"
- "What's 100 divided by 4?" / "Сколько будет 100 разделить на 4?"
- "(2 + 3) * 4"
- "sqrt(16)"

**Parameters:**
- `expression`: Mathematical expression (supports +, -, *, /, **, sqrt, etc.)

**Natural Language Support:**
- "plus" / "add" → +
- "minus" / "subtract" → -
- "times" / "multiply" → *
- "divided by" / "divide" → /
- "to the power of" → **
- "squared" → **2

### Specific Operations

**Command Type:** `calculate_add`
**Parameters:** `a`, `b`

**Command Type:** `calculate_subtract`
**Parameters:** `a`, `b`

**Command Type:** `calculate_multiply`
**Parameters:** `a`, `b`

**Command Type:** `calculate_divide`
**Parameters:** `a`, `b`

---

## Screen Control Commands

**Module:** `modules/screen_control/screen_controller.py`

Control screen, power, and system state.

### Lock Screen
**Command Type:** `screen_lock`

Lock the computer screen.

**Example:** "Lock screen" / "Заблокируй экран"

**Safety:** SAFE (no confirmation required)

### Sleep
**Command Type:** `screen_sleep`

Put computer to sleep.

**Example:** "Sleep" / "Режим сна"

**Safety:** REQUIRES CONFIRMATION

### Shutdown
**Command Type:** `screen_shutdown`

Shutdown the computer.

**Example:** "Shutdown" / "Выключи компьютер"

**Parameters:**
- `force` (optional): Force close applications (default: false)
- `timeout` (optional): Seconds until shutdown (default: 60)

**Safety:** REQUIRES CONFIRMATION

### Restart
**Command Type:** `screen_restart`

Restart the computer.

**Example:** "Restart" / "Перезагрузи компьютер"

**Parameters:**
- `force` (optional): Force close applications (default: false)
- `timeout` (optional): Seconds until restart (default: 60)

**Safety:** REQUIRES CONFIRMATION

### Cancel Shutdown
**Command Type:** `screen_cancel_shutdown`

Cancel a pending shutdown or restart.

**Safety:** SAFE

### Monitor Control
**Command Type:** `screen_monitor_off`
**Command Type:** `screen_monitor_on`

Turn monitor(s) on or off.

**Safety:** SAFE

### Hibernate
**Command Type:** `screen_hibernate`

Hibernate the computer.

**Safety:** REQUIRES CONFIRMATION

### Log Off
**Command Type:** `screen_logoff`

Log off current user.

**Safety:** REQUIRES CONFIRMATION

---

## App Launcher Enhancements

**New Module:** `modules/app_launcher/app_favorites.py`

### Features Added:

1. **Favorites Management**
   - Mark apps as favorites
   - Fuzzy match boost for favorites (+10 points)
   - Quick access to favorite apps

2. **Usage Tracking**
   - Track app launch frequency
   - Boost scores based on usage (up to +15 points)
   - Learn from usage patterns

3. **Recent Apps**
   - Track recently launched apps
   - "Open recent" functionality

4. **Learning System**
   - Remember user query → app mappings
   - Improve matching over time

---

## Installation and Deployment

### New Files:

1. **`install.py`** - Interactive installer
   - Dependency installation
   - Directory creation
   - Shortcut creation
   - Startup configuration
   - Configuration wizard

2. **`uninstall.py`** - Clean uninstaller
   - Remove shortcuts
   - Remove startup entries
   - Clean user data (optional)
   - Remove configuration (optional)

3. **`windows_service.py`** - Windows service wrapper
   - Run Gerald as Windows service
   - Auto-restart on failure
   - Service management (install/start/stop/remove)

4. **`services/command_service/modules/settings/deployment.py`**
   - Deployment utilities
   - System tray integration helpers
   - Service management API

---

## Safety Rules Updated

**File:** `services/command_service/config/safety_rules.yaml`

### New Safe Commands (no confirmation):
- All character switching commands
- All system information queries (read-only)
- All time/date queries
- All calculator operations
- Screen lock
- Monitor on/off
- Cancel shutdown

### New Confirmation Required:
- Screen sleep
- Screen shutdown
- Screen restart
- Screen hibernate
- Screen logoff

---

## Testing

### New Test Files:

1. **`tests/test_system_info.py`**
   - Test all system info queries
   - Memory, CPU, disk, network tests

2. **`tests/test_time_date.py`**
   - Time/date queries
   - Alarm setting and cancellation
   - Timer functionality

3. **`tests/test_calculator.py`**
   - Basic arithmetic
   - Complex expressions
   - Natural language parsing
   - Safety checks

4. **`tests/test_screen_control.py`**
   - Screen control methods
   - Windows detection

---

## Command Count Summary

**Total New Command Types Added: 35+**

### Breakdown:
- Character Switching: 1
- System Information: 8
- Time/Date: 8
- Calculator: 5+
- Screen Control: 10
- App Launcher Enhancements: N/A (improved existing)

---

## API Endpoint Updates

All new commands are accessible via the existing endpoint:

```
POST /commands/execute
```

Example request:
```json
{
    "command_type": "system_info_memory",
    "params": {},
    "language": "en"
}
```

---

## Usage Examples

### English:
1. "Gerald, what's my computer name?"
2. "Gerald, how much RAM do I have?"
3. "Gerald, what time is it?"
4. "Gerald, calculate 25 times 4"
5. "Gerald, lock the screen"
6. "Gerald, switch to Rapunzel"

### Russian (Русский):
1. "Джеральд, как зовут мой компьютер?"
2. "Джеральд, сколько оперативной памяти?"
3. "Джеральд, который час?"
4. "Джеральд, посчитай 25 умножить на 4"
5. "Джеральд, заблокируй экран"
6. "Джеральд, переключись на Рапунцель"

---

## Integration Notes

### For ASR Service (Agent 1):
- Character switch commands should update voice recognition personality
- New command patterns need to be added to intent recognition

### For LLM Service (Agent 2):
- Character switch commands should update response personality
- System info can be used for context-aware responses
- Time/date info available for temporal reasoning

### For Command Service (Agent 3):
- All new modules are integrated in command_router.py
- Safety rules configured appropriately
- Tests provided for all new functionality

---

## Next Steps

1. **ASR Service Integration**: Add voice recognition patterns for all new commands
2. **LLM Service Integration**: Train character personalities and response patterns
3. **UI Development**: Create system tray icon and notification system
4. **Documentation**: User manual with command examples
5. **Testing**: Integration testing with all services running

---

## Deployment

### Installation:
```bash
python install.py
```

### Uninstallation:
```bash
python uninstall.py
```

### Windows Service:
```bash
# Install (requires admin)
python windows_service.py install

# Start
python windows_service.py start

# Stop
python windows_service.py stop

# Remove
python windows_service.py remove
```

---

**Command Service Extended Successfully!**

All new functionality is ready for deployment and integration with ASR and LLM services.

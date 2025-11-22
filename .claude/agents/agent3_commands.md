# Agent 3: Command Execution Service

## Your Responsibility
You are responsible for the **Command Service** - executing all system commands including app launching/closing, file operations, terminal commands, system settings, music control, and language switching.

## Your Files (You Own These - No Other Agent Can Modify)
```
services/command_service/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main command service entry point
│   ├── command_router.py          # Route commands to appropriate modules
│   ├── command_validator.py       # Validate and sanitize commands
│   ├── safety_checker.py          # Check if command is safe
│   └── execution_manager.py       # Manage command execution
├── modules/
│   ├── __init__.py
│   ├── app_launcher/
│   │   ├── __init__.py
│   │   ├── app_finder.py          # Find apps on Windows system
│   │   ├── app_launcher.py        # Launch applications
│   │   ├── app_closer.py          # Close running applications
│   │   └── app_database.py        # Cache of installed apps
│   ├── terminal/
│   │   ├── __init__.py
│   │   ├── terminal_executor.py   # Execute terminal commands safely
│   │   ├── command_whitelist.py   # Safe commands list
│   │   └── output_handler.py      # Handle command output
│   ├── file_ops/
│   │   ├── __init__.py
│   │   ├── file_manager.py        # Create/delete files
│   │   ├── directory_manager.py   # Navigate/create directories
│   │   ├── file_browser.py        # List directory contents
│   │   └── path_resolver.py       # Resolve and validate paths
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── startup_manager.py     # Configure OS startup launch
│   │   ├── language_manager.py    # Switch system language
│   │   └── preferences.py         # User preferences storage
│   └── music_control/
│       ├── __init__.py
│       ├── music_controller.py    # Control music apps
│       └── app_interfaces.py      # Interfaces for specific apps (Yandex Music, etc.)
├── config/
│   ├── command_config.yaml        # Command service configuration
│   ├── safety_rules.yaml          # Safety rules for commands
│   └── app_aliases.yaml           # App name aliases and mappings
├── tests/
│   ├── test_app_launcher.py
│   ├── test_terminal_executor.py
│   ├── test_file_manager.py
│   ├── test_safety_checker.py
│   ├── test_settings.py
│   └── test_music_control.py
└── requirements.txt               # Command service dependencies

shared/utils/
├── __init__.py
├── windows_api.py                 # Windows API utilities
├── process_manager.py             # Process management utilities
└── logger.py                      # Logging utilities
```

## Technologies You Should Use

### Windows Integration
- **pywin32** - Windows API access (essential!)
- **psutil** - Process and system utilities
- **winreg** - Windows registry access
- **ctypes** - Windows API calls
- **wmi** - Windows Management Instrumentation

### App Management
- **subprocess** - Launch and control processes
- **win32com.client** - Control Windows applications
- **win32gui** - Window management
- **win32process** - Process control

### File Operations
- **pathlib** - Modern path handling
- **shutil** - File operations
- **os** - OS-level operations
- **watchdog** - File system monitoring (optional)

### Terminal
- **subprocess** - Execute commands
- **cmd/powershell** - Command execution engines

### Music Control
- **pyautogui** - Keyboard/mouse automation (last resort)
- **pycaw** - Windows audio control
- **COM interfaces** - For specific app control

## Your Tasks

### Phase 1: App Launcher Module
1. Implement Windows app discovery (Start Menu, Program Files, etc.)
2. Create fuzzy app name matching (e.g., "Yandex bro" → "Yandex Browser")
3. Implement app launching via Windows API
4. Create app database with caching
5. Implement app closing by process name/window title

### Phase 2: Terminal Module
6. Implement safe terminal command execution
7. Create command whitelist/blacklist
8. Add output capture and parsing
9. Implement timeout and resource limits
10. Add support for PowerShell and CMD

### Phase 3: File Operations Module
11. Implement file creation/deletion with safety checks
12. Create directory navigation and listing
13. Implement directory creation
14. Add path validation and sanitization
15. Create safety confirmations for destructive operations

### Phase 4: Settings Module
16. Implement Windows startup configuration (Registry/Task Scheduler)
17. Create language switching for Gerald (not OS language)
18. Implement user preferences storage
19. Add configuration persistence

### Phase 5: Music Control Module
20. Implement media key simulation (Play/Pause/Next/Previous)
21. Add volume control
22. Create interfaces for specific apps (Yandex Music, Spotify, etc.)
23. Implement "play music" command

### Phase 6: Safety & Integration
24. Implement comprehensive safety checker
25. Create command validation system
26. Add confirmation request system
27. Write comprehensive tests
28. Optimize for Windows 10/11

## API You Must Expose

Your Command service should expose:

```python
# HTTP endpoints (using FastAPI)
POST /commands/execute         # Execute a command
POST /commands/validate        # Validate command safety
GET  /commands/apps/list       # List installed apps
GET  /commands/apps/running    # List running apps
POST /commands/confirm         # Confirm dangerous operation
GET  /commands/status          # Service status

# Request format for command execution
{
    "command_id": "uuid",
    "command_type": "app_launch" | "app_close" | "terminal" | "file_create" |
                    "file_delete" | "dir_create" | "dir_list" | "music_control" |
                    "settings" | "system",
    "language": "en" | "ru",
    "params": {
        # Depends on command_type
        "app_name": "Yandex Browser",        # for app_launch/app_close
        "terminal_command": "dir",           # for terminal
        "file_path": "C:\\Users\\...",      # for file operations
        "action": "play" | "pause" | "next"  # for music_control
    },
    "confirmed": false  # true if user confirmed dangerous operation
}

# Response format
{
    "success": true,
    "requires_confirmation": false,
    "confirmation_message": "This will delete...",  # if requires_confirmation
    "result": {
        "output": "Application launched successfully",
        "details": {...}
    },
    "error": null
}

# Message queue topics
topic: "commands.execute"           # Subscribe to command execution requests
topic: "commands.result"            # Publish execution results
topic: "commands.confirmation"      # Request user confirmation
```

## Integration Points

1. **ASR Service (Agent 1)**: Receive parsed commands for execution
2. **LLM Service (Agent 2)**: Request natural language confirmations
3. **Shared Utils**: Windows API wrappers, process management

## Command Types and Safety Levels

### Safe Commands (Execute Immediately)
- App launch (from known locations)
- App close
- Directory listing
- Music control (play/pause/next)
- Language switching
- Volume control

### Requires Confirmation (Ask First)
- File deletion
- File creation (in system directories)
- Terminal commands (unless whitelisted)
- Directory deletion
- System settings changes
- Registry modifications

### Forbidden (Never Execute)
- Format drives
- Delete system files
- Modify critical registry keys
- Kill critical system processes
- Network attacks

## App Discovery Strategy

Scan these locations for apps:
1. Start Menu: `C:\ProgramData\Microsoft\Windows\Start Menu`
2. User Start Menu: `%APPDATA%\Microsoft\Windows\Start Menu`
3. Program Files: `C:\Program Files` and `C:\Program Files (x86)`
4. Windows Apps: Via PowerShell `Get-AppxPackage`
5. Registry: `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths`

Build searchable database with:
- App name
- Executable path
- Keywords/aliases
- Installation path

## Fuzzy Matching for App Names

Use fuzzy string matching for app discovery:
- **fuzzywuzzy** or **rapidfuzz** library
- Match threshold: 70%
- Support partial matches: "Yandex bro" → "Yandex Browser"
- Handle typos and abbreviations

```python
# Example
user_input = "open yandex bro"
best_match = find_best_app_match("yandex bro")
# Returns: ("Yandex Browser", 85, "C:\\Program Files\\Yandex\\Browser\\browser.exe")
```

## Safety Checker Implementation

Create `safety_checker.py` with rules:

```python
class SafetyLevel(Enum):
    SAFE = 1              # Execute immediately
    NEEDS_CONFIRMATION = 2 # Ask user first
    FORBIDDEN = 3         # Never execute

def check_command_safety(command_type, params) -> Tuple[SafetyLevel, str]:
    """
    Returns (safety_level, reason)
    """
    if command_type == "file_delete":
        if is_system_file(params["file_path"]):
            return (SafetyLevel.FORBIDDEN, "Cannot delete system files")
        return (SafetyLevel.NEEDS_CONFIRMATION, f"Delete {params['file_path']}?")

    # ... more rules
```

## Startup Configuration (Windows)

Implement two methods:
1. **Registry** (User-level): `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
2. **Task Scheduler** (More reliable): Create task that runs at login

```python
def enable_startup():
    # Method 1: Registry
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "GeraldDesktopManager", 0, winreg.REG_SZ,
                      f'"{sys.executable}" "{main_script_path}"')
    winreg.CloseKey(key)

    # Method 2: Task Scheduler (recommended)
    # Use win32com.client or schtasks.exe
```

## Terminal Command Execution

Safe execution with limits:

```python
import subprocess

def execute_terminal_command(command: str, timeout: int = 30):
    """
    Execute command with safety checks
    """
    # Check whitelist
    if not is_safe_command(command):
        raise UnsafeCommandError()

    # Execute with timeout
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=safe_working_dir
    )

    return result.stdout, result.stderr, result.returncode
```

## Installation Instructions You Should Create

Create `services/command_service/requirements.txt`:
```
fastapi>=0.104.0
uvicorn>=0.24.0
pywin32>=306
psutil>=5.9.0
pydantic>=2.0.0
pyyaml>=6.0
rapidfuzz>=3.5.0
pycaw>=20181226
pyautogui>=0.9.54
aiofiles>=23.0.0
```

## Configuration Files

### `config/safety_rules.yaml`
```yaml
safe_commands:
  - app_launch
  - app_close
  - dir_list
  - music_play
  - music_pause
  - volume_control

confirmation_required:
  - file_delete
  - file_create_in_system
  - terminal_command
  - dir_delete
  - registry_modify

forbidden_patterns:
  - "format *"
  - "del /s /q C:\\"
  - "rm -rf /"
  - "reg delete HKLM"

system_paths:
  - "C:\\Windows"
  - "C:\\Program Files"
  - "C:\\System"

whitelisted_terminal_commands:
  - "dir"
  - "ls"
  - "cd"
  - "pwd"
  - "echo"
  - "type"
  - "ping"
```

### `config/app_aliases.yaml`
```yaml
aliases:
  yandex:
    - "Yandex Browser"
    - "Yandex"
    - "Yandex bro"

  chrome:
    - "Google Chrome"
    - "Chrome"

  notepad:
    - "Notepad"
    - "note"
```

## Windows-Specific Implementations

### Launch App
```python
import subprocess
import os

def launch_app(exe_path: str):
    subprocess.Popen([exe_path], shell=True)
```

### Close App
```python
import psutil

def close_app(app_name: str):
    for proc in psutil.process_iter(['name', 'exe']):
        if app_name.lower() in proc.info['name'].lower():
            proc.terminate()
            proc.wait(timeout=5)
```

### Music Control
```python
import pyautogui

def control_music(action: str):
    if action == "play" or action == "pause":
        pyautogui.press('playpause')
    elif action == "next":
        pyautogui.press('nexttrack')
    elif action == "previous":
        pyautogui.press('prevtrack')
```

## Notes from Agent 4 (Testing & Documentation)
Agent 4 will write testing feedback and suggestions here as they monitor your work.

---

## Getting Started

1. Set up FastAPI service structure
2. Implement app discovery and caching
3. Create app launcher with fuzzy matching
4. Implement safety checker
5. Add terminal command execution
6. Create file operations module
7. Implement startup configuration
8. Add music control
9. Write comprehensive tests

Start with `services/command_service/src/main.py` and app launcher module!

# Gerald Command Service

The **Command Service** is the "hands" of Gerald Desktop Manager - it executes all system operations safely with comprehensive validation and safety checks.

## Features

### 1. App Launcher Module
- **App Discovery**: Scans Windows system for installed apps (Start Menu, Program Files, Registry)
- **Fuzzy Matching**: "Yandex bro" → "Yandex Browser" (70% threshold)
- **App Database**: Cached database with auto-refresh
- **Launch & Close**: Launch apps via Windows API, close by name/PID/window title

### 2. Terminal Module
- **Safe Execution**: Execute CMD and PowerShell commands with safety checks
- **Command Whitelist**: Whitelisted commands execute without confirmation
- **Timeout & Limits**: Configurable timeouts and resource limits
- **Output Capture**: Full stdout/stderr capture and parsing

### 3. File Operations Module
- **File Management**: Create, delete, copy, move files
- **Directory Management**: Create, delete, navigate directories
- **File Browser**: List, search, and browse directory contents
- **Path Validation**: Protect system files and critical directories

### 4. Settings Module
- **Startup Manager**: Configure Windows startup (Registry + Task Scheduler)
- **Language Manager**: Switch Gerald's language (EN/RU)
- **Preferences**: Store and manage user preferences

### 5. Music Control Module
- **Media Keys**: Play/Pause/Next/Previous/Stop
- **Volume Control**: Up/Down/Set/Mute via pycaw
- **Multi-Player**: Support for Yandex Music, Spotify, VLC, etc.

### 6. Safety Checker
Three-level safety system:
- **SAFE**: Execute immediately (app_launch, dir_list, music_control)
- **NEEDS_CONFIRMATION**: Ask user first (file_delete, terminal_command)
- **FORBIDDEN**: Never execute (format drives, delete system files)

## Architecture

```
command_service/
├── src/
│   ├── main.py                 # FastAPI server
│   ├── command_router.py       # Route commands to modules
│   ├── command_validator.py    # Validate and sanitize
│   ├── safety_checker.py       # Three-level safety system
│   └── execution_manager.py    # Manage execution lifecycle
├── modules/
│   ├── app_launcher/           # App discovery and launching
│   ├── terminal/               # Terminal command execution
│   ├── file_ops/               # File operations
│   ├── settings/               # System settings
│   └── music_control/          # Music playback control
├── config/
│   ├── command_config.yaml     # Service configuration
│   ├── safety_rules.yaml       # Safety rules
│   └── app_aliases.yaml        # App name aliases
└── tests/                      # Comprehensive tests
```

## API Endpoints

### Command Execution
- `POST /commands/execute` - Execute a command
- `POST /commands/validate` - Validate command safety
- `POST /commands/confirm` - Confirm dangerous operation
- `DELETE /commands/{id}` - Cancel pending command

### App Management
- `GET /commands/apps/list` - List installed apps
- `GET /commands/apps/running` - List running apps
- `GET /commands/apps/search?query=...` - Search apps
- `POST /commands/apps/refresh` - Refresh app database

### Service Status
- `GET /commands/status` - Service status
- `GET /commands/history` - Command history
- `GET /commands/pending` - Pending confirmations
- `GET /health` - Health check

## Request Format

```json
{
  "command_type": "app_launch",
  "language": "en",
  "params": {
    "app_name": "Yandex Browser"
  },
  "confirmed": false
}
```

## Response Format

```json
{
  "success": true,
  "requires_confirmation": false,
  "result": {
    "message": "Application launched successfully",
    "pid": 12345
  },
  "error": null
}
```

## Safety Rules

### Protected Paths
- `C:\Windows`
- `C:\Windows\System32`
- `C:\Program Files`
- `C:\Program Files (x86)`

### Protected Processes
- `csrss.exe`, `wininit.exe`, `services.exe`
- `lsass.exe`, `winlogon.exe`, `explorer.exe`

### Whitelisted Commands
- `dir`, `ls`, `cd`, `pwd`, `echo`
- `type`, `cat`, `ping`, `ipconfig`

### Forbidden Patterns
- `format *`
- `del /s /q C:\`
- `rm -rf /`
- `reg delete HKLM`

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python src/main.py
```

## Configuration

Edit `/home/user/jarvis_manager/services/command_service/config/command_config.yaml`:

```yaml
service:
  host: "0.0.0.0"
  port: 8002

app_discovery:
  fuzzy_threshold: 70
  cache_refresh_interval: 3600

terminal:
  default_shell: "cmd"

music:
  preferred_player: "yandex_music"
  volume_step: 5
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_safety_checker.py -v

# Run with coverage
pytest tests/ --cov=src --cov=modules
```

## Usage Examples

### Launch Application
```python
POST /commands/execute
{
  "command_type": "app_launch",
  "params": {"app_name": "chrome"}
}
```

### Execute Terminal Command
```python
POST /commands/execute
{
  "command_type": "terminal",
  "params": {"terminal_command": "dir"}
}
```

### Control Music
```python
POST /commands/execute
{
  "command_type": "music_play",
  "params": {}
}
```

### Create File
```python
POST /commands/execute
{
  "command_type": "file_create",
  "params": {
    "file_path": "C:\\Users\\test\\note.txt",
    "content": "Hello World"
  }
}
```

## Windows Compatibility

This service is designed for **Windows 10/11** and uses:
- `pywin32` for Windows API access
- `psutil` for process management
- `pycaw` for audio control
- `rapidfuzz` for fuzzy matching
- Windows Registry and Task Scheduler

## Safety First

All operations go through safety checks:
1. **Validation**: Parameters validated and sanitized
2. **Safety Check**: Three-level safety assessment
3. **Confirmation**: Dangerous operations require user confirmation
4. **Execution**: Only safe/confirmed operations execute
5. **History**: All commands logged for audit

## Integration

This service integrates with:
- **ASR Service**: Receives parsed voice commands
- **LLM Service**: Requests natural language confirmations
- **Message Queue**: Publishes results and requests

## License

Part of Gerald Desktop Manager project.

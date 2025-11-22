# Gerald Desktop Manager - Deployment Guide

Complete guide for deploying Gerald Desktop Manager in production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [System Preparation](#system-preparation)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Service Setup](#service-setup)
6. [Post-Deployment Testing](#post-deployment-testing)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Checklist

Before deploying Gerald, ensure all requirements are met:

### Hardware Requirements

- [ ] **CPU**: Modern multi-core processor (Intel i5/AMD Ryzen 5 or better)
- [ ] **RAM**: Minimum 8GB (16GB recommended)
- [ ] **Disk Space**: 30GB free space
  - 25GB for models
  - 3GB for application
  - 2GB for user data and logs
- [ ] **Microphone**: USB or built-in microphone
- [ ] **Webcam**: Optional (for face recognition)

### Software Requirements

- [ ] **Operating System**: Windows 10 (build 1903+) or Windows 11
- [ ] **Python**: Version 3.10, 3.11, or 3.12 (64-bit)
- [ ] **Administrator Access**: For installation and startup configuration
- [ ] **Internet Connection**: For initial model download only

### Pre-Installation Verification

```powershell
# Verify Windows version
winver

# Verify Python version
python --version

# Check available disk space
Get-PSDrive C | Select-Object Free

# Check RAM
Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum
```

---

## System Preparation

### 1. Create Deployment Directory

```powershell
# Create installation directory
New-Item -Path "C:\Gerald" -ItemType Directory -Force

# Navigate to directory
cd C:\Gerald
```

### 2. Install Python (if not installed)

Download Python from [python.org](https://www.python.org/downloads/) and install:

```powershell
# Verify Python is in PATH
python --version
pip --version
```

**Important**: During Python installation, check "Add Python to PATH"

### 3. Clone or Extract Repository

```powershell
# Option 1: Clone from Git
git clone <repository-url> C:\Gerald\jarvis_manager

# Option 2: Extract from ZIP
Expand-Archive -Path gerald-manager-v1.0.0.zip -DestinationPath C:\Gerald\
```

---

## Installation Steps

### Step 1: Install Python Dependencies

```powershell
cd C:\Gerald\jarvis_manager

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies for all services
pip install -r services/asr_service/requirements.txt
pip install -r services/llm_service/requirements.txt
pip install -r services/command_service/requirements.txt
pip install -r requirements.txt
```

**Note**: If you encounter permission errors, run PowerShell as Administrator.

### Step 2: Download AI Models

```powershell
# Run model download script
python setup_models.py
```

This will download:
- **Vosk ASR models** (English + Russian): ~200MB
- **LLM model** (Phi-3-mini): ~2.3GB
- **Face recognition models**: ~10MB
- **TTS models**: ~50MB

**Total download**: ~2.5GB

**Estimated time**: 15-30 minutes depending on connection speed

### Step 3: Verify Installation

```powershell
# Run installation verification
python -m pytest tests/ -v --tb=short -k "test_initialization"
```

Expected output: All initialization tests pass

### Step 4: Configure Gerald

Edit `config/main_config.yaml`:

```yaml
gerald:
  character: "gerald"          # Options: gerald, winnie_pooh
  default_language: "en"       # Options: en, ru
  auto_start: false           # Launch with Windows

asr:
  vad_threshold: 0.5          # Voice detection sensitivity (0.0-1.0)
  sample_rate: 16000          # Audio sample rate
  mic_device_index: null      # null = default microphone

llm:
  model: "phi-3-mini"         # Local LLM model
  temperature: 0.7            # Response randomness (0.0-2.0)
  max_tokens: 100             # Max response length

logging:
  level: "INFO"               # Options: DEBUG, INFO, WARNING, ERROR
  max_size_mb: 100           # Max log file size
  backup_count: 5            # Number of backup log files
```

---

## Configuration

### Audio Configuration

Test microphone:

```powershell
# List available microphones
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(i, p.get_device_info_by_index(i)['name']) for i in range(p.get_device_count())]"
```

Set microphone in `config/main_config.yaml`:

```yaml
asr:
  mic_device_index: 1  # Use index from list above
```

### Character Selection

Available characters:
1. **Gerald** - Strict, loyal knight (default)
2. **Winnie Pooh** - Gentle, philosophical bear

Set in config:

```yaml
gerald:
  character: "winnie_pooh"  # Change from gerald
```

### Language Settings

Supported languages:
- `en` - English
- `ru` - Russian

Gerald auto-detects language, but you can set default:

```yaml
gerald:
  default_language: "ru"
```

### Startup Configuration

To launch Gerald with Windows:

```yaml
gerald:
  auto_start: true
```

Or use command:

```powershell
# Enable startup
python run_gerald.py --enable-startup

# Disable startup
python run_gerald.py --disable-startup
```

---

## Service Setup

### Option 1: Run as Console Application

Simple launch:

```powershell
# Using simple launcher
python start_gerald.py

# Using main launcher
python run_gerald.py

# With options
python run_gerald.py --character winnie_pooh --language ru
```

### Option 2: Run as Windows Service

See [WINDOWS_SERVICE.md](WINDOWS_SERVICE.md) for detailed instructions.

Quick setup:

```powershell
# Install as service
python install_service.py

# Start service
sc start GeraldManager

# Check status
sc query GeraldManager
```

### Option 3: Run with Task Scheduler

Create scheduled task to run at login:

```powershell
# Create task
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\Gerald\jarvis_manager\run_gerald.py"
$Trigger = New-ScheduledTaskTrigger -AtLogon
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries
Register-ScheduledTask -TaskName "GeraldManager" -Action $Action -Trigger $Trigger -Settings $Settings
```

---

## Post-Deployment Testing

### 1. Service Health Checks

```powershell
# Test ASR Service
Invoke-RestMethod -Uri "http://localhost:8001/health"

# Test LLM Service
Invoke-RestMethod -Uri "http://localhost:8002/health"

# Test Command Service
Invoke-RestMethod -Uri "http://localhost:8003/health"
```

Expected response: `{"status": "healthy"}`

### 2. Voice Command Testing

Test basic commands:

1. **English**:
   - "Open Notepad"
   - "Who are you?"
   - "Exit Gerald"

2. **Russian**:
   - "Открой блокнот"
   - "Кто ты?"
   - "Выключись"

### 3. Character Testing

```powershell
# Test character switching
python -c "from services.llm_service.src.character_manager import CharacterManager; cm = CharacterManager('services/llm_service/characters'); cm.load_character('gerald'); print(cm.get_character_info())"
```

### 4. Performance Testing

```powershell
# Run performance tests
python -m pytest tests/performance/ -v

# Check CPU usage
Get-Process python | Select-Object CPU, WS

# Check memory usage
Get-Process python | Select-Object PM, WS
```

Expected metrics:
- **CPU Usage**: <5% when idle
- **Memory Usage**: <4GB total
- **Response Time**: <2 seconds

### 5. Integration Testing

```powershell
# Run full integration tests
python -m pytest tests/integration/ -v
```

---

## Troubleshooting

### Common Issues

#### Issue: "Models not found"

**Solution**:
```powershell
python setup_models.py
```

#### Issue: "Port already in use"

**Solution**:
```powershell
# Find process using port
netstat -ano | findstr :8001

# Kill process
taskkill /PID <pid> /F
```

#### Issue: "Microphone not detected"

**Solution**:
```powershell
# Check Windows sound settings
ms-settings:sound

# Test microphone
python -c "import pyaudio; p = pyaudio.PyAudio(); print(f'Devices: {p.get_device_count()}')"
```

#### Issue: "Service won't start"

**Solution**:
```powershell
# Check logs
Get-Content logs/asr_service.log -Tail 50
Get-Content logs/llm_service.log -Tail 50
Get-Content logs/command_service.log -Tail 50

# Restart services
python run_gerald.py --restart
```

### Deployment Logs

Logs location: `C:\Gerald\jarvis_manager\logs\`

```powershell
# View logs
Get-ChildItem logs/ | Select-Object Name, Length, LastWriteTime

# Tail ASR log
Get-Content logs/asr_service.log -Wait
```

---

## Rollback Procedures

### Emergency Shutdown

```powershell
# Stop all services
python run_gerald.py --stop

# Or force kill
Get-Process python | Where-Object {$_.MainWindowTitle -like "*Gerald*"} | Stop-Process -Force
```

### Rollback to Previous Version

```powershell
# Stop current version
python run_gerald.py --stop

# Backup current version
Copy-Item -Path C:\Gerald\jarvis_manager -Destination C:\Gerald\jarvis_manager.backup -Recurse

# Restore previous version
Copy-Item -Path C:\Gerald\jarvis_manager.v1.0.0 -Destination C:\Gerald\jarvis_manager -Recurse -Force

# Start restored version
cd C:\Gerald\jarvis_manager
python run_gerald.py
```

### Uninstall

```powershell
# Stop services
python run_gerald.py --stop

# Remove startup entry (if enabled)
python run_gerald.py --disable-startup

# Remove directory
Remove-Item -Path C:\Gerald\jarvis_manager -Recurse -Force
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] System requirements verified
- [ ] Python installed and in PATH
- [ ] Admin access confirmed
- [ ] Backup of existing installation (if upgrading)

### Installation

- [ ] Dependencies installed
- [ ] Models downloaded
- [ ] Configuration updated
- [ ] Installation verified

### Testing

- [ ] Service health checks pass
- [ ] Voice commands working
- [ ] Character switching working
- [ ] Performance metrics acceptable

### Production

- [ ] Startup configuration set
- [ ] Logging configured
- [ ] Monitoring in place
- [ ] Documentation updated

### Post-Deployment

- [ ] User training completed
- [ ] Support contacts documented
- [ ] Rollback plan documented
- [ ] Backup schedule established

---

## Support

For issues during deployment:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review logs in `logs/` directory
3. Run diagnostics: `python run_gerald.py --diagnose`
4. Create GitHub issue with logs and system info

---

**Deployment Guide Version**: 1.0.0
**Last Updated**: 2025-11-22
**Tested On**: Windows 10 (21H2), Windows 11 (22H2)

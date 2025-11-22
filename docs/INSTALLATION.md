# Gerald Desktop Manager - Installation Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Model Downloads](#model-downloads)
5. [First Run Setup](#first-run-setup)
6. [Configuration](#configuration)
7. [Troubleshooting Installation](#troubleshooting-installation)
8. [Uninstallation](#uninstallation)

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (64-bit) or Windows 11
- **Processor**: Intel Core i5 or AMD Ryzen 5 (4 cores)
- **RAM**: 8GB
- **Disk Space**: 30GB free space (25GB for models, 5GB for runtime)
- **Microphone**: Any USB or built-in microphone
- **Webcam**: Optional (required only for face recognition)
- **Internet**: Required only for initial model downloads

### Recommended Requirements
- **Processor**: Intel Core i7 or AMD Ryzen 7 (6+ cores)
- **RAM**: 16GB
- **Disk**: SSD with 40GB+ free space
- **GPU**: Optional (future versions may support GPU acceleration)

### Software Requirements
- **Python**: 3.10, 3.11, or 3.12 (64-bit)
- **Microsoft Visual C++ Redistributable**: 2015-2022 (x64)
- **Windows Media Feature Pack**: (for TTS on Windows N/KN editions)

---

## Prerequisites

### 1. Install Python 3.10+

**Option A: Download from python.org (Recommended)**
1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or later (64-bit)
3. Run installer
4. **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"

**Option B: Using Winget (Windows 11)**
```bash
winget install Python.Python.3.11
```

**Verify installation:**
```bash
python --version
# Should show: Python 3.10.x or later
```

### 2. Install Microsoft Visual C++ Redistributable

Download and install from:
https://aka.ms/vs/17/release/vc_redist.x64.exe

This is required for:
- `dlib` (face recognition)
- `pyaudio` (audio capture)
- Some LLM libraries

### 3. Install Git (Optional, for cloning)

Download from: https://git-scm.com/download/win

Or using Winget:
```bash
winget install Git.Git
```

---

## Installation Steps

### Step 1: Download Gerald

**Option A: Clone with Git**
```bash
git clone https://github.com/yourusername/gerald-desktop-manager.git
cd gerald-desktop-manager
```

**Option B: Download ZIP**
1. Download ZIP from GitHub releases
2. Extract to desired location (e.g., `C:\Gerald`)
3. Open Command Prompt in that folder

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Command Prompt:
venv\Scripts\activate.bat

# On PowerShell:
venv\Scripts\Activate.ps1

# If PowerShell gives execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` prefix in your terminal.

### Step 3: Install Dependencies

Install dependencies for each service:

```bash
# Install ASR Service dependencies
pip install -r services/asr_service/requirements.txt

# Install LLM Service dependencies
pip install -r services/llm_service/requirements.txt

# Install Command Service dependencies
pip install -r services/command_service/requirements.txt

# Install testing dependencies (optional)
pip install -r tests/requirements.txt
```

**Note**: Installation may take 10-20 minutes depending on internet speed.

**Common Issues**:
- If `pyaudio` fails, see [Troubleshooting](#troubleshooting-installation)
- If `dlib` fails, install CMake first: `pip install cmake`

### Step 4: Download AI Models

Gerald requires several AI models to operate offline:

```bash
python setup_models.py
```

This will download (~25GB total):
- ✓ Vosk ASR model (English) - ~100MB
- ✓ Vosk ASR model (Russian) - ~100MB
- ✓ Phi-3-mini LLM model - ~2.3GB
- ✓ Face recognition models - ~10MB
- ✓ Voice biometrics models - ~50MB
- ✓ Additional dependencies - ~100MB

**Download time**: 30-60 minutes on average internet connection.

**Note**: Models are stored in `shared/models/` directory.

### Step 5: Verify Installation

Run health checks for all services:

```bash
python -m services.asr_service.src.main --check
python -m services.llm_service.src.main --check
python -m services.command_service.src.main --check
```

All should show: ✓ Service ready

---

## Model Downloads

### What Gets Downloaded

#### 1. ASR Models (Vosk)
```
shared/models/asr/
├── vosk-model-small-en-us-0.15/    (~100MB)
│   └── [ASR model files]
└── vosk-model-small-ru-0.22/       (~100MB)
    └── [ASR model files]
```

**Source**: https://alphacephei.com/vosk/models

#### 2. LLM Model
```
shared/models/llm/
└── phi-3-mini-4k-instruct-q4.gguf  (~2.3GB)
```

**Source**: https://huggingface.co/ (via llama.cpp)

**Alternative models** (can choose during setup):
- `gemma-2-2b-it-q4.gguf` (~1.5GB) - Faster, less capable
- `tinyllama-1.1b-chat-q4.gguf` (~637MB) - Fastest, minimal quality

#### 3. Face Recognition Models
```
shared/models/face/
└── shape_predictor_68_face_landmarks.dat (~10MB)
```

**Source**: dlib model repository

#### 4. Voice Biometrics Models
```
shared/models/voice/
└── [SpeechBrain speaker recognition models] (~50MB)
```

**Source**: SpeechBrain Hub

### Manual Download (if automated fails)

If `setup_models.py` fails, download manually:

1. **Vosk English**:
   - URL: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   - Extract to: `shared/models/asr/vosk-model-small-en-us-0.15/`

2. **Vosk Russian**:
   - URL: https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
   - Extract to: `shared/models/asr/vosk-model-small-ru-0.22/`

3. **Phi-3-mini**:
   - Use huggingface-cli:
     ```bash
     pip install huggingface-hub
     huggingface-cli download microsoft/Phi-3-mini-4k-instruct-gguf \
       phi-3-mini-4k-instruct-q4.gguf \
       --local-dir shared/models/llm/
     ```

---

## First Run Setup

### 1. Launch Gerald

```bash
python run_gerald.py
```

Or on Windows, double-click: `run_gerald.bat`

### 2. First-Time Configuration Wizard

Gerald will guide you through setup:

```
╔════════════════════════════════════════════════╗
║  Welcome to Gerald Desktop Manager v1.0.0     ║
╚════════════════════════════════════════════════╝

First-time setup detected. Let's configure Gerald.

[1/5] Select Language
  1. English
  2. Русский (Russian)
Choice [1]: 1

[2/5] Test Microphone
Speak into your microphone: "Testing, one, two, three"
✓ Microphone working! Detected: "testing one two three"

[3/5] Test Speakers
Playing test sound...
Did you hear Gerald's voice? (yes/no): yes
✓ Speakers working!

[4/5] Face Recognition (Optional)
Enable face recognition? (yes/no): yes
  → Look at your webcam
  → Smile naturally
  → Hold still for 3 seconds...
✓ Face enrolled! Welcome, User.

[5/5] Startup Options
Launch Gerald with Windows? (yes/no): yes
✓ Auto-start enabled.

Setup complete! Gerald is ready to serve.
```

### 3. Verify Services

After first run, check that all services are running:

```bash
# Check ASR Service
curl http://localhost:8001/health
# Should return: {"status": "healthy"}

# Check LLM Service
curl http://localhost:8002/health
# Should return: {"status": "healthy"}

# Check Command Service
curl http://localhost:8003/health
# Should return: {"status": "healthy"}
```

---

## Configuration

### Main Configuration File

Edit `config/main_config.yaml`:

```yaml
# Application Settings
app:
  name: "Gerald Desktop Manager"
  version: "1.0.0"
  character: "gerald"           # Change to switch characters
  default_language: "en"        # "en" or "ru"
  auto_start: true              # Launch with Windows
  log_level: "INFO"             # DEBUG, INFO, WARNING, ERROR

# Performance Settings
performance:
  max_cpu_percent: 5            # Max CPU when idle
  max_memory_mb: 4096           # Max memory usage
  optimize_for: "cpu"           # "cpu" or "memory"

# Privacy Settings
privacy:
  store_user_features: true     # Store face/voice data
  encrypt_data: false           # Encrypt user database
```

### ASR Configuration

Edit ASR settings if needed:

```yaml
asr:
  vad:
    threshold: 0.5              # Lower = more sensitive (0.0-1.0)
    min_speech_duration_ms: 250

  audio:
    sample_rate: 16000          # Don't change (Vosk requirement)
    channels: 1                 # Mono audio

  tts:
    rate: 180                   # Speech rate (words per minute)
    volume: 0.9                 # Volume (0.0-1.0)
```

### LLM Configuration

Edit LLM settings:

```yaml
llm:
  model: "phi-3-mini"           # or "gemma-2-2b", "tinyllama-1.1b"

  inference:
    temperature: 0.7            # Creativity (0.0-1.0)
    max_tokens: 100             # Max response length
```

### Command Safety Configuration

Edit safety rules:

```yaml
commands:
  safety:
    confirmation_required:
      - file_delete
      - terminal_command
      - registry_modify

    forbidden_patterns:
      - "format *"
      - "del /s /q C:\\"
```

---

## Troubleshooting Installation

### Issue: `pip install` fails with "error: Microsoft Visual C++ 14.0 is required"

**Solution**: Install Visual C++ Redistributable (see Prerequisites)

### Issue: `pyaudio` installation fails

**Solution 1**: Install precompiled wheel
```bash
pip install pipwin
pipwin install pyaudio
```

**Solution 2**: Use sounddevice instead
Edit `services/asr_service/src/audio_capture.py` to use sounddevice

### Issue: `dlib` installation fails

**Solution**: Install CMake first
```bash
pip install cmake
pip install dlib
```

Or use precompiled wheel:
```bash
pip install dlib-19.24.0-cp311-cp311-win_amd64.whl
```

### Issue: Models fail to download

**Solutions**:
1. Check internet connection
2. Disable VPN/proxy temporarily
3. Download models manually (see [Manual Download](#manual-download-if-automated-fails))
4. Check disk space (need 30GB free)

### Issue: "Port already in use" error

**Solution**: Another service using ports 8001-8003
```bash
# Find process using port
netstat -ano | findstr :8001

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Issue: Microphone not detected

**Solutions**:
1. Check Windows Privacy Settings:
   - Settings → Privacy → Microphone
   - Enable "Allow apps to access microphone"
   - Enable for Python/Terminal

2. Check device manager:
   - Ensure microphone is enabled
   - Update audio drivers

3. Test microphone:
   - Open Windows Sound Recorder
   - Record test clip

### Issue: TTS not working on Windows N/KN editions

**Solution**: Install Media Feature Pack
- Windows 10 N/KN: https://www.microsoft.com/en-us/software-download/mediafeaturepack
- Windows 11 N/KN: Settings → Apps → Optional features → Add "Media Feature Pack"

### Issue: High CPU usage

**Solutions**:
1. Reduce VAD sensitivity in config:
   ```yaml
   asr:
     vad:
       threshold: 0.7  # Increase from 0.5
   ```

2. Use smaller LLM model:
   ```yaml
   llm:
     model: "gemma-2-2b"  # Instead of phi-3-mini
   ```

### Issue: Python not found in PATH

**Solution**: Add Python to PATH manually
1. Find Python installation path (e.g., `C:\Python311\`)
2. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Edit "Path" under User variables
   - Add: `C:\Python311\` and `C:\Python311\Scripts\`

---

## Startup with Windows

### Enable Auto-Start

**Method 1**: During first-run setup (choose "yes")

**Method 2**: Edit configuration
```yaml
# config/main_config.yaml
app:
  auto_start: true
```
Then restart Gerald.

**Method 3**: Manual registry/startup folder
```bash
# Run this to add to startup folder
python -c "import os, shutil; shutil.copy('run_gerald.bat', os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'))"
```

### Disable Auto-Start

**Method 1**: Edit configuration
```yaml
app:
  auto_start: false
```

**Method 2**: Remove from startup folder
```bash
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\run_gerald.bat"
```

---

## Updating Gerald

### Update to Latest Version

```bash
# If using Git
git pull origin main

# Reinstall dependencies
pip install -r services/asr_service/requirements.txt --upgrade
pip install -r services/llm_service/requirements.txt --upgrade
pip install -r services/command_service/requirements.txt --upgrade

# Update models if needed
python setup_models.py --update
```

---

## Uninstallation

### Complete Removal

1. **Stop Gerald** (if running):
   ```bash
   # Say "Exit Gerald" or:
   taskkill /IM python.exe /F
   ```

2. **Disable auto-start** (if enabled):
   ```bash
   del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\run_gerald.bat"
   ```

3. **Remove user data** (optional):
   ```bash
   del shared\user_data.db
   ```

4. **Delete Gerald folder**:
   ```bash
   cd ..
   rmdir /s /q gerald-desktop-manager
   ```

5. **Uninstall Python** (if installed only for Gerald):
   - Control Panel → Programs → Uninstall Python

### Keep User Data

To keep face/voice enrollment data for reinstall:
1. Copy `shared/user_data.db` to safe location
2. After reinstalling, copy back to `shared/` folder

---

## Verification Checklist

After installation, verify everything works:

- [ ] Python 3.10+ installed and in PATH
- [ ] All dependencies installed without errors
- [ ] Models downloaded successfully (~25GB)
- [ ] ASR Service starts (port 8001)
- [ ] LLM Service starts (port 8002)
- [ ] Command Service starts (port 8003)
- [ ] Microphone detected and working
- [ ] Test command recognized: "Who are you?"
- [ ] Gerald responds via TTS
- [ ] Face recognition works (if enabled)
- [ ] Auto-start configured (if desired)

**Test Commands**:
1. "Who are you?" → Gerald introduces himself
2. "What time is it?" → Gerald tells current time
3. "Open Calculator" → Calculator launches
4. "Close Calculator" → Calculator closes

If all tests pass, installation is complete!

---

## Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) to learn all commands
- Read [COMMANDS.md](COMMANDS.md) for complete command reference
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues arise
- Join community (link to Discord/forum)

---

**Installation Support**: If you encounter issues not covered here, please:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Search existing GitHub issues
3. Create new issue with details

**Last Updated**: 2025-11-22
**Version**: 1.0.0

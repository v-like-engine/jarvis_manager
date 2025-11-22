# Gerald Desktop Manager - Quick Start Guide

Get Gerald up and running in 15 minutes!

## ⚡ Super Quick Start (For the Impatient)

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download models (first time only, ~2.5GB)
python setup_models.py

# 3. Start Gerald
python start_gerald.py
```

Then say: **"Who are you?"** to test!

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] **Windows 10/11** (64-bit)
- [ ] **Python 3.10+** installed
- [ ] **8GB RAM** minimum
- [ ] **30GB free disk space**
- [ ] **Microphone** (any USB or built-in mic)
- [ ] **Internet connection** (for initial setup only)

---

## 🚀 Step-by-Step Installation

### Step 1: Get the Code

**Option A: Download ZIP**
```powershell
# Download and extract to C:\Gerald\
# Then:
cd C:\Gerald\jarvis_manager
```

**Option B: Clone with Git**
```powershell
git clone <repository-url> C:\Gerald\jarvis_manager
cd C:\Gerald\jarvis_manager
```

### Step 2: Install Python Dependencies

```powershell
# Option 1: Install all at once
pip install -r requirements.txt

# Option 2: Install per service (more control)
pip install -r services/asr_service/requirements.txt
pip install -r services/llm_service/requirements.txt
pip install -r services/command_service/requirements.txt
```

**Estimated time**: 5-10 minutes

**Note**: If you see errors, you may need to install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Step 3: Download AI Models

```powershell
python setup_models.py
```

This downloads:
- ✅ Speech recognition models (English + Russian)
- ✅ Local language model (Phi-3-mini)
- ✅ Face recognition models
- ✅ Text-to-speech models

**Download size**: ~2.5GB
**Estimated time**: 10-30 minutes (depending on connection)

**Progress indicators**:
```
Downloading Vosk English model... ████████████ 100%
Downloading Vosk Russian model... ████████████ 100%
Downloading LLM model (Phi-3)...  ████████████ 100%
✅ All models downloaded successfully!
```

### Step 4: First Launch

```powershell
# Simple launcher (recommended for first time)
python start_gerald.py
```

**What happens**:
1. Services start (ASR, LLM, Command)
2. Microphone initialization
3. Gerald greets you
4. Ready for commands!

**Expected output**:
```
╔═══════════════════════════════════════════════════════════╗
║        🎙️  GERALD DESKTOP MANAGER 🖥️                     ║
║        Voice-Controlled Desktop Manager                   ║
╚═══════════════════════════════════════════════════════════╝

🚀 Starting Gerald Desktop Manager...
   Character: gerald
   Language: en

✅ ASR Service started (port 8001)
✅ LLM Service started (port 8002)
✅ Command Service started (port 8003)

🎤 Listening for commands...
Gerald: "Ready to serve, sir. Awaiting your orders."
```

---

## 🎤 Your First Voice Commands

### Test Gerald with These Commands

#### 1. Test Basic Response
**Say**: "Who are you?"

**Gerald**: "I am Gerald, your loyal desktop knight. I control your Windows machine by voice command. Speak your orders, and I shall execute them."

#### 2. Launch an Application
**Say**: "Open Notepad"

**Gerald**: "Opening Notepad, sir."
→ Notepad launches

#### 3. Close an Application
**Say**: "Close Notepad"

**Gerald**: "Closing Notepad. Done."
→ Notepad closes

#### 4. Ask for Help
**Say**: "What can you do?"

**Gerald**: "I can launch and close applications, manage files, control music, execute terminal commands, and much more. What would you like me to do?"

#### 5. Exit Gerald
**Say**: "Exit Gerald"

**Gerald**: "Shutting down. Farewell, sir."
→ Gerald stops

---

## 🎯 Essential Commands

### Application Control

| Command | Action |
|---------|--------|
| "Open Chrome" | Launch Google Chrome |
| "Open Notepad" | Launch Notepad |
| "Open Calculator" | Launch Calculator |
| "Close Chrome" | Close Chrome |

### System Commands

| Command | Action |
|---------|--------|
| "Who are you?" | Gerald introduces himself |
| "What can you do?" | Lists capabilities |
| "Change language" | Switch English/Russian |
| "Exit Gerald" | Shutdown Gerald |

### Music Control

| Command | Action |
|---------|--------|
| "Play music" | Play/resume |
| "Pause" | Pause playback |
| "Next track" | Skip to next |
| "Volume up" | Increase volume |

### File Operations

| Command | Action |
|---------|--------|
| "Create folder test" | Create new folder |
| "Delete file test.txt" | Delete file (asks confirmation) |

---

## 🇷🇺 Russian Commands

Gerald speaks Russian too! Switch with: **"Change language"**

### Basic Russian Commands

| Russian | English | Action |
|---------|---------|--------|
| "Кто ты?" | "Who are you?" | Introduction |
| "Открой Хром" | "Open Chrome" | Launch Chrome |
| "Закрой Хром" | "Close Chrome" | Close Chrome |
| "Играй музыку" | "Play music" | Play music |
| "Выключись" | "Exit Gerald" | Shutdown |

**Switch back to English**: "Change language" (works in any language)

---

## ⚙️ Basic Configuration

### Change Default Language

Edit `config/main_config.yaml`:

```yaml
gerald:
  default_language: "ru"  # Change to "ru" for Russian
```

### Change Character

```yaml
gerald:
  character: "winnie_pooh"  # Change to Winnie Pooh (gentle bear)
```

Available characters:
- `gerald` - Loyal knight (strict, direct)
- `winnie_pooh` - Gentle bear (kind, philosophical)

### Auto-Start with Windows

```powershell
# Enable
python run_gerald.py --enable-startup

# Disable
python run_gerald.py --disable-startup
```

---

## 🔧 Troubleshooting Quick Fixes

### Problem: "Models not found"

**Solution**:
```powershell
python setup_models.py
```

### Problem: "Microphone not working"

**Solution**:
```powershell
# 1. Check Windows sound settings
ms-settings:sound

# 2. Test microphone
python -c "import pyaudio; p = pyaudio.PyAudio(); print(f'Microphones: {p.get_device_count()}')"

# 3. Grant microphone permission
# Windows Settings → Privacy → Microphone → Allow apps
```

### Problem: "Service won't start"

**Solution**:
```powershell
# Check if ports are in use
netstat -ano | findstr "8001 8002 8003"

# Kill processes on those ports
taskkill /F /PID <pid>

# Restart Gerald
python start_gerald.py
```

### Problem: "Gerald doesn't understand me"

**Solution**:
1. Speak clearly and at normal pace
2. Use exact command phrases (see [COMMANDS.md](COMMANDS.md))
3. Check microphone is not muted
4. Reduce background noise
5. Move closer to microphone

### Problem: "Python not found"

**Solution**:
```powershell
# Install Python from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Verify installation
python --version
```

---

## 📚 Next Steps

Now that Gerald is running, explore more:

1. **Learn More Commands**: See [COMMANDS.md](COMMANDS.md) for full list (182 commands!)
2. **Configure Gerald**: See [USER_GUIDE.md](USER_GUIDE.md) for advanced configuration
3. **Enroll Your Face**: Say "Enroll my face" for face recognition
4. **Customize Voice**: Edit character settings in `services/llm_service/characters/`
5. **Run as Service**: See [WINDOWS_SERVICE.md](WINDOWS_SERVICE.md) for always-on setup

---

## 🎓 Understanding Gerald

### How It Works

```
1. You speak → 2. Gerald hears → 3. Understands → 4. Executes → 5. Responds

┌─────────────┐
│ You speak   │
│ "Open Note" │
└─────┬───────┘
      │
      v
┌─────────────────┐
│ ASR Service     │ ← Vosk speech recognition
│ Converts speech │
│ to text         │
└─────┬───────────┘
      │
      v
┌─────────────────┐
│ LLM Service     │ ← Gerald's brain (Phi-3)
│ Understands     │
│ intent & checks │
│ safety          │
└─────┬───────────┘
      │
      v
┌─────────────────┐
│ Command Service │ ← Executes command
│ Opens Notepad   │
└─────┬───────────┘
      │
      v
┌─────────────────┐
│ Gerald speaks   │ ← Text-to-speech
│ "Opening Note"  │
└─────────────────┘
```

### 3 Main Components

1. **ASR Service** (Port 8001): Speech recognition, TTS, face/voice ID
2. **LLM Service** (Port 8002): Gerald's personality and intelligence
3. **Command Service** (Port 8003): Executes commands on Windows

All run locally - **no internet needed** after setup!

---

## 💡 Pro Tips

### Tip 1: Use Wake Word (Future)
Currently, Gerald is always listening. Future version will support custom wake word like "Hey Gerald"

### Tip 2: Command Chaining (Future)
Soon you'll be able to chain commands: "Open Chrome and navigate to YouTube"

### Tip 3: Custom Commands (Future)
Create your own voice commands using the command framework

### Tip 4: Use Simple Launcher
```powershell
# Best for beginners
python start_gerald.py

# Advanced options
python run_gerald.py --character winnie_pooh --debug
```

### Tip 5: Check Logs
```powershell
# If something goes wrong
type logs\asr_service.log
type logs\llm_service.log
type logs\command_service.log
```

---

## 🆘 Getting Help

### Quick Help

```powershell
# Show help
python start_gerald.py --help

# Show command reference
python start_gerald.py --help-commands
```

### Documentation

- 📖 [Full User Guide](USER_GUIDE.md)
- 📋 [Complete Command List](COMMANDS.md)
- 🏗️ [Architecture](ARCHITECTURE.md)
- 🔧 [Troubleshooting](TROUBLESHOOTING.md)
- ⚙️ [Installation Guide](INSTALLATION.md)

### Support Channels

- GitHub Issues: [Report a bug]
- Documentation: `docs/` folder
- Logs: `logs/` folder

---

## ✅ Quick Start Checklist

- [ ] Windows 10/11 with Python 3.10+ installed
- [ ] Cloned/downloaded repository
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Downloaded models (`python setup_models.py`)
- [ ] Started Gerald (`python start_gerald.py`)
- [ ] Tested voice command ("Who are you?")
- [ ] Launched an application ("Open Notepad")
- [ ] Explored command list ([COMMANDS.md](COMMANDS.md))
- [ ] Configured settings (optional)
- [ ] Set up auto-start (optional)

---

## 🎉 You're Ready!

Gerald is now ready to serve as your voice-controlled desktop assistant.

**Say**: "Who are you?" to begin!

For more commands and features, see the [complete documentation](README.md).

**Have fun controlling your PC by voice!** 🎙️⚔️

---

**Quick Start Guide Version**: 1.0.0
**Last Updated**: 2025-11-22
**Difficulty**: Beginner-Friendly

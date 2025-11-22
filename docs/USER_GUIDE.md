# Gerald Desktop Manager - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Basic Commands](#basic-commands)
4. [Application Control](#application-control)
5. [File Operations](#file-operations)
6. [Terminal Commands](#terminal-commands)
7. [Music Control](#music-control)
8. [User Recognition](#user-recognition)
9. [Settings & Configuration](#settings--configuration)
10. [Language Switching](#language-switching)
11. [Safety & Confirmations](#safety--confirmations)
12. [Tips & Best Practices](#tips--best-practices)
13. [FAQ](#faq)

---

## Introduction

Welcome to Gerald, your voice-controlled desktop manager! Gerald is an AI assistant that responds to your voice commands to control your Windows computer. Think of Gerald as a loyal knight - strict, helpful, direct, and always ready to serve.

### What Gerald Can Do
- Launch and close applications
- Create, delete, and manage files and folders
- Execute terminal commands
- Control music playback
- Recognize users by face or voice
- Respond in English or Russian
- Protect you from dangerous operations

### What Makes Gerald Special
- **100% Offline**: No internet required after setup
- **Bilingual**: Speaks English and Russian fluently
- **Safe**: Asks confirmation for dangerous operations
- **Fast**: Responds in under 2 seconds
- **Private**: Your data never leaves your computer
- **Efficient**: Uses less than 5% CPU when idle

---

## Getting Started

### Starting Gerald

**Method 1: Run script**
```bash
python run_gerald.py
```

**Method 2: Batch file (Windows)**
Double-click: `run_gerald.bat`

**Method 3: Auto-start**
If enabled, Gerald starts automatically with Windows.

### First Launch

On first launch, you'll see:
```
╔════════════════════════════════════════════════╗
║     Gerald Desktop Manager v1.0.0             ║
║     Voice Assistant Ready                     ║
╚════════════════════════════════════════════════╝

Initializing services...
✓ ASR Service ready
✓ LLM Service ready
✓ Command Service ready

Listening... (Say "Hey Gerald" to activate)
```

### Activating Gerald

Gerald is always listening for the wake word:

**Wake Words**:
- "Hey Gerald" (English)
- "Gerald" (English)
- "Джеральд" (Russian)
- "Привет Джеральд" (Russian)

After wake word, speak your command.

**Example**:
```
You: "Hey Gerald"
Gerald: "Yes?" (beep sound)
You: "Open Chrome"
Gerald: "Chrome is ready" (launches browser)
```

### Stopping Gerald

**Voice Command**:
- "Exit Gerald"
- "Shutdown Gerald"
- "Close Gerald"
- "Выключись" (Russian)

**Keyboard**:
- Press `Ctrl+C` in terminal
- Close terminal window

---

## Basic Commands

### Information Commands

#### Ask About Gerald
```
English:
- "Who are you?"
- "Tell me about yourself"
- "What can you do?"

Russian:
- "Кто ты?"
- "Расскажи о себе"
- "Что ты умеешь?"

Gerald responds with his identity and capabilities.
```

#### Get Current Time
```
English:
- "What time is it?"
- "Tell me the time"

Russian:
- "Сколько времени?"
- "Который час?"

Example response: "It's 3:45 PM"
```

#### Get Current Date
```
English:
- "What's the date?"
- "What day is it?"

Russian:
- "Какое сегодня число?"
- "Какая сегодня дата?"

Example response: "Today is November 22nd, 2025"
```

### System Information

```
English:
- "How much memory are you using?"
- "What's your CPU usage?"
- "Show system stats"

Russian:
- "Сколько памяти используешь?"
- "Какая загрузка процессора?"

Gerald reports current resource usage.
```

---

## Application Control

### Launching Applications

Gerald can launch any installed application by name.

**Syntax**:
```
English:
- "Open <app name>"
- "Launch <app name>"
- "Start <app name>"
- "Run <app name>"

Russian:
- "Открой <app name>"
- "Запусти <app name>"
- "Включи <app name>"
```

**Examples**:
```
"Open Yandex Browser"
"Launch Chrome"
"Start Visual Studio Code"
"Run Calculator"
"Open Notepad"
"Launch Spotify"
"Start Word"
"Open Excel"
```

**Russian Examples**:
```
"Открой Яндекс браузер"
"Запусти Chrome"
"Открой Калькулятор"
```

### Fuzzy Matching

Gerald uses fuzzy matching, so you don't need exact names:

| You Say | Gerald Launches |
|---------|-----------------|
| "Open Chrome" | Google Chrome |
| "Launch VS Code" | Visual Studio Code |
| "Start Word" | Microsoft Word |
| "Open Yandex" | Yandex Browser |
| "Run Calculator" | Calculator |

### Closing Applications

**Syntax**:
```
English:
- "Close <app name>"
- "Shut down <app name>"
- "Exit <app name>"
- "Kill <app name>"

Russian:
- "Закрой <app name>"
- "Выключи <app name>"
```

**Examples**:
```
"Close Chrome"
"Shut down Calculator"
"Exit Spotify"
```

**Russian Examples**:
```
"Закрой браузер"
"Выключи калькулятор"
```

### Application Not Found

If Gerald can't find the app:
```
Gerald: "I can't find that application. Did you mean Chrome?"
```

You can then:
- Say "Yes" to launch suggested app
- Say "No" and rephrase command
- Install the application first

---

## File Operations

### Creating Files

**Syntax**:
```
English:
- "Create a file named <filename>"
- "Create file <filename>"

Russian:
- "Создай файл <filename>"
```

**Examples**:
```
"Create a file named notes.txt"
"Create file shopping_list.txt"
```

Gerald creates file in current user's Documents folder by default.

### Creating Folders

**Syntax**:
```
English:
- "Create a folder named <foldername>"
- "Create directory <foldername>"
- "Make a folder <foldername>"

Russian:
- "Создай папку <foldername>"
```

**Examples**:
```
"Create a folder named Projects"
"Make a folder called Photos_2025"
```

### Deleting Files (Requires Confirmation)

**Syntax**:
```
English:
- "Delete file <filename>"
- "Remove file <filename>"

Russian:
- "Удали файл <filename>"
```

**Example Flow**:
```
You: "Delete file old_notes.txt"
Gerald: "This will permanently delete old_notes.txt. Confirm deletion?"
You: "Yes" or "Confirm"
Gerald: "File deleted"

OR

You: "No" or "Cancel"
Gerald: "Deletion cancelled"
```

### Deleting Folders (Requires Confirmation)

**Syntax**:
```
English:
- "Delete folder <foldername>"
- "Remove directory <foldername>"

Russian:
- "Удали папку <foldername>"
```

**Example Flow**:
```
You: "Delete folder temp"
Gerald: "This will delete folder temp and all contents. Are you sure?"
You: "Yes"
Gerald: "Folder deleted"
```

### File Safety

Gerald protects system files:
- Cannot delete files in `C:\Windows\`
- Cannot delete files in `C:\Program Files\`
- Cannot delete system files like `system32.dll`
- Always asks confirmation before deletion

---

## Terminal Commands

Gerald can execute Windows terminal commands.

### Running Commands (Requires Confirmation)

**Syntax**:
```
English:
- "Run command <command>"
- "Execute <command>"
- "Terminal <command>"

Russian:
- "Выполни команду <command>"
```

**Example Flow**:
```
You: "Run command ipconfig"
Gerald: "This will execute terminal command: ipconfig. Confirm?"
You: "Yes"
Gerald: (executes command)
         "Command output: [shows IP configuration]"
```

### Safe Commands (No Confirmation)

Some commands are pre-approved and don't require confirmation:
- `ipconfig` - Network configuration
- `ping <host>` - Network ping
- `whoami` - Current user
- `dir` - List directory
- `echo <text>` - Print text

**Example**:
```
You: "Run command whoami"
Gerald: (executes immediately)
         "Current user: DESKTOP\YourName"
```

### Dangerous Commands (Blocked)

Gerald blocks extremely dangerous commands:
- `format C:` - Would erase drive
- `del /s /q C:\` - Would delete all files
- `rm -rf /` - Would delete everything
- `reg delete HKLM` - Would corrupt registry

**Example**:
```
You: "Run command format C:"
Gerald: "I cannot execute this command. It would damage your system."
```

---

## Music Control

Control media playback in any music application (Spotify, YouTube, etc.)

### Play/Pause

```
English:
- "Play music"
- "Pause music"
- "Resume playback"
- "Stop music"

Russian:
- "Включи музыку"
- "Поставь на паузу"
- "Останови музыку"
```

### Next/Previous Track

```
English:
- "Next song"
- "Next track"
- "Previous song"
- "Previous track"

Russian:
- "Следующая песня"
- "Предыдущий трек"
```

### Volume Control

```
English:
- "Volume up"
- "Volume down"
- "Increase volume"
- "Decrease volume"
- "Mute"
- "Unmute"

Russian:
- "Громче"
- "Тише"
- "Выключи звук"
```

**Note**: Gerald controls system-wide media keys, so it works with any app (Spotify, VLC, YouTube in browser, etc.)

---

## User Recognition

### Face Recognition

Enroll your face so Gerald can identify you.

#### Enrolling Face

```
English:
- "Recognize me"
- "Enroll my face"
- "Remember my face"

Russian:
- "Запомни меня"
- "Запомни моё лицо"

Gerald: "Look at the camera. Smile naturally. Hold still..."
(Captures face)
Gerald: "Face enrolled. Welcome, <your name>."
```

#### Identifying User

```
English:
- "Who am I?"
- "Do you recognize me?"

Russian:
- "Кто я?"

Gerald: (looks at camera)
        "Welcome back, John" (if recognized)
        OR
        "I don't recognize you" (if not enrolled)
```

### Voice Recognition

Enroll your voice for additional security.

#### Enrolling Voice

```
English:
- "Enroll my voice"
- "Remember my voice"

Gerald: "Please say: The quick brown fox jumps over the lazy dog"
You: (repeat phrase)
Gerald: "Voice enrolled successfully"
```

#### Voice Identification

Automatic - Gerald recognizes your voice when you speak.

### Privacy Note

All face/voice data stored locally in `shared/user_data.db`. Never uploaded to cloud.

To delete your data:
```
"Delete my user data"
```

---

## Settings & Configuration

### Changing Settings

```
English:
- "Change setting <setting_name> to <value>"
- "Set <setting_name> to <value>"

Examples:
- "Change language to Russian"
- "Set auto-start to enabled"
- "Change voice speed to fast"
```

### Available Settings

| Setting | Values | Description |
|---------|--------|-------------|
| Language | en, ru | Interface language |
| Auto-start | enabled, disabled | Start with Windows |
| Voice speed | slow, normal, fast | TTS speed |
| Voice volume | 0-100 | TTS volume |
| VAD sensitivity | low, medium, high | Microphone sensitivity |

### Viewing Current Settings

```
"Show settings"
"What are my settings?"

Gerald: "Current settings:
- Language: English
- Auto-start: Enabled
- Voice speed: Normal"
```

---

## Language Switching

Gerald supports English and Russian with automatic detection.

### Auto-Detection (Default)

Gerald automatically detects which language you're speaking:
```
You: "Open Chrome" (English detected)
Gerald: "Chrome is ready"

You: "Открой калькулятор" (Russian detected)
Gerald: "Калькулятор готов"
```

### Manual Language Change

```
English:
- "Change language to Russian"
- "Switch to Russian"
- "Speak Russian"

Russian:
- "Смени язык на английский"
- "Переключись на английский"

Gerald confirms in new language:
"Language changed to Russian" / "Язык изменён на русский"
```

### Mixed Language Commands

Gerald handles mixed commands:
```
You: "Open Яндекс браузер"
Gerald: (understands intent, responds in detected primary language)
```

---

## Safety & Confirmations

### Confirmation Required

Gerald asks confirmation for:
1. **File Deletion**: Deleting any file or folder
2. **Terminal Commands**: Running commands (except whitelisted)
3. **System Changes**: Modifying registry, services
4. **Application Uninstall**: Uninstalling software

### Confirmation Flow

```
You: "Delete file important.txt"
Gerald: "This will permanently delete important.txt. Confirm?"
You: "Yes" / "Confirm" / "Do it" / "Proceed"
Gerald: (executes action)

OR

You: "No" / "Cancel" / "Stop" / "Nevermind"
Gerald: "Action cancelled"
```

### Absolutely Forbidden

Some commands are **never** executed, even with confirmation:
- Format system drives
- Delete Windows folder
- Delete critical system files
- Modify critical registry keys

```
You: "Delete folder Windows"
Gerald: "I cannot execute this command. It would damage your system."
```

### Safety Philosophy

Gerald follows these safety rules:
1. **Confirm before destruction** - All deletion requires confirmation
2. **Protect system integrity** - System files are protected
3. **Transparent communication** - Gerald explains what will happen
4. **Easy cancellation** - Just say "No" or "Cancel"
5. **Audit trail** - All actions logged (see `logs/commands.log`)

---

## Tips & Best Practices

### Speaking to Gerald

**DO**:
- ✓ Speak clearly and naturally
- ✓ Use simple, direct commands
- ✓ Wait for Gerald's response before next command
- ✓ Say wake word ("Hey Gerald") before each command

**DON'T**:
- ✗ Whisper or speak too quietly
- ✗ Speak too fast or mumble
- ✗ Give multiple commands in one sentence
- ✗ Interrupt Gerald while speaking

### Command Examples

**Good Commands** (Clear, Direct):
```
✓ "Open Chrome"
✓ "What time is it?"
✓ "Create folder Projects"
✓ "Next song"
```

**Confusing Commands** (Avoid):
```
✗ "Hey could you maybe open Chrome and also what time is it?"
✗ "Um, like, can you, uh, create a file?"
✗ "OPENCHROMEPLEASE" (too fast)
```

### Microphone Setup

For best results:
- Use USB microphone or good built-in mic
- Minimize background noise
- Position mic 6-12 inches from mouth
- Reduce fan noise, music, TV

### Performance Tips

To keep Gerald responsive:
- Close unnecessary applications
- Don't run heavy tasks while using Gerald
- Keep system memory available (>2GB free)
- Update Windows and drivers regularly

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Gerald doesn't hear me | Check mic volume, reduce background noise |
| Gerald misunderstands | Speak more clearly, use simpler words |
| Gerald is slow | Close other apps, check CPU usage |
| Gerald wrong language | Manually set language in config |

---

## FAQ

### Q: Does Gerald require internet?
**A**: No. After initial setup (model downloads), Gerald works 100% offline.

### Q: Can I use Gerald on laptop speakers/microphone?
**A**: Yes, but external USB mic recommended for better accuracy.

### Q: How private is my data?
**A**: Completely private. All voice/face data stored locally. Nothing uploaded to cloud.

### Q: Can I change Gerald's voice?
**A**: Yes. Edit `config/main_config.yaml` to adjust pitch, rate, and volume. Custom voices coming in future updates.

### Q: What if Gerald misunderstands me?
**A**: Say the command again more clearly, or manually type correction (future feature).

### Q: Can Gerald control applications that are already open?
**A**: Currently only launch/close. Window control (minimize, maximize) coming in future updates.

### Q: Does Gerald work with non-English applications?
**A**: Yes. Gerald can launch applications regardless of language.

### Q: Can I add custom commands?
**A**: Not yet in v1.0. Custom command framework planned for v1.1.

### Q: How do I update Gerald?
**A**: See [INSTALLATION.md](INSTALLATION.md#updating-gerald)

### Q: Can I use Gerald with dual monitors?
**A**: Yes. Gerald launches apps normally, which appear based on Windows settings.

### Q: What happens if I lose internet mid-command?
**A**: Nothing. Gerald doesn't use internet after setup.

### Q: Can multiple users use Gerald?
**A**: Yes. Each user can enroll face/voice. Gerald identifies users automatically.

### Q: How do I reset Gerald to defaults?
**A**: Delete `config/main_config.yaml` and restart. First-run wizard will appear.

### Q: Can I run Gerald on multiple computers?
**A**: Yes. Install separately on each computer. Settings don't sync.

### Q: Does Gerald support macOS or Linux?
**A**: Not yet. Windows only in v1.0. Cross-platform support planned for future.

---

## Getting Help

### Log Files

Check logs for errors:
- `logs/asr_service.log` - Voice recognition issues
- `logs/llm_service.log` - LLM errors
- `logs/command_service.log` - Command execution problems
- `logs/commands.log` - Audit trail of all commands

### Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

### Support

- **Documentation**: Check all `.md` files in `docs/` folder
- **GitHub Issues**: Report bugs or request features
- **Community**: (Discord/forum link)

---

## Next Steps

- Explore all commands in [COMMANDS.md](COMMANDS.md)
- Learn about architecture in [ARCHITECTURE.md](ARCHITECTURE.md)
- Contribute to project: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

**Enjoy using Gerald! May your desktop be forever under control.** ⚔️

**Last Updated**: 2025-11-22
**Version**: 1.0.0

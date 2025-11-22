# Gerald Desktop Manager - Voice Commands Reference

Complete bilingual (English/Russian) command reference for Gerald Desktop Manager v1.0.0

## Table of Contents
1. [Wake Words](#wake-words)
2. [System Commands](#system-commands)
3. [Application Control](#application-control)
4. [File Operations](#file-operations)
5. [Terminal Commands](#terminal-commands)
6. [Music Control](#music-control)
7. [User Recognition](#user-recognition)
8. [Settings & Configuration](#settings--configuration)
9. [Information Queries](#information-queries)
10. [Confirmation Responses](#confirmation-responses)

---

## Command Legend

| Symbol | Meaning |
|--------|---------|
| `<app>` | Application name (e.g., "Chrome", "Calculator") |
| `<file>` | File name (e.g., "notes.txt") |
| `<folder>` | Folder/directory name |
| `<command>` | Terminal command |
| `<setting>` | Setting name |
| `<value>` | Setting value |
| 🔒 | Requires confirmation |
| ⛔ | Blocked for safety |
| ⚡ | Instant execution |

---

## Wake Words

Gerald listens for wake words to know you're addressing him. Say wake word before each command.

### English Wake Words
```
• "Hey Gerald"
• "Gerald"
• "OK Gerald"
• "Hey Gerald, ..."  (wake + command in one)
```

### Russian Wake Words
```
• "Джеральд"
• "Привет Джеральд"
• "Эй Джеральд"
```

**Example Usage**:
```
You: "Hey Gerald"
Gerald: *beep* (ready)
You: "Open Chrome"

OR

You: "Hey Gerald, open Chrome" (combined)
```

---

## System Commands

### Gerald Self-Control

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Exit Gerald | Выключись | Shutdown Gerald | ⚡ |
| Shutdown Gerald | Выключи Gerald | Shutdown Gerald | ⚡ |
| Close Gerald | Закрой Gerald | Shutdown Gerald | ⚡ |
| Restart Gerald | Перезапусти Gerald | Restart all services | 🔒 |
| Sleep Gerald | Спящий режим | Pause listening | ⚡ |
| Wake up Gerald | Проснись | Resume listening | ⚡ |

### Gerald Identity

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Who are you? | Кто ты? | Gerald introduces himself | ⚡ |
| Tell me about yourself | Расскажи о себе | Gerald describes capabilities | ⚡ |
| What can you do? | Что ты умеешь? | List capabilities | ⚡ |
| What's your name? | Как тебя зовут? | Gerald states his name | ⚡ |

---

## Application Control

### Launch Applications

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Open `<app>` | Открой `<app>` | Launch application | ⚡ |
| Launch `<app>` | Запусти `<app>` | Launch application | ⚡ |
| Start `<app>` | Включи `<app>` | Launch application | ⚡ |
| Run `<app>` | Запусти программу `<app>` | Launch application | ⚡ |

**Examples**:
```
English:
• "Open Chrome"
• "Launch Visual Studio Code"
• "Start Calculator"
• "Run Notepad"
• "Open Yandex Browser"
• "Launch Spotify"
• "Start Word"
• "Open Excel"

Russian:
• "Открой Chrome"
• "Запусти Калькулятор"
• "Включи Блокнот"
• "Открой Яндекс браузер"
• "Запусти Spotify"
```

### Close Applications

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Close `<app>` | Закрой `<app>` | Close application | ⚡ |
| Shut down `<app>` | Выключи `<app>` | Close application | ⚡ |
| Exit `<app>` | Выйди из `<app>` | Close application | ⚡ |
| Kill `<app>` | Убей `<app>` | Force close application | 🔒 |

**Examples**:
```
English:
• "Close Chrome"
• "Shut down Calculator"
• "Exit Notepad"
• "Kill unresponsive app"

Russian:
• "Закрой браузер"
• "Выключи калькулятор"
• "Выйди из блокнота"
```

### Common Applications (Fuzzy Match Support)

Gerald recognizes these applications with fuzzy matching:

| App Category | Application Names |
|--------------|-------------------|
| **Browsers** | Chrome, Firefox, Edge, Yandex Browser, Opera, Brave |
| **Office** | Word, Excel, PowerPoint, Outlook, OneNote |
| **Development** | Visual Studio Code, VS Code, PyCharm, IntelliJ, Sublime Text |
| **Media** | VLC, Spotify, iTunes, Windows Media Player, Audacity |
| **Utilities** | Calculator, Notepad, Paint, Snipping Tool, Task Manager |
| **Communication** | Skype, Teams, Discord, Slack, Zoom |
| **Graphics** | Photoshop, GIMP, Illustrator, Inkscape |

**Fuzzy Match Examples**:
```
You say: "Open VS Code"    → Launches: Visual Studio Code
You say: "Start Calc"      → Launches: Calculator
You say: "Run Chrome"      → Launches: Google Chrome
You say: "Open Yandex"     → Launches: Yandex Browser
```

---

## File Operations

### Create Files

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Create file `<file>` | Создай файл `<file>` | Create new file | ⚡ |
| Create a file named `<file>` | Создай файл с именем `<file>` | Create new file | ⚡ |
| Make file `<file>` | Сделай файл `<file>` | Create new file | ⚡ |

**Examples**:
```
English:
• "Create file notes.txt"
• "Create a file named shopping_list.txt"
• "Make file todo.txt"

Russian:
• "Создай файл заметки.txt"
• "Создай файл список_покупок.txt"
```

**Default Location**: User's Documents folder

### Create Folders

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Create folder `<folder>` | Создай папку `<folder>` | Create new folder | ⚡ |
| Create directory `<folder>` | Создай директорию `<folder>` | Create new folder | ⚡ |
| Make folder `<folder>` | Сделай папку `<folder>` | Create new folder | ⚡ |

**Examples**:
```
English:
• "Create folder Projects"
• "Create directory Photos_2025"
• "Make folder Work"

Russian:
• "Создай папку Проекты"
• "Создай папку Фото_2025"
```

### Delete Files

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Delete file `<file>` | Удали файл `<file>` | Delete file | 🔒 |
| Remove file `<file>` | Убери файл `<file>` | Delete file | 🔒 |
| Erase file `<file>` | Стереть файл `<file>` | Delete file | 🔒 |

**Confirmation Required**: Yes

**Example Flow**:
```
You: "Delete file old_notes.txt"
Gerald: "This will permanently delete old_notes.txt. Confirm deletion?"
You: "Yes"
Gerald: "File deleted"
```

### Delete Folders

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Delete folder `<folder>` | Удали папку `<folder>` | Delete folder and contents | 🔒 |
| Remove directory `<folder>` | Убери директорию `<folder>` | Delete folder and contents | 🔒 |

**Confirmation Required**: Yes

**Protected Locations** (Cannot Delete):
- `C:\Windows\`
- `C:\Program Files\`
- `C:\Program Files (x86)\`
- User profile folders (Desktop, Documents, etc.)

---

## Terminal Commands

### Execute Commands

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Run command `<command>` | Выполни команду `<command>` | Execute terminal command | 🔒 |
| Execute `<command>` | Исполни `<command>` | Execute terminal command | 🔒 |
| Terminal `<command>` | Терминал `<command>` | Execute terminal command | 🔒 |
| Command prompt `<command>` | Командная строка `<command>` | Execute terminal command | 🔒 |

**Confirmation Required**: Yes (except whitelisted)

### Whitelisted Commands (No Confirmation)

These safe commands execute immediately:

| Command | Description | Example |
|---------|-------------|---------|
| `ipconfig` | Network configuration | "Run command ipconfig" |
| `ping <host>` | Network ping | "Run command ping google.com" |
| `whoami` | Current user | "Run command whoami" |
| `dir` | List directory | "Run command dir" |
| `echo <text>` | Print text | "Run command echo hello" |
| `hostname` | Computer name | "Run command hostname" |
| `systeminfo` | System information | "Run command systeminfo" |

### Forbidden Commands (Never Execute)

These commands are **absolutely blocked**:

| Pattern | Reason |
|---------|--------|
| `format *` | Would erase drives |
| `del /s /q C:\` | Would delete all files |
| `rm -rf /` | Would delete everything |
| `reg delete HKLM` | Would corrupt registry |
| `rd /s /q C:\Windows` | Would delete Windows |

**Example**:
```
You: "Run command format C:"
Gerald: "I cannot execute this command. It would damage your system."
```

---

## Music Control

### Playback Control

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Play music | Включи музыку | Play/Resume | ⚡ |
| Pause music | Поставь на паузу | Pause | ⚡ |
| Stop music | Останови музыку | Stop | ⚡ |
| Resume playback | Продолжи воспроизведение | Resume | ⚡ |
| Play | Играй | Play | ⚡ |
| Pause | Пауза | Pause | ⚡ |

### Track Navigation

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Next song | Следующая песня | Skip to next track | ⚡ |
| Next track | Следующий трек | Skip to next track | ⚡ |
| Skip | Пропусти | Skip to next track | ⚡ |
| Previous song | Предыдущая песня | Previous track | ⚡ |
| Previous track | Предыдущий трек | Previous track | ⚡ |
| Go back | Назад | Previous track | ⚡ |

### Volume Control

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Volume up | Громче | Increase volume | ⚡ |
| Louder | Увеличь громкость | Increase volume | ⚡ |
| Increase volume | Прибавь звук | Increase volume | ⚡ |
| Volume down | Тише | Decrease volume | ⚡ |
| Quieter | Уменьши громкость | Decrease volume | ⚡ |
| Decrease volume | Убавь звук | Decrease volume | ⚡ |
| Mute | Выключи звук | Mute audio | ⚡ |
| Unmute | Включи звук | Unmute audio | ⚡ |

**Note**: Works with any media application (Spotify, YouTube, VLC, etc.)

---

## User Recognition

### Face Recognition

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Recognize me | Узнай меня | Identify user by face | ⚡ |
| Who am I? | Кто я? | Identify user by face | ⚡ |
| Enroll my face | Запомни моё лицо | Enroll face | ⚡ |
| Remember my face | Запомни меня | Enroll face | ⚡ |
| Forget my face | Забудь моё лицо | Delete face data | 🔒 |

**Enrollment Flow**:
```
You: "Enroll my face"
Gerald: "Look at the camera. Smile naturally. Hold still..."
(Captures face)
Gerald: "Face enrolled. Welcome, User."
```

### Voice Recognition

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Enroll my voice | Запомни мой голос | Enroll voice | ⚡ |
| Remember my voice | Запомни меня по голосу | Enroll voice | ⚡ |
| Forget my voice | Забудь мой голос | Delete voice data | 🔒 |

**Enrollment Flow**:
```
You: "Enroll my voice"
Gerald: "Please say: The quick brown fox jumps over the lazy dog"
You: (repeat phrase)
Gerald: "Voice enrolled successfully"
```

### User Data

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Delete my data | Удали мои данные | Delete all user data | 🔒 |
| Clear my profile | Очисти мой профиль | Delete user profile | 🔒 |
| Show my profile | Покажи мой профиль | Display user info | ⚡ |

---

## Settings & Configuration

### Language Settings

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Change language to English | Смени язык на английский | Switch to English | ⚡ |
| Change language to Russian | Смени язык на русский | Switch to Russian | ⚡ |
| Switch to English | Переключись на английский | Switch to English | ⚡ |
| Switch to Russian | Переключись на русский | Switch to Russian | ⚡ |
| Speak English | Говори по-английски | Switch to English | ⚡ |
| Speak Russian | Говори по-русски | Switch to Russian | ⚡ |

### Startup Settings

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Enable auto-start | Включи автозапуск | Start with Windows | ⚡ |
| Disable auto-start | Выключи автозапуск | Don't start with Windows | ⚡ |
| Start with Windows | Запускайся с Windows | Enable auto-start | ⚡ |

### Voice Settings

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Speak faster | Говори быстрее | Increase TTS speed | ⚡ |
| Speak slower | Говори медленнее | Decrease TTS speed | ⚡ |
| Speak louder | Говори громче | Increase TTS volume | ⚡ |
| Speak quieter | Говори тише | Decrease TTS volume | ⚡ |
| Normal voice speed | Нормальная скорость голоса | Reset TTS speed | ⚡ |

### Microphone Settings

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Increase sensitivity | Увеличь чувствительность | More sensitive mic | ⚡ |
| Decrease sensitivity | Уменьши чувствительность | Less sensitive mic | ⚡ |
| Test microphone | Проверь микрофон | Mic test | ⚡ |

### View Settings

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Show settings | Покажи настройки | Display all settings | ⚡ |
| What are my settings? | Какие у меня настройки? | Display all settings | ⚡ |
| Reset settings | Сбрось настройки | Reset to defaults | 🔒 |

---

## Information Queries

### Time & Date

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| What time is it? | Сколько времени? | Tell current time | ⚡ |
| Tell me the time | Скажи время | Tell current time | ⚡ |
| What's the time? | Который час? | Tell current time | ⚡ |
| What's the date? | Какое число? | Tell current date | ⚡ |
| What day is it? | Какой сегодня день? | Tell day of week | ⚡ |
| What's today's date? | Какое сегодня число? | Tell current date | ⚡ |

### System Information

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| How much memory are you using? | Сколько памяти используешь? | Report memory usage | ⚡ |
| What's your CPU usage? | Какая загрузка процессора? | Report CPU usage | ⚡ |
| Show system stats | Покажи системную статистику | Show all stats | ⚡ |
| What's my computer name? | Как называется мой компьютер? | Tell computer name | ⚡ |
| What's my username? | Как моё имя пользователя? | Tell username | ⚡ |

### Gerald Status

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Are you working? | Ты работаешь? | Status check | ⚡ |
| Are you online? | Ты онлайн? | Status check | ⚡ |
| Status check | Проверка статуса | Full status report | ⚡ |
| What services are running? | Какие сервисы работают? | List active services | ⚡ |

---

## Confirmation Responses

When Gerald asks for confirmation, respond with:

### Affirmative (Proceed)

| English | Russian |
|---------|---------|
| Yes | Да |
| Confirm | Подтверди |
| Do it | Сделай |
| Proceed | Продолжай |
| Go ahead | Давай |
| Execute | Выполни |
| OK | ОК |
| Sure | Конечно |

### Negative (Cancel)

| English | Russian |
|---------|---------|
| No | Нет |
| Cancel | Отмена |
| Stop | Стоп |
| Nevermind | Не надо |
| Don't | Не надо |
| Abort | Отмени |
| Wait | Подожди |

**Example Flow**:
```
Gerald: "This will delete file important.txt. Confirm deletion?"
You: "Yes" → File deleted
OR
You: "No" → Action cancelled
```

---

## Special Commands

### Emergency Commands

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Help | Помощь | Show quick help | ⚡ |
| Stop | Стоп | Stop current action | ⚡ |
| Cancel | Отмена | Cancel current action | ⚡ |
| Repeat | Повтори | Repeat last response | ⚡ |
| What did you say? | Что ты сказал? | Repeat last response | ⚡ |

### Testing Commands

| English Command | Russian Command | Action | Type |
|----------------|-----------------|--------|------|
| Test microphone | Проверь микрофон | Microphone test | ⚡ |
| Test speakers | Проверь динамики | Speaker test | ⚡ |
| Test voice recognition | Проверь распознавание голоса | ASR test | ⚡ |
| Are you listening? | Ты слушаешь? | Listening test | ⚡ |

---

## Command Syntax Guide

### Placeholders

- `<app>` - Any application name (Chrome, Calculator, etc.)
- `<file>` - File name with or without extension
- `<folder>` - Folder/directory name
- `<command>` - Terminal command
- `<value>` - Setting value (number, text, etc.)

### Examples

```
Template: "Open <app>"
Valid: "Open Chrome", "Open Calculator", "Open Yandex Browser"

Template: "Create file <file>"
Valid: "Create file notes.txt", "Create file todo.md"

Template: "Volume <up|down>"
Valid: "Volume up", "Volume down"
```

---

## Tips for Better Recognition

### DO:
✓ Speak clearly and naturally
✓ Use simple, direct commands
✓ Say wake word first: "Hey Gerald, open Chrome"
✓ Wait for Gerald's beep before speaking command
✓ Use exact command patterns from this guide

### DON'T:
✗ Speak too fast or mumble
✗ Combine multiple commands: "Open Chrome and Calculator"
✗ Use vague commands: "Do the thing"
✗ Interrupt Gerald while speaking

---

## Language Detection

Gerald automatically detects language:

```
You: "Open Chrome" → Detected: English → Response in English
You: "Открой Chrome" → Detected: Russian → Response in Russian
```

Mixed commands work too:
```
You: "Open Яндекс браузер" → Gerald understands intent
```

---

## Command Aliases

Many commands have multiple variations. All of these work:

| Category | Variations |
|----------|------------|
| **Launch** | Open, Launch, Start, Run |
| **Close** | Close, Shut down, Exit, Kill |
| **Confirm** | Yes, Confirm, Do it, Proceed, OK |
| **Cancel** | No, Cancel, Stop, Nevermind, Abort |
| **Delete** | Delete, Remove, Erase |

---

## Future Commands (Coming Soon)

Planned for future versions:

- Window management: "Minimize Chrome", "Maximize window"
- Custom workflows: "Start work mode" (opens specific apps)
- Browser control: "Open Google", "Search for..."
- Email: "Read emails", "Send email to..."
- Calendar: "What's my schedule?"
- Smart home: "Turn off lights" (with integrations)

---

## Complete Command Count

| Category | English Commands | Russian Commands | Total |
|----------|------------------|------------------|-------|
| System | 12 | 12 | 24 |
| Applications | 8 | 8 | 16 |
| Files | 10 | 10 | 20 |
| Terminal | 6 | 6 | 12 |
| Music | 15 | 15 | 30 |
| Recognition | 8 | 8 | 16 |
| Settings | 18 | 18 | 36 |
| Information | 14 | 14 | 28 |
| **TOTAL** | **91** | **91** | **182** |

---

## See Also

- [USER_GUIDE.md](USER_GUIDE.md) - Detailed usage guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [API_REFERENCE.md](API_REFERENCE.md) - Developer API docs

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
**Language Support**: English, Russian (Русский)

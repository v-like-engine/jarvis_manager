# Gerald Desktop Manager - Demo Scenarios

Complete demonstration scenarios for testing and showcasing Gerald's capabilities.

## Table of Contents

1. [Quick Demo (5 minutes)](#quick-demo-5-minutes)
2. [Full Feature Demo (15 minutes)](#full-feature-demo-15-minutes)
3. [Character Switching Demo](#character-switching-demo)
4. [Bilingual Demo](#bilingual-demo)
5. [Safety Features Demo](#safety-features-demo)
6. [Advanced Features Demo](#advanced-features-demo)
7. [Video Script](#video-script)

---

## Quick Demo (5 minutes)

Perfect for first-time users or quick presentations.

### Setup
```powershell
python start_gerald.py
```

### Scenario 1: Basic Introduction (1 min)

**Command 1**: "Who are you?"
```
Expected: Gerald introduces himself as a voice-controlled desktop assistant
Response: "I am Gerald, your loyal desktop knight. I control your Windows machine by voice command. Speak your orders, and I shall execute them."
```

**Command 2**: "What can you do?"
```
Expected: Lists main capabilities
Response: Brief overview of app control, file management, music control, etc.
```

### Scenario 2: Application Control (2 min)

**Command 3**: "Open Notepad"
```
Expected: Notepad launches
Response: "Opening Notepad, sir."
Action: Notepad window appears
```

**Command 4**: "Open Calculator"
```
Expected: Calculator launches
Response: "Calculator opening."
Action: Calculator window appears
```

**Command 5**: "Close Notepad"
```
Expected: Notepad closes
Response: "Closing Notepad. Done."
Action: Notepad window closes
```

### Scenario 3: Music Control (1 min)

**Command 6**: "Play music"
```
Expected: Media playback starts/resumes
Response: "Playing."
Action: Music player responds to play command
```

**Command 7**: "Pause"
```
Expected: Media pauses
Response: "Paused."
Action: Playback pauses
```

### Scenario 4: Shutdown (1 min)

**Command 8**: "Exit Gerald"
```
Expected: Gerald shuts down gracefully
Response: "Shutting down. Farewell, sir."
Action: All services stop cleanly
```

**Demo Result**: User sees basic voice control in action

---

## Full Feature Demo (15 minutes)

Comprehensive demonstration of all major features.

### Setup
```powershell
python start_gerald.py
# Ensure test applications installed (Chrome, Notepad, Calculator)
# Prepare test folder: C:\GeraldDemo\
```

### Part 1: Introduction & Character (2 min)

**Step 1**: "Who are you?"
```
Gerald introduces himself
```

**Step 2**: "What's your name?"
```
Response: "I am Gerald. Your voice-controlled desktop knight."
```

**Step 3**: "Tell me about yourself"
```
Extended self-description
```

### Part 2: Application Management (3 min)

**Step 4**: "Open Google Chrome"
```
Chrome browser launches
```

**Step 5**: "Open Notepad"
```
Notepad launches alongside Chrome
```

**Step 6**: "Open Calculator"
```
Calculator opens (3 apps now running)
```

**Step 7**: "Close Calculator"
```
Calculator closes, others remain
```

**Step 8**: "Close Chrome"
```
Chrome closes
```

### Part 3: File Operations (3 min)

**Step 9**: "Create folder GeraldTest"
```
Expected: Folder created in current directory
Response: "Folder GeraldTest created."
Action: Folder appears
```

**Step 10**: "Create file test.txt in GeraldTest"
```
Expected: Empty file created
Response: "File created: test.txt"
```

**Step 11**: "Delete file test.txt"
```
Expected: Confirmation prompt
Response: "This will delete test.txt. Are you sure? Say 'confirm' or 'cancel'."
```

**Step 12**: "Confirm"
```
Expected: File deleted
Response: "File deleted."
```

### Part 4: Music Control (2 min)

**Step 13**: "Play music"
```
Media plays
```

**Step 14**: "Volume up"
```
Volume increases
```

**Step 15**: "Next track"
```
Skips to next track
```

**Step 16**: "Pause"
```
Playback pauses
```

### Part 5: System Commands (2 min)

**Step 17**: "What time is it?"
```
Expected: Current time
Response: "It is 3:45 PM."
```

**Step 18**: "What's today's date?"
```
Expected: Current date
Response: "Today is November 22, 2025."
```

**Step 19**: "What's my computer name?"
```
Expected: Computer hostname
Response: "Your computer is DESKTOP-ABC123."
```

### Part 6: Language Switching (2 min)

**Step 20**: "Change language"
```
Expected: Switches to Russian
Response (in Russian): "Язык изменён на русский."
```

**Step 21**: "Кто ты?" (Russian: "Who are you?")
```
Expected: Russian introduction
Response: "Я Геральд, ваш голосовой помощник..."
```

**Step 22**: "Change language" (spoken in Russian)
```
Expected: Switches back to English
Response: "Language changed to English."
```

### Part 7: Shutdown (1 min)

**Step 23**: "Exit Gerald"
```
Graceful shutdown
```

**Demo Result**: Complete overview of all major features

---

## Character Switching Demo

Demonstrate different personality modes.

### Setup
```powershell
python start_gerald.py --character gerald
```

### Scenario 1: Gerald (Strict Knight)

**Command 1**: "Who are you?"
```
Expected: Formal, authoritative introduction
Response: "I am Gerald, your loyal knight and desktop guardian. I serve at your command, executing your orders with precision and discipline."
Voice: Lower pitch, steady pace, authoritative
```

**Command 2**: "Open Notepad"
```
Response: "Opening Notepad, sir."
Tone: Direct, brief, no-nonsense
```

**Command 3**: "Thank you"
```
Response: "Just doing my duty. What's next?"
Tone: Professional, not overly warm
```

### Scenario 2: Winnie Pooh (Gentle Bear)

**Switch Character**:
```powershell
# Restart with different character
python start_gerald.py --character winnie_pooh
```

**Command 4**: "Who are you?"
```
Expected: Warm, gentle introduction
Response: "Oh, hello! I'm Winnie the Pooh, a bear from the Hundred Acre Wood. I'm here to help you with your computer. I may be a bear of very little brain, but I'll do my best!"
Voice: Slower, gentler, warm tone
```

**Command 5**: "Open Notepad"
```
Response: "Hmm... opening Notepad. Yes, yes, I'll do that right away."
Tone: Thoughtful, warm, slightly hesitant
```

**Command 6**: "Thank you"
```
Response: "Oh, you're very welcome! Happy to help. Perhaps there's some honey nearby?"
Tone: Warm, pleased, philosophical
```

### Comparison

| Aspect | Gerald | Winnie Pooh |
|--------|--------|-------------|
| **Tone** | Authoritative, strict | Gentle, thoughtful |
| **Pace** | Quick, efficient | Slow, contemplative |
| **Style** | Direct, brief | Warm, elaborate |
| **Personality** | Knight, loyal | Bear, philosophical |

**Demo Result**: Shows personality system works correctly

---

## Bilingual Demo

Demonstrate seamless English/Russian support.

### Scenario: English to Russian Switch

**Setup**:
```powershell
python start_gerald.py --language en
```

**English Phase**:

1. "Who are you?"
   ```
   Response in English
   ```

2. "Open Calculator"
   ```
   Calculator opens, English response
   ```

3. "Change language"
   ```
   Response: "Language changed to Russian."
   ```

**Russian Phase**:

4. "Кто ты?" (Who are you?)
   ```
   Response: Russian introduction
   ```

5. "Открой блокнот" (Open Notepad)
   ```
   Notepad opens, Russian response
   ```

6. "Закрой калькулятор" (Close Calculator)
   ```
   Calculator closes, Russian response
   ```

7. "Сменить язык" (Change language)
   ```
   Response: "Язык изменён на английский."
   ```

**Demo Result**: Seamless bilingual operation

---

## Safety Features Demo

Demonstrate safety checks and confirmation flow.

### Scenario 1: File Deletion (Safe Mode)

**Command 1**: "Delete file important_document.txt"
```
Expected: Safety warning + confirmation request
Response: "Warning! This will permanently delete important_document.txt. This action cannot be undone. Are you sure? Say 'confirm' to proceed or 'cancel' to abort."
```

**Command 2**: "Cancel"
```
Expected: Operation cancelled
Response: "Operation cancelled. File not deleted."
```

**Command 3**: "Delete file test.txt"
```
Expected: Confirmation request
Response: "Delete test.txt. Confirm?"
```

**Command 4**: "Confirm"
```
Expected: File deleted
Response: "File deleted."
```

### Scenario 2: Dangerous Terminal Command

**Command 5**: "Execute command format C:"
```
Expected: Absolute block
Response: "I cannot execute that command. It is extremely dangerous and could destroy your system. This operation is blocked for safety."
```

**Command 6**: "Execute command delete system32"
```
Expected: Absolute block
Response: "I will not execute that command. It would damage your Windows installation. Blocked."
```

### Scenario 3: Terminal Command with Confirmation

**Command 7**: "Execute command ipconfig /flushdns"
```
Expected: Confirmation (safe command but needs approval)
Response: "This will execute: ipconfig /flushdns. This command flushes DNS cache. Confirm?"
```

**Command 8**: "Confirm"
```
Expected: Command executes
Response: "Command executed. DNS cache flushed."
```

**Demo Result**: Safety system prevents dangerous operations

---

## Advanced Features Demo

### Scenario 1: System Information

**Command 1**: "What's my computer name?"
```
Response: "Your computer is DESKTOP-ABC123."
```

**Command 2**: "How much RAM do I have?"
```
Response: "You have 16GB of RAM. Currently using 8GB (50%)."
```

**Command 3**: "What's my CPU usage?"
```
Response: "CPU usage is 35%."
```

**Command 4**: "How much disk space is free?"
```
Response: "Drive C: has 125GB free of 500GB (75% used)."
```

### Scenario 2: Time and Date

**Command 5**: "What time is it?"
```
Response: "It is 3:45 PM."
```

**Command 6**: "What's today's date?"
```
Response: "Today is Saturday, November 22, 2025."
```

**Command 7**: "What day is it?"
```
Response: "Today is Saturday."
```

### Scenario 3: Calculator (Future Feature)

**Command 8**: "Calculate 25 times 4"
```
Expected: Math calculation
Response: "25 times 4 equals 100."
```

---

## Video Script

### Demo Video Structure (3-5 minutes)

**Opening** (0:00-0:15)
```
[Screen: Windows desktop]
Narrator: "Meet Gerald, your voice-controlled desktop assistant for Windows."
[Gerald logo appears]
```

**Launch** (0:15-0:30)
```
[Screen: Terminal]
Command: python start_gerald.py
[Screen: Services starting]
Gerald (TTS): "Ready to serve, sir."
Narrator: "Gerald runs completely offline using local AI models."
```

**Basic Commands** (0:30-1:15)
```
User: "Who are you?"
Gerald: "I am Gerald, your loyal desktop knight..."

User: "Open Chrome"
[Chrome launches]
Gerald: "Opening Chrome, sir."

User: "Open Calculator"
[Calculator opens]
Gerald: "Calculator opening."

User: "Close Chrome"
[Chrome closes]
Gerald: "Closing Chrome. Done."
```

**Safety Demo** (1:15-1:45)
```
User: "Delete file important.txt"
Gerald: "Warning! This will delete important.txt. Confirm?"
User: "Cancel"
Gerald: "Operation cancelled."

Narrator: "Gerald protects your system with multi-layer safety checks."
```

**Bilingual** (1:45-2:15)
```
User: "Change language"
Gerald: "Язык изменён на русский."

User: "Открой блокнот"
[Notepad opens]
Gerald: "Открываю блокнот."

Narrator: "Full bilingual support with English and Russian."
```

**Character Switch** (2:15-2:45)
```
[Restart with Winnie Pooh]
User: "Who are you?"
Winnie: "Oh, hello! I'm Winnie the Pooh..."

Narrator: "Choose different personalities to match your style."
```

**Features Overview** (2:45-3:15)
```
[Split screen showing features]
- Application control
- File management
- Music control
- Terminal commands
- System information
- Voice/face recognition

Narrator: "Over 180 voice commands for complete desktop control."
```

**Closing** (3:15-3:30)
```
User: "Exit Gerald"
Gerald: "Shutting down. Farewell, sir."

[Gerald logo]
Text: "Gerald Desktop Manager"
Text: "100% Offline • Private • Open Source"
Text: "Download at: github.com/..."
```

---

## Testing Checklist

Use this checklist when demonstrating Gerald:

### Pre-Demo Setup
- [ ] Models downloaded
- [ ] Services start successfully
- [ ] Microphone working and tested
- [ ] Test applications installed (Chrome, Notepad, Calculator)
- [ ] Test folder created (C:\GeraldDemo\)
- [ ] Background noise minimized
- [ ] Script/notes prepared

### Basic Features
- [ ] Introduction commands work
- [ ] App launch works (3+ apps)
- [ ] App close works
- [ ] Music control works
- [ ] File operations work
- [ ] Language switch works

### Advanced Features
- [ ] Safety checks trigger correctly
- [ ] Character switching works
- [ ] System info commands work
- [ ] Bilingual commands work
- [ ] Shutdown is clean

### Post-Demo
- [ ] All applications closed
- [ ] Test files cleaned up
- [ ] Gerald shut down properly
- [ ] No error messages in logs

---

## Tips for Great Demos

### Do's

✅ **Speak clearly** - Enunciate words
✅ **Normal pace** - Not too fast or slow
✅ **Use exact phrases** - Match command patterns
✅ **Pause between commands** - Let Gerald respond
✅ **Show errors** - Demonstrate error handling
✅ **Highlight safety** - Show confirmation flow
✅ **Test beforehand** - Always do a dry run

### Don'ts

❌ **Don't mumble** - Gerald needs clear audio
❌ **Don't rush** - Wait for responses
❌ **Don't use background music** - Interferes with VAD
❌ **Don't skip setup** - Models must be downloaded
❌ **Don't use complex sentences** - Stick to command patterns
❌ **Don't demo in noisy environment** - Background noise reduces accuracy

---

**Demo Scenarios Version**: 1.0.0
**Last Updated**: 2025-11-22
**Tested**: Windows 10 & 11

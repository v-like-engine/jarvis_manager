# Changelog

All notable changes to Gerald Desktop Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v1.1.0
- WebSocket support for real-time communication
- Custom voice command framework
- Official Python and JavaScript SDKs
- Improved face recognition accuracy
- GPU acceleration for LLM inference
- Additional characters (Jarvis, Friday)

### Planned for v1.2.0
- Advanced music control (Spotify integration)
- Browser control and web search
- Window management commands
- Performance optimizations
- Linux support (Ubuntu)

### Planned for v2.0.0
- macOS support
- Multi-user support with profiles
- Cloud synchronization (optional)
- Mobile companion app
- Smart home integration
- Custom wake word training

---

## [1.0.0] - 2025-11-22

### Initial Release

First public release of Gerald Desktop Manager - a voice-controlled desktop manager for Windows 10/11.

### Added

#### Core Features
- **Voice Control**: Complete voice command system for Windows control
- **Offline Operation**: 100% local processing, no internet required after setup
- **Bilingual Support**: Full English and Russian language support
- **Character System**: Gerald character with extensible personality framework

#### ASR Service (Agent 1)
- Speech recognition using Vosk (English and Russian models)
- Voice Activity Detection using Silero VAD
- Text-to-Speech using pyttsx3
- Face recognition using dlib and face-recognition
- Voice biometrics using SpeechBrain
- Automatic language detection
- Command parsing with pattern matching
- Real-time audio capture from microphone

#### LLM Service (Agent 2)
- Local LLM inference using llama.cpp
- Support for Phi-3-mini, Gemma-2-2b, TinyLlama models
- Gerald character personality system
- Prompt template engine using Jinja2
- Safety validation for dangerous commands
- Context management for conversations
- Response generation in multiple languages
- Character switching capability

#### Command Service (Agent 3)
- **Application Control**:
  - Launch applications by voice
  - Close running applications
  - Fuzzy matching for app names
  - Support for common Windows applications
- **File Operations**:
  - Create files and folders
  - Delete files and folders (with confirmation)
  - System file protection
- **Terminal Execution**:
  - Execute Windows terminal commands
  - Whitelist for safe commands
  - Blacklist for dangerous commands
  - Confirmation required for risky commands
- **Music Control**:
  - Play/pause/stop playback
  - Next/previous track
  - Volume up/down/mute
  - Works with any media application
- **Settings Management**:
  - Change language
  - Configure auto-start
  - Adjust voice settings
  - View and update all settings

#### Safety Features
- Multi-layer safety checking (ASR → LLM → Command)
- Confirmation required for dangerous operations
- Absolute blocks for system-destroying commands
- Protection of system files and folders
- Audit logging of all commands

#### Documentation (Agent 4)
- Complete architecture documentation
- Step-by-step installation guide
- Comprehensive user guide
- Bilingual command reference (182 commands)
- Complete API reference for all services
- Developer guide for contributors
- Troubleshooting guide
- Contributing guidelines

#### Testing (Agent 4)
- Integration test framework
- Performance test suite
- Safety test coverage
- Test fixtures and utilities
- CI/CD ready test infrastructure

### Technical Details

#### Architecture
- Microservice architecture (3 independent services)
- REST API communication between services
- FastAPI for all service endpoints
- SQLite for user data storage
- YAML for configuration
- Structured logging with separate log files

#### Models
- Vosk ASR models (English and Russian)
- Phi-3-mini LLM (2.3GB, Q4 quantized)
- Face recognition models (dlib)
- SpeechBrain voice biometrics
- Total model size: ~25GB

#### Performance
- CPU usage: <5% when idle
- Memory usage: <4GB total
- Response time: <2 seconds
- Startup time: ~30 seconds

#### Requirements
- Windows 10 or Windows 11 (64-bit)
- Python 3.10, 3.11, or 3.12
- 8GB RAM minimum (16GB recommended)
- 30GB disk space
- Microphone (any USB or built-in)
- Optional: Webcam (for face recognition)

### Command Categories

1. **System Commands** (12 English + 12 Russian):
   - Gerald control (exit, restart, sleep)
   - Self-identification (who are you, what can you do)

2. **Application Control** (8 English + 8 Russian):
   - Launch applications
   - Close applications
   - Fuzzy app name matching

3. **File Operations** (10 English + 10 Russian):
   - Create files and folders
   - Delete files and folders (with confirmation)

4. **Terminal Commands** (6 English + 6 Russian):
   - Execute terminal commands (with confirmation)
   - Safe command whitelist
   - Dangerous command blacklist

5. **Music Control** (15 English + 15 Russian):
   - Playback control
   - Track navigation
   - Volume control

6. **User Recognition** (8 English + 8 Russian):
   - Face enrollment and identification
   - Voice enrollment and identification
   - User data management

7. **Settings** (18 English + 18 Russian):
   - Language switching
   - Startup configuration
   - Voice settings
   - Microphone settings

8. **Information Queries** (14 English + 14 Russian):
   - Time and date
   - System information
   - Gerald status

**Total**: 91 English commands + 91 Russian commands = 182 commands

### API Endpoints

#### ASR Service (Port 8001)
- `GET /health` - Service health check
- `POST /recognize` - Speech to text
- `POST /parse_command` - Extract intent from text
- `POST /speak` - Text to speech
- `POST /enroll_face` - Enroll user face
- `POST /identify_face` - Identify user by face
- `POST /enroll_voice` - Enroll user voice
- `POST /identify_voice` - Identify user by voice

#### LLM Service (Port 8002)
- `GET /health` - Service health check
- `POST /generate` - Generate natural language response
- `POST /safety_check` - Validate command safety
- `GET /character` - Get current character info
- `POST /set_character` - Switch character

#### Command Service (Port 8003)
- `GET /health` - Service health check
- `POST /execute` - Execute parsed command
- `POST /app/launch` - Launch application
- `POST /app/close` - Close application
- `GET /app/list` - List running applications
- `POST /file/create` - Create file
- `POST /file/delete` - Delete file
- `POST /folder/create` - Create folder
- `POST /terminal/execute` - Execute terminal command
- `POST /music/play` - Control music playback
- `POST /music/volume` - Control volume
- `GET /settings` - Get all settings
- `POST /settings/update` - Update setting

### Dependencies

#### Core Dependencies
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- pydantic >= 2.0.0
- vosk >= 0.3.45
- llama-cpp-python >= 0.2.0
- pyttsx3 >= 2.90
- face-recognition >= 1.3.0
- speechbrain >= 0.5.16
- pywin32 >= 306
- psutil >= 5.9.0

#### Development Dependencies
- pytest >= 7.4.0
- pytest-asyncio >= 0.21.0
- pytest-cov >= 4.1.0
- black >= 23.0.0
- flake8 >= 6.0.0
- mypy >= 1.5.0

See `services/*/requirements.txt` for complete dependency lists.

### Known Issues

1. **Windows Only**: No macOS or Linux support in v1.0
2. **CPU-Only LLM**: No GPU acceleration yet
3. **Limited Languages**: Only English and Russian
4. **Basic Music Control**: Only standard media keys
5. **No Custom Commands**: Can't add user-defined voice commands

### Security

- All voice/face data stored locally in SQLite
- No cloud communication after initial setup
- Multi-layer safety validation
- Dangerous commands blocked or require confirmation
- System files protected from deletion

### Privacy

- 100% offline operation
- No telemetry or analytics
- No data collection
- User data can be deleted anytime
- Open source (license TBD)

---

## Version History Summary

| Version | Release Date | Major Features |
|---------|--------------|----------------|
| v1.0.0  | 2025-11-22   | Initial release with core voice control features |

---

## Upgrade Guide

### From Future v1.0.x to v1.1.0

(Will be added when v1.1.0 is released)

---

## Contributors

### Core Team
- **Agent 1 (ASR Service)**: Speech recognition, TTS, face/voice ID
- **Agent 2 (LLM Service)**: Language model integration, character system
- **Agent 3 (Command Service)**: Command execution, app control, file operations
- **Agent 4 (Testing & Documentation)**: QA, testing, documentation

### Community Contributors

(Will be added as contributors join)

---

## Links

- **Homepage**: https://github.com/yourusername/gerald-desktop-manager
- **Documentation**: https://gerald-docs.com (TBD)
- **Issues**: https://github.com/yourusername/gerald-desktop-manager/issues
- **Discussions**: https://github.com/yourusername/gerald-desktop-manager/discussions
- **Discord**: https://discord.gg/gerald (TBD)

---

**Legend**:
- `Added` - New features
- `Changed` - Changes to existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security improvements

---

**Last Updated**: 2025-11-22
**Current Version**: v1.0.0

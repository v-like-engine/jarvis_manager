# Gerald Desktop Manager 🎙️🖥️

**Voice-Controlled Virtual Desktop Manager for Windows 10/11**

Gerald is an offline, voice-controlled desktop manager that acts as your personal computer knight - strict, helpful, and always ready to execute your commands.

## 🌟 Features

- **Voice Control**: Speak commands in English or Russian
- **Offline First**: Works without internet using local models
- **App Management**: Launch and close applications by voice
- **Face Recognition**: Identify users via webcam
- **Voice Recognition**: Identify users by voice patterns
- **File Operations**: Create, delete, and navigate files/folders
- **Terminal Integration**: Execute safe terminal commands
- **Music Control**: Control music playback in apps
- **Auto-Start**: Launch with Windows
- **Multilingual**: Full Russian and English support with auto-detection
- **Safe by Design**: Confirmation required for dangerous operations

## 🎯 Voice Commands

### English Examples
- "Open Yandex Browser" - Launch application
- "Close Chrome" - Close running app
- "Recognize me" - Start face/voice identification
- "Who are you?" - About Gerald
- "Change the language" - Switch language
- "Exit Gerald" - Shutdown manager

### Russian Examples
- "Открой Яндекс браузер" - Запустить приложение
- "Закрой Chrome" - Закрыть приложение
- "Кто я?" - Распознавание лица/голоса
- "Кто ты?" - Информация о Gerald
- "Сменить язык" - Переключить язык
- "Выключись" - Выключить менеджер

See [full command list](docs/COMMANDS.md) for all available commands.

## 🏗️ Architecture

Gerald is built as a **microservice architecture** with three main services:

```
┌─────────────────────────────────────────────────────────────┐
│                     Gerald Desktop Manager                  │
├─────────────────┬──────────────────┬────────────────────────┤
│  ASR Service    │   LLM Service    │  Command Service       │
│  (Agent 1)      │   (Agent 2)      │  (Agent 3)             │
├─────────────────┼──────────────────┼────────────────────────┤
│ • Speech Rec    │ • Local LLM      │ • App Launcher         │
│ • Voice/Face ID │ • Character      │ • File Operations      │
│ • TTS Engine    │   (Gerald)       │ • Terminal Executor    │
│ • Command Parse │ • Prompt Builder │ • Music Control        │
│ • VAD           │ • Safety Prompts │ • Settings Manager     │
└─────────────────┴──────────────────┴────────────────────────┘
```

Each service is independent and communicates via REST APIs or message queues.

## 📋 Requirements

### System Requirements
- **OS**: Windows 10 or Windows 11
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 25GB for models
- **Microphone**: Any USB or built-in microphone
- **Webcam**: Optional (for face recognition)

### Python Dependencies
See individual service requirements:
- `services/asr_service/requirements.txt`
- `services/llm_service/requirements.txt`
- `services/command_service/requirements.txt`

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd jarvis_manager
```

### 2. Install Dependencies
```bash
# Install all service dependencies
pip install -r services/asr_service/requirements.txt
pip install -r services/llm_service/requirements.txt
pip install -r services/command_service/requirements.txt
```

### 3. Download Models
```bash
# Download ASR, LLM, and recognition models (first run only)
python setup_models.py
```

This will download:
- Vosk ASR models for English and Russian (~100MB each)
- Local LLM model (Phi-3-mini or Gemma-2, ~2-5GB)
- Face recognition models (~10MB)
- TTS models (~50MB)

### 4. Launch Gerald
```bash
python run_gerald.py
```

Or use the batch file on Windows:
```bash
run_gerald.bat
```

### 5. First-Time Setup
On first run, Gerald will:
1. Initialize all services
2. Test microphone access
3. Request webcam permission (for face recognition)
4. Ask if you want to enable startup with Windows

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[User Guide](docs/USER_GUIDE.md)** - How to use Gerald
- **[Commands Reference](docs/COMMANDS.md)** - Complete command list
- **[Architecture](docs/ARCHITECTURE.md)** - System design and architecture
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Contributing and development
- **[API Reference](docs/API_REFERENCE.md)** - Service APIs
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

## 🧪 Testing

Run tests for all services:
```bash
# Run all tests
pytest tests/

# Run specific service tests
pytest services/asr_service/tests/
pytest services/llm_service/tests/
pytest services/command_service/tests/

# Run with coverage
pytest --cov=services tests/
```

## 🔧 Configuration

Main configuration file: `config/main_config.yaml`

```yaml
gerald:
  character: "gerald"          # Character personality
  default_language: "en"       # en or ru
  auto_start: false           # Launch with Windows

asr:
  vad_threshold: 0.5          # Voice activity detection sensitivity
  sample_rate: 16000          # Audio sample rate

llm:
  model: "phi-3-mini"         # Local LLM model
  temperature: 0.7            # Response randomness
  max_tokens: 100             # Max response length

commands:
  confirmation_required:      # Commands requiring confirmation
    - file_delete
    - terminal_command
```

## 🎭 Character System

Gerald is the default character, but the system supports multiple personalities. Each character has:
- Unique voice settings
- Personality traits
- Response styles
- System prompts

Character configurations are in `services/llm_service/characters/`

### Gerald's Personality
- **Archetype**: Loyal Knight
- **Traits**: Strict, heroic, helpful, direct, sometimes rude
- **Communication**: Brief, authoritative, not overly polite
- **Voice**: Lower pitch, steady pace

## 🔒 Privacy & Security

- **Offline First**: All processing happens locally, no data sent to cloud
- **Data Storage**: User face/voice features stored locally in SQLite database
- **Safety Checks**: Dangerous operations require explicit confirmation
- **No Telemetry**: No usage data collected or transmitted

## 🛠️ Development

### Project Structure
```
jarvis_manager/
├── services/
│   ├── asr_service/          # Agent 1: ASR & Recognition
│   ├── llm_service/          # Agent 2: LLM & Characters
│   └── command_service/      # Agent 3: Command Execution
├── shared/
│   ├── models/               # Downloaded models
│   └── utils/                # Shared utilities
├── docs/                     # Documentation
├── tests/                    # Integration tests
├── config/                   # Configuration files
└── .claude/agents/           # Agent development docs
```

### Development Agents

This project was built using 4 specialized AI agents:
1. **Agent 1**: ASR Service (Speech, voice, face recognition)
2. **Agent 2**: LLM Service (Local models, character setup)
3. **Agent 3**: Command Service (App control, file ops, terminal)
4. **Agent 4**: Testing & Documentation (QA, tests, docs)

See `.claude/agents/` for agent specifications.

## 🐛 Known Issues

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for solutions.

## 🗺️ Roadmap

- [ ] Support for macOS and Linux
- [ ] Additional characters (Jarvis, Friday, etc.)
- [ ] Voice command customization
- [ ] Browser control integration
- [ ] Calendar and email integration
- [ ] Smart home device control

## 📝 License

[To be determined]

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `docs/` folder

---

**Gerald is ready to serve. Speak your command!** 🎙️⚔️

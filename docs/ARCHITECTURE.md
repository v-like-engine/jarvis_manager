# Gerald Desktop Manager - System Architecture

## Table of Contents
1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [System Design](#system-design)
4. [Service Architecture](#service-architecture)
5. [Communication Layer](#communication-layer)
6. [Data Flow](#data-flow)
7. [Technology Stack](#technology-stack)
8. [Offline-First Design](#offline-first-design)
9. [Performance Considerations](#performance-considerations)
10. [Security & Privacy](#security--privacy)

---

## Overview

Gerald Desktop Manager is a voice-controlled desktop management system for Windows 10/11 built using a **microservice architecture**. The system is designed to operate completely offline, processing all voice commands locally without requiring internet connectivity.

### Core Principles
- **Microservice Architecture**: Three independent services with clear responsibilities
- **Offline-First**: All processing happens locally using on-device models
- **Low Resource Usage**: Optimized for background operation (<5% CPU when idle)
- **Bilingual Support**: Native English and Russian language support
- **Safety-First**: Dangerous operations require explicit user confirmation
- **Character-Driven**: Extensible personality system (Gerald as default)

---

## Architecture Principles

### 1. Separation of Concerns
Each service has a single, well-defined responsibility:
- **ASR Service**: All input/output (speech, face, voice, TTS)
- **LLM Service**: Intelligence and personality layer
- **Command Service**: Execution and system integration

### 2. Service Independence
- Services can be developed, tested, and deployed independently
- Each service has its own configuration, dependencies, and data store
- Services communicate via well-defined APIs
- Failure in one service doesn't crash the entire system

### 3. Scalability
- Services can run on same machine or distributed across multiple machines
- Easy to add new services (e.g., Browser Control Service, Smart Home Service)
- Character system allows multiple personalities without code changes

### 4. Testability
- Each service has unit tests for internal logic
- Integration tests verify service communication
- Performance tests ensure resource efficiency
- Safety tests validate security mechanisms

---

## System Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Gerald Desktop Manager                         │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   ASR Service    │  │   LLM Service    │  │ Command Service  │  │
│  │   (Port 8001)    │  │   (Port 8002)    │  │   (Port 8003)    │  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤  │
│  │ • Microphone     │  │ • Local LLM      │  │ • App Launcher   │  │
│  │ • VAD            │  │ • Character      │  │ • File Ops       │  │
│  │ • Speech→Text    │  │ • Prompt Builder │  │ • Terminal Exec  │  │
│  │ • Command Parser │  │ • Safety Check   │  │ • Music Control  │  │
│  │ • Face Rec       │  │ • Response Gen   │  │ • Safety Checker │  │
│  │ • Voice Rec      │  │ • Context Mgmt   │  │ • Settings Mgr   │  │
│  │ • TTS            │  │                  │  │                  │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                      │             │
│           └──────────────┬──────┴──────────┬───────────┘             │
│                          │                 │                         │
│                    ┌─────▼─────────────────▼─────┐                  │
│                    │  HTTP REST API / Message Q  │                  │
│                    └─────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Windows 10/11 OS  │
                    │ • Win32 APIs       │
                    │ • File System      │
                    │ • Process Manager  │
                    └────────────────────┘
```

---

## Service Architecture

### 1. ASR Service (Port 8001)
**Responsibility**: All voice and face input/output

#### Components:
```
asr_service/
├── src/
│   ├── main.py                    # FastAPI service entry point
│   ├── audio_capture.py           # Microphone input handling
│   ├── vad.py                     # Voice Activity Detection (Silero VAD)
│   ├── speech_recognition.py     # Vosk ASR (en + ru models)
│   ├── command_parser.py          # Extract intent from recognized text
│   ├── language_detector.py       # Auto-detect language
│   ├── tts_engine.py              # Text-to-Speech (pyttsx3)
│   ├── face_recognition.py        # Face detection/recognition
│   └── voice_biometrics.py        # Speaker identification
├── config/
│   └── asr_config.yaml            # Service configuration
├── tests/
│   └── test_*.py                  # Unit tests
└── requirements.txt               # Dependencies
```

#### Key Technologies:
- **Vosk** (0.3.45+): Offline ASR for English and Russian
- **Silero VAD** (4.0.0+): Voice activity detection
- **pyttsx3**: Text-to-speech engine
- **face-recognition** + **dlib**: Face detection and recognition
- **SpeechBrain**: Voice biometrics (speaker identification)
- **FastAPI**: REST API framework
- **sounddevice/pyaudio**: Audio I/O

#### APIs:
- `POST /recognize` - Convert audio to text
- `POST /speak` - Convert text to speech
- `POST /enroll_face` - Register user face
- `POST /identify_face` - Identify user from webcam
- `POST /enroll_voice` - Register user voice
- `POST /identify_voice` - Identify user from audio
- `GET /health` - Service health check

---

### 2. LLM Service (Port 8002)
**Responsibility**: Natural language understanding and response generation

#### Components:
```
llm_service/
├── src/
│   ├── main.py                    # FastAPI service entry point
│   ├── llm_engine.py              # LLM inference (llama.cpp)
│   ├── prompt_builder.py          # Build prompts from templates
│   ├── character_loader.py        # Load character configs
│   ├── context_manager.py         # Manage conversation history
│   └── safety_validator.py        # Check for dangerous intents
├── characters/
│   ├── gerald.yaml                # Gerald character config
│   ├── jarvis.yaml                # (Future) Jarvis character
│   └── friday.yaml                # (Future) Friday character
├── prompts/
│   ├── system_prompts.yaml        # System prompts
│   ├── safety_prompts.yaml        # Safety check prompts
│   └── response_templates.yaml    # Response templates
├── config/
│   └── llm_config.yaml            # Service configuration
└── tests/
    └── test_*.py                  # Unit tests
```

#### Key Technologies:
- **llama.cpp** (Python bindings): Local LLM inference
- **Phi-3-mini** / **Gemma-2-2b**: Small, efficient language models
- **Jinja2**: Template engine for prompts
- **FastAPI**: REST API framework

#### Supported Models:
1. **Phi-3-mini** (3.8B params, ~2.3GB)
   - Fast inference on CPU
   - Good reasoning capabilities
   - Recommended default

2. **Gemma-2-2b** (2B params, ~1.5GB)
   - Faster but less capable
   - Good for low-end hardware

3. **TinyLlama-1.1b** (1.1B params, ~637MB)
   - Ultra-fast, minimal quality
   - Emergency fallback

#### APIs:
- `POST /generate` - Generate response to user input
- `POST /safety_check` - Check if command is dangerous
- `POST /set_character` - Switch character personality
- `GET /character` - Get current character info
- `GET /health` - Service health check

---

### 3. Command Service (Port 8003)
**Responsibility**: Execute system commands and operations

#### Components:
```
command_service/
├── src/
│   ├── main.py                    # FastAPI service entry point
│   ├── command_router.py          # Route commands to handlers
│   └── safety_checker.py          # Final safety validation
├── modules/
│   ├── app_launcher/
│   │   ├── launcher.py            # Launch/close applications
│   │   ├── app_discovery.py       # Find installed apps
│   │   └── fuzzy_matcher.py       # Fuzzy app name matching
│   ├── file_ops/
│   │   ├── file_manager.py        # File operations
│   │   └── safety_rules.py        # File safety rules
│   ├── terminal/
│   │   ├── executor.py            # Execute terminal commands
│   │   └── command_validator.py   # Validate terminal commands
│   ├── music_control/
│   │   └── media_controller.py    # Control music playback
│   └── settings/
│       └── settings_manager.py    # Manage Gerald settings
├── config/
│   └── command_config.yaml        # Service configuration
└── tests/
    └── test_*.py                  # Unit tests
```

#### Key Technologies:
- **pywin32**: Windows API integration
- **psutil**: Process and system utilities
- **rapidfuzz**: Fuzzy string matching for app names
- **pycaw**: Audio control
- **pyautogui/keyboard**: Media key simulation
- **FastAPI**: REST API framework

#### APIs:
- `POST /execute` - Execute a command
- `POST /app/launch` - Launch application
- `POST /app/close` - Close application
- `POST /file/create` - Create file/folder
- `POST /file/delete` - Delete file/folder
- `POST /terminal/execute` - Execute terminal command
- `POST /music/play` - Control music playback
- `POST /settings/update` - Update settings
- `GET /health` - Service health check

---

## Communication Layer

### HTTP REST (Default)
Services communicate via HTTP REST APIs for simplicity:

```
User speaks → ASR Service
              ↓ (recognized text + language)
              LLM Service
              ↓ (command intent + parameters)
              Command Service
              ↓ (execution result)
              LLM Service (generate response)
              ↓ (response text + language)
              ASR Service (TTS)
              ↓ (audio)
User hears ← Speaker
```

### Message Queue (Optional)
For higher reliability, can use RabbitMQ:
- Asynchronous processing
- Better error handling
- Command queueing
- Event-driven architecture

Configuration in `config/main_config.yaml`:
```yaml
communication:
  type: "http"  # or "messagequeue"
  timeout: 30
```

---

## Data Flow

### 1. Standard Command Flow

```
┌──────────┐
│  User    │ "Open Yandex Browser"
└────┬─────┘
     │
     ▼
┌─────────────────────┐
│  ASR Service        │
│  1. VAD detects     │
│  2. Recognize text  │
│  3. Detect language │
│  4. Parse command   │
└────┬────────────────┘
     │ {"text": "open yandex browser",
     │  "language": "en",
     │  "intent": "app_launch",
     │  "params": {"app": "yandex browser"}}
     ▼
┌─────────────────────┐
│  LLM Service        │
│  1. Safety check    │
│  2. Build context   │
└────┬────────────────┘
     │ {"safe": true, "command": {...}}
     ▼
┌─────────────────────┐
│  Command Service    │
│  1. Fuzzy match app │
│  2. Launch process  │
│  3. Return result   │
└────┬────────────────┘
     │ {"success": true, "app": "Yandex.exe"}
     ▼
┌─────────────────────┐
│  LLM Service        │
│  1. Generate reply  │
│  2. Apply character │
└────┬────────────────┘
     │ {"text": "Yandex Browser is ready", "language": "en"}
     ▼
┌─────────────────────┐
│  ASR Service        │
│  1. TTS synthesis   │
│  2. Play audio      │
└────┬────────────────┘
     │
     ▼
┌──────────┐
│  User    │ Hears: "Yandex Browser is ready"
└──────────┘
```

### 2. Dangerous Command Flow (with Confirmation)

```
User: "Delete file system32.dll"
  ↓
ASR Service: Recognize & parse
  ↓
LLM Service: Safety check → DANGEROUS!
  ↓
LLM Service: Generate confirmation request
  ↓
ASR Service: TTS "This is dangerous. Confirm?"
  ↓
User: "Yes, confirm"
  ↓
ASR Service: Recognize confirmation
  ↓
Command Service: Execute deletion
  ↓
LLM Service: Generate confirmation
  ↓
ASR Service: TTS "File deleted"
```

---

## Technology Stack

### ASR Service
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| ASR | Vosk | 0.3.45+ | Offline speech recognition |
| VAD | Silero VAD | 4.0.0+ | Voice activity detection |
| TTS | pyttsx3 | 2.90+ | Text-to-speech |
| Face | face-recognition + dlib | 1.3.0+ | Face detection/recognition |
| Voice ID | SpeechBrain | 0.5.16+ | Speaker identification |
| Audio I/O | sounddevice/pyaudio | 0.4.6+ | Microphone/speaker access |
| API | FastAPI | 0.104+ | REST API framework |

### LLM Service
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| LLM | llama.cpp (Python) | 0.2.0+ | Local LLM inference |
| Model | Phi-3-mini / Gemma-2 | Latest | Language understanding |
| Templates | Jinja2 | 3.1.0+ | Prompt templates |
| API | FastAPI | 0.104+ | REST API framework |

### Command Service
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Windows API | pywin32 | 306+ | System integration |
| Process Mgmt | psutil | 5.9+ | Process control |
| Fuzzy Match | rapidfuzz | 3.5+ | App name matching |
| Audio Control | pycaw | Latest | Volume/music control |
| Automation | pyautogui/keyboard | Latest | Media keys |
| API | FastAPI | 0.104+ | REST API framework |

### Shared
- **Python**: 3.10+ (all services)
- **SQLite**: User data storage
- **YAML**: Configuration files
- **pytest**: Testing framework

---

## Offline-First Design

Gerald is designed to work **completely offline** without internet:

### Model Downloads
All models downloaded once during setup:
```
shared/models/
├── asr/
│   ├── vosk-model-small-en-us-0.15/    (~100MB)
│   └── vosk-model-small-ru-0.22/       (~100MB)
├── llm/
│   └── phi-3-mini-4k-instruct-q4.gguf  (~2.3GB)
├── face/
│   └── shape_predictor_68_face_landmarks.dat (~10MB)
├── tts/
│   └── (pyttsx3 uses OS voices, no download)
└── voice/
    └── speechbrain models                (~50MB)
```

**Total storage**: ~25GB (including safety margin)

### No Internet Required
- ASR: Vosk models run locally
- LLM: llama.cpp loads local GGUF models
- TTS: Uses Windows built-in voices
- Face/Voice: OpenCV and SpeechBrain run locally

### Privacy Benefits
- No voice data sent to cloud
- No user data leaves machine
- No telemetry or analytics
- Complete user control

---

## Performance Considerations

### Resource Targets
- **CPU (Idle)**: <5% when listening
- **CPU (Active)**: <50% during command processing
- **Memory**: <4GB total for all services
- **Response Time**: <2 seconds from speech to TTS

### Optimization Strategies

#### 1. VAD Efficiency
- Use Silero VAD (lightweight, accurate)
- Process audio every 100ms (not 10ms)
- Skip ASR when no voice detected
- Save ~90% CPU during silence

#### 2. LLM Inference
- Use quantized models (Q4 format)
- Limit max tokens (100 tokens max)
- Cache common responses
- Warm start: keep model in memory

#### 3. Service Startup
- Lazy loading: load models only when first used
- Parallel initialization: start all services simultaneously
- Preload critical models (ASR, VAD)
- Defer non-critical models (face, voice ID)

#### 4. Memory Management
- Unload unused models after timeout
- Use memory-mapped model loading
- Limit conversation context (5 messages max)
- Clear audio buffers regularly

---

## Security & Privacy

### Safety Mechanisms

#### 1. Multi-Layer Safety Checks
```
User Command
    ↓
ASR: Parse intent
    ↓
LLM: Safety prompt check → BLOCK or ALLOW
    ↓
Command Service: Final validation → BLOCK or ALLOW
    ↓
Execute (if allowed)
```

#### 2. Confirmation Required
Dangerous operations always require confirmation:
- File/folder deletion
- Terminal commands
- Registry modifications
- System file operations

Configuration in `config/main_config.yaml`:
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
      - "rm -rf /"
```

#### 3. Forbidden Commands
Absolute blocks (never execute, even with confirmation):
- Format drives
- Delete system folders
- Modify critical registry keys

### Privacy Protection
- All data stored locally in SQLite
- No cloud synchronization
- No telemetry or analytics
- User can delete all data anytime
- Optional data encryption

Database location: `shared/user_data.db`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    face_encoding BLOB,
    voice_embedding BLOB,
    created_at TIMESTAMP
);
```

---

## Extensibility

### Adding New Characters
1. Create `llm_service/characters/new_character.yaml`
2. Define personality traits and system prompts
3. Set voice parameters (pitch, rate, volume)
4. No code changes required

### Adding New Services
1. Create new service directory
2. Implement FastAPI endpoints
3. Update `config/services.yaml`
4. Services automatically discover each other

### Adding New Commands
1. Add command pattern to ASR parser
2. Update LLM safety prompts
3. Implement handler in Command Service
4. Document in `docs/COMMANDS.md`

---

## Deployment Architecture

### Single Machine (Default)
All services on same Windows machine:
```
Windows PC
├── ASR Service (localhost:8001)
├── LLM Service (localhost:8002)
└── Command Service (localhost:8003)
```

### Distributed (Future)
Services on different machines:
```
PC 1 (User's machine)
└── ASR Service + Command Service

PC 2 (Powerful machine)
└── LLM Service (LLM inference)
```

### Docker (Optional)
Each service in container:
```bash
docker-compose up -d
```

---

## Conclusion

Gerald's microservice architecture provides:
- **Modularity**: Easy to develop and test independently
- **Scalability**: Can add new services/features easily
- **Performance**: Optimized for low-resource usage
- **Privacy**: Complete offline operation
- **Safety**: Multi-layer safety checks
- **Extensibility**: Easy to customize and extend

This architecture balances simplicity (for single-machine use) with flexibility (for future enhancements).

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
**Maintained by**: Agent 4 (Testing & Documentation)

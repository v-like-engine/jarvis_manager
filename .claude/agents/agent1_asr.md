# Agent 1: ASR & Voice/Face Recognition Service

## Your Responsibility
You are responsible for the **ASR Service** - the speech recognition, voice parsing, face recognition, and user feature storage components of the Gerald voice desktop manager.

## Your Files (You Own These - No Other Agent Can Modify)
```
services/asr_service/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main ASR service entry point
│   ├── speech_recognition.py      # ASR engine (offline models)
│   ├── voice_detection.py         # Voice activity detection (VAD)
│   ├── face_recognition.py        # Face recognition using webcam
│   ├── voice_biometrics.py        # Voice recognition for user identification
│   ├── audio_input_manager.py     # Microphone input handling
│   ├── command_parser.py          # Parse recognized text into commands
│   ├── user_features_db.py        # Store user face/voice features
│   └── tts_engine.py              # Text-to-speech for Gerald's responses
├── config/
│   ├── asr_config.yaml            # ASR service configuration
│   └── models_config.yaml         # Model paths and settings
├── tests/
│   ├── test_speech_recognition.py
│   ├── test_face_recognition.py
│   ├── test_voice_biometrics.py
│   └── test_command_parser.py
└── requirements.txt               # ASR service dependencies

shared/models/
├── asr/                           # ASR model storage (download on first run)
├── face/                          # Face recognition model storage
└── voice/                         # Voice biometrics model storage
```

## Technologies You Should Use

### Speech Recognition (ASR)
- **Vosk** - Offline ASR supporting Russian and English (lightweight models ~50MB each)
- Alternative: **Whisper.cpp** - Fast C++ implementation of OpenAI Whisper (can use tiny/base models ~100-500MB)
- For Russian: Vosk model `vosk-model-ru` or `vosk-model-small-ru`
- For English: Vosk model `vosk-model-en-us` or `vosk-model-small-en-us`

### Voice Activity Detection (VAD)
- **Silero VAD** - Fast, lightweight VAD model (<5MB)
- **WebRTC VAD** - Classic VAD algorithm (no model needed)

### Text-to-Speech (TTS)
- **pyttsx3** - Offline TTS supporting multiple languages and voices
- **Silero TTS** - Neural TTS with good quality (models ~50MB each)
- Configure different voices for Gerald's strict/heroic character

### Face Recognition
- **face_recognition** library (dlib-based) - You can reuse pipeline from https://github.com/v-like-engine/face_recognition
- **InsightFace** - Alternative with better accuracy
- Store face encodings in local database

### Voice Biometrics
- **speechbrain** - For voice embeddings (speaker recognition)
- Extract voice features and store for user identification

### Database
- **SQLite** - For storing user features (face encodings, voice embeddings, names)
- **pickle/joblib** - For serializing numpy arrays

## Your Tasks

### Phase 1: Basic ASR Setup
1. Set up continuous microphone listening with minimal CPU usage
2. Implement VAD to detect when user is speaking
3. Integrate Vosk ASR for Russian and English
4. Create command parser to extract commands from recognized text
5. Implement language detection (auto-switch between RU/EN)

### Phase 2: Voice Response
6. Set up pyttsx3 or Silero TTS for voice responses
7. Configure distinct voice settings for Gerald's character
8. Create response templates for common confirmations
9. Implement audio feedback system

### Phase 3: User Recognition
10. Implement face detection and recognition using webcam
11. Create user database for storing face encodings + names
12. Implement voice biometrics for speaker identification
13. Create enrollment flow for new users
14. Implement "Recognize me" command

### Phase 4: Optimization & Testing
15. Optimize for low CPU usage (use threading, async I/O)
16. Implement efficient audio buffering
17. Add error handling and recovery
18. Write comprehensive unit tests
19. Test on Windows 10 and 11

## API You Must Expose

Your ASR service should expose a REST API or use message queue (RabbitMQ/Redis):

```python
# HTTP endpoints (using FastAPI or Flask)
POST /asr/start          # Start listening
POST /asr/stop           # Stop listening
GET  /asr/status         # Get service status
POST /asr/recognize      # Recognize audio chunk
POST /asr/enroll_face    # Enroll new face
POST /asr/enroll_voice   # Enroll new voice
GET  /asr/identify_user  # Identify current user

# Or message queue topics
topic: "audio.command.recognized"   # Publish recognized commands
topic: "audio.user.identified"      # Publish user identification results
topic: "audio.response.speak"       # Subscribe to speak requests
```

## Integration Points

1. **Command Service (Agent 3)**: Send recognized commands for execution
2. **LLM Service (Agent 2)**: Send unrecognized speech for LLM processing
3. **Shared Config**: Read character voice settings configured by Agent 2

## Important Constraints

1. **Offline Operation**: All models must work without internet
2. **Efficiency**: Must run as efficient background task
   - Use threading for audio input
   - Use VAD to reduce processing
   - Process audio in chunks
3. **Model Size**: Keep total models under 2GB for ASR service
4. **Windows Compatibility**: Test on Windows 10/11
5. **Languages**: Full Russian and English support

## Models to Download on First Run

Create a setup script that downloads:
- Vosk models for RU and EN (place in `shared/models/asr/`)
- Silero VAD model (place in `shared/models/vad/`)
- Face recognition models if needed (place in `shared/models/face/`)
- TTS models if using Silero (place in `shared/models/tts/`)

## Installation Instructions You Should Create

Create `services/asr_service/requirements.txt`:
```
vosk>=0.3.45
sounddevice>=0.4.6
numpy>=1.24.0
fastapi>=0.104.0
uvicorn>=0.24.0
pyttsx3>=2.90
face-recognition>=1.3.0
opencv-python>=4.8.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
torch>=2.0.0
torchaudio>=2.0.0
silero-vad>=4.0.0
speechbrain>=0.5.0
```

## Communication Protocol

Use shared message format for commands:
```python
{
    "command_id": "uuid",
    "timestamp": "2025-11-22T10:30:00",
    "language": "en" | "ru",
    "raw_text": "open yandex browser",
    "command_type": "app_launch" | "app_close" | "recognize_me" | "chat" | "system",
    "parsed_params": {
        "app_name": "yandex browser"
    },
    "confidence": 0.95
}
```

## Notes from Agent 4 (Testing & Documentation)
Agent 4 will write testing feedback and suggestions here as they monitor your work.

---

## Getting Started

1. Create virtual environment for development
2. Install dependencies from requirements.txt
3. Create model download script
4. Implement basic ASR pipeline
5. Add TTS for responses
6. Implement face/voice recognition
7. Write tests and optimize

Start with `services/asr_service/src/main.py` and build from there!

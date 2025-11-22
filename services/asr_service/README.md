# ASR Service

**Automatic Speech Recognition Service for Gerald Desktop Manager**

The ASR Service provides comprehensive speech recognition, voice activity detection, face recognition, voice biometrics, and text-to-speech capabilities for the Gerald voice-controlled desktop manager.

## Features

- **Offline Speech Recognition**: Vosk-based ASR for English and Russian
- **Voice Activity Detection**: Silero VAD and WebRTC VAD support
- **Command Parsing**: Intelligent parsing of recognized text into structured commands
- **Text-to-Speech**: pyttsx3-based TTS with Gerald's character voice
- **Face Recognition**: Webcam-based face identification using dlib
- **Voice Biometrics**: Speaker identification using SpeechBrain embeddings
- **User Database**: SQLite storage for user biometric features

## Architecture

```
services/asr_service/
├── src/
│   ├── main.py                   # FastAPI service entry point
│   ├── audio_input_manager.py    # Microphone input handling
│   ├── voice_detection.py        # VAD implementation
│   ├── speech_recognition.py     # Vosk ASR integration
│   ├── command_parser.py         # Command parsing logic
│   ├── tts_engine.py            # Text-to-speech engine
│   ├── face_recognition.py       # Face recognition
│   ├── voice_biometrics.py       # Voice speaker ID
│   └── user_features_db.py       # User database
├── config/
│   ├── asr_config.yaml          # Service configuration
│   └── models_config.yaml       # Model settings
├── tests/                       # Unit tests
└── requirements.txt             # Dependencies
```

## Installation

### 1. Install Dependencies

```bash
cd services/asr_service
pip install -r requirements.txt
```

### 2. Download Models

```bash
python download_models.py
```

This will download:
- Vosk English model (~40 MB)
- Vosk Russian model (~45 MB)
- Silero VAD model (~2 MB)
- Face recognition models (~100 MB, optional)

Total download size: ~150-250 MB

### 3. Configuration

Edit `config/asr_config.yaml` to customize:
- Audio settings (sample rate, channels)
- VAD thresholds
- Recognition confidence thresholds
- TTS voice settings
- Face/voice recognition settings

## Usage

### Starting the Service

```bash
python src/main.py
```

Or using uvicorn:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### API Endpoints

#### Service Control

- `POST /asr/start` - Start continuous listening
- `POST /asr/stop` - Stop listening
- `GET /status` - Get service status

#### Speech Recognition

- `POST /asr/recognize` - Recognize speech from audio data

```json
{
  "audio": [float array],
  "language": "en"
}
```

#### Text-to-Speech

- `POST /asr/speak` - Speak text

```json
{
  "text": "Hello, I am Gerald",
  "language": "en",
  "blocking": false
}
```

#### User Enrollment

- `POST /asr/enroll_face` - Enroll user face

```json
{
  "name": "John Doe",
  "language_preference": "en"
}
```

#### User Identification

- `GET /asr/identify_user` - Identify user from webcam

Returns:
```json
{
  "status": "identified",
  "user_id": 1,
  "name": "John Doe",
  "confidence": 0.95
}
```

## Command Format

Commands are parsed into structured JSON:

```json
{
  "command_id": "uuid",
  "timestamp": "2025-11-22T10:30:00Z",
  "language": "en",
  "raw_text": "open yandex browser",
  "command_type": "app_launch",
  "parsed_params": {
    "app_name": "yandex browser",
    "action": "launch"
  },
  "confidence": 0.95
}
```

### Supported Command Types

- `app_launch` - Launch application
- `app_close` - Close application
- `recognize_me` - Trigger user identification
- `chat` - General chat/questions
- `system` - System commands (shutdown, restart, etc.)
- `file_op` - File operations
- `terminal` - Terminal commands
- `music_control` - Music playback control

## Examples

### English Commands

- "Open Yandex Browser" → app_launch
- "Close Chrome" → app_close
- "Recognize me" → recognize_me
- "Who are you?" → chat

### Russian Commands

- "Открой Яндекс браузер" → app_launch
- "Закрой Chrome" → app_close
- "Кто я" → recognize_me
- "Кто ты?" → chat

## Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

Run specific test:

```bash
pytest tests/test_command_parser.py -v
```

## Performance

- **CPU Usage**: <5% when idle (VAD only)
- **Memory**: ~500 MB (models loaded)
- **Latency**: <100ms for command recognition
- **Accuracy**: >90% for clear speech

## Troubleshooting

### Models not found

Run `python download_models.py` to download required models.

### Microphone not working

Check device index in config:
```yaml
audio:
  device_index: null  # null = default, or specify index
```

List available devices:
```python
from src.audio_input_manager import AudioInputManager
manager = AudioInputManager()
devices = manager.list_devices()
print(devices)
```

### Low recognition accuracy

Adjust VAD threshold:
```yaml
vad:
  threshold: 0.5  # Lower = more sensitive
```

Adjust recognition confidence:
```yaml
asr:
  confidence_threshold: 0.6  # Lower = more permissive
```

### TTS not working

Check available voices:
```python
from src.tts_engine import TextToSpeech
tts = TextToSpeech()
voices = tts.get_voices()
print(voices)
```

## Integration

The ASR service communicates with other Gerald services via REST API:

- **LLM Service**: Sends unrecognized speech for processing
- **Command Service**: Sends parsed commands for execution

## Development

### Adding new command types

1. Add to `CommandType` enum in `command_parser.py`
2. Add trigger words in config
3. Implement parsing logic in `_extract_params()`
4. Add tests

### Adding new languages

1. Download Vosk model for language
2. Add model path to config
3. Add trigger words for new language
4. Update tests

## License

Part of Gerald Desktop Manager project.

## Credits

- **Vosk**: Speech recognition - https://alphacephei.com/vosk/
- **Silero**: VAD and TTS - https://github.com/snakers4/silero-vad
- **face_recognition**: Face recognition - https://github.com/ageitgey/face_recognition
- **SpeechBrain**: Voice biometrics - https://speechbrain.github.io/
- **pyttsx3**: Text-to-speech - https://github.com/nateshmbhat/pyttsx3

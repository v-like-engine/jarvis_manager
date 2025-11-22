# Gerald Desktop Manager - API Reference

Complete REST API documentation for all Gerald services (v1.0.0)

## Table of Contents
1. [Overview](#overview)
2. [ASR Service API](#asr-service-api)
3. [LLM Service API](#llm-service-api)
4. [Command Service API](#command-service-api)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Authentication](#authentication)
8. [WebSocket Support](#websocket-support)

---

## Overview

Gerald consists of three microservices, each exposing a REST API:

| Service | Port | Base URL | Description |
|---------|------|----------|-------------|
| ASR Service | 8001 | `http://localhost:8001` | Speech recognition, TTS, face/voice ID |
| LLM Service | 8002 | `http://localhost:8002` | Natural language understanding, response generation |
| Command Service | 8003 | `http://localhost:8003` | Command execution, app control, file operations |

### API Conventions

**Content Type**: All endpoints accept and return `application/json`

**Request Format**:
```http
POST /endpoint HTTP/1.1
Host: localhost:PORT
Content-Type: application/json

{
  "parameter": "value"
}
```

**Response Format**:
```json
{
  "status": "success|error",
  "data": { ... },
  "message": "Human-readable message",
  "timestamp": "2025-11-22T10:30:00Z"
}
```

---

## ASR Service API

**Base URL**: `http://localhost:8001`

### Health Check

#### `GET /health`

Check if ASR service is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "asr_service",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

---

### Speech Recognition

#### `POST /recognize`

Convert audio to text.

**Request**:
```json
{
  "audio_data": "base64_encoded_audio",
  "language": "auto",  // "auto", "en", or "ru"
  "sample_rate": 16000,
  "format": "wav"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "text": "open chrome",
    "language": "en",
    "confidence": 0.92,
    "words": [
      {"word": "open", "start": 0.1, "end": 0.3},
      {"word": "chrome", "start": 0.4, "end": 0.7}
    ]
  },
  "message": "Recognition successful",
  "timestamp": "2025-11-22T10:30:00Z"
}
```

**Error Response**:
```json
{
  "status": "error",
  "error_code": "AUDIO_TOO_SHORT",
  "message": "Audio duration must be at least 250ms",
  "timestamp": "2025-11-22T10:30:00Z"
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8001/recognize \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "BASE64_AUDIO_HERE",
    "language": "auto"
  }'
```

---

### Command Parsing

#### `POST /parse_command`

Extract intent and parameters from recognized text.

**Request**:
```json
{
  "text": "open yandex browser",
  "language": "en"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "intent": "app_launch",
    "confidence": 0.95,
    "params": {
      "app_name": "yandex browser",
      "action": "open"
    },
    "language": "en"
  }
}
```

**Supported Intents**:
- `app_launch` - Launch application
- `app_close` - Close application
- `file_create` - Create file
- `file_delete` - Delete file
- `folder_create` - Create folder
- `folder_delete` - Delete folder
- `terminal_command` - Execute terminal command
- `music_control` - Control music playback
- `user_recognition` - Face/voice identification
- `settings_change` - Change settings
- `information_query` - Ask for information
- `gerald_control` - Control Gerald (exit, restart, etc.)

---

### Text-to-Speech

#### `POST /speak`

Convert text to speech and play audio.

**Request**:
```json
{
  "text": "Chrome is ready",
  "language": "en",  // "en" or "ru"
  "rate": 180,       // Words per minute (100-300)
  "volume": 0.9,     // 0.0 to 1.0
  "pitch": 0.5       // 0.0 to 1.0
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "duration_seconds": 1.2,
    "audio_data": "base64_encoded_audio"  // Optional
  },
  "message": "Speech synthesized and played"
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8001/speak \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, I am Gerald",
    "language": "en",
    "rate": 180,
    "volume": 0.9
  }'
```

---

### Face Recognition

#### `POST /enroll_face`

Enroll user's face for identification.

**Request**:
```json
{
  "user_name": "John Doe",
  "capture_image": true,  // true = use webcam, false = provide image
  "image_data": "base64_image"  // Required if capture_image = false
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "user_id": "user_123",
    "user_name": "John Doe",
    "enrollment_time": "2025-11-22T10:30:00Z",
    "face_encoding_length": 128
  },
  "message": "Face enrolled successfully"
}
```

#### `POST /identify_face`

Identify user from webcam or image.

**Request**:
```json
{
  "capture_image": true,
  "image_data": "base64_image"  // Optional if capture_image = true
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "identified": true,
    "user_id": "user_123",
    "user_name": "John Doe",
    "confidence": 0.87
  },
  "message": "User identified"
}
```

**Not Recognized Response**:
```json
{
  "status": "success",
  "data": {
    "identified": false,
    "message": "No matching face found"
  }
}
```

---

### Voice Recognition

#### `POST /enroll_voice`

Enroll user's voice for speaker identification.

**Request**:
```json
{
  "user_name": "John Doe",
  "audio_data": "base64_encoded_audio",
  "duration_seconds": 5.0
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "user_id": "user_123",
    "user_name": "John Doe",
    "voice_embedding_length": 512
  },
  "message": "Voice enrolled successfully"
}
```

#### `POST /identify_voice`

Identify user from voice sample.

**Request**:
```json
{
  "audio_data": "base64_encoded_audio"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "identified": true,
    "user_id": "user_123",
    "user_name": "John Doe",
    "confidence": 0.82
  }
}
```

---

## LLM Service API

**Base URL**: `http://localhost:8002`

### Health Check

#### `GET /health`

Check if LLM service is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "llm_service",
  "version": "1.0.0",
  "model_loaded": true,
  "model_name": "phi-3-mini"
}
```

---

### Generate Response

#### `POST /generate`

Generate natural language response.

**Request**:
```json
{
  "user_input": "open chrome",
  "context": {
    "language": "en",
    "user_name": "John",
    "previous_messages": [
      {"role": "user", "content": "who are you?"},
      {"role": "assistant", "content": "I am Gerald, your desktop manager"}
    ]
  },
  "scenario": "command_confirmation",  // See scenarios below
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 100
  }
}
```

**Scenarios**:
- `command_confirmation` - Confirm command execution
- `error_explanation` - Explain error to user
- `information_response` - Answer information query
- `greeting` - Greet user
- `self_description` - Describe Gerald's capabilities
- `dangerous_warning` - Warn about dangerous operation

**Response**:
```json
{
  "status": "success",
  "data": {
    "response_text": "Chrome is ready",
    "language": "en",
    "should_speak": true,
    "tokens_used": 12,
    "inference_time_ms": 450
  }
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "who are you?",
    "context": {"language": "en"},
    "scenario": "self_description"
  }'
```

---

### Safety Check

#### `POST /safety_check`

Check if command is safe to execute.

**Request**:
```json
{
  "command_intent": "file_delete",
  "command_params": {
    "file_path": "C:\\Users\\John\\Documents\\old_notes.txt"
  },
  "language": "en"
}
```

**Response (Safe)**:
```json
{
  "status": "success",
  "data": {
    "is_safe": true,
    "requires_confirmation": true,
    "reason": "File deletion requires user confirmation",
    "suggested_confirmation_text": "This will permanently delete old_notes.txt. Confirm deletion?"
  }
}
```

**Response (Dangerous)**:
```json
{
  "status": "success",
  "data": {
    "is_safe": false,
    "blocked": true,
    "reason": "System file protection: Cannot delete Windows system files",
    "alternative_suggestion": null
  }
}
```

---

### Character Management

#### `GET /character`

Get current character information.

**Response**:
```json
{
  "status": "success",
  "data": {
    "name": "Gerald",
    "archetype": "Loyal Knight",
    "personality_traits": ["strict", "heroic", "helpful", "direct"],
    "voice_settings": {
      "pitch": 0.4,
      "rate": 180,
      "volume": 0.9
    },
    "language_support": ["en", "ru"]
  }
}
```

#### `POST /set_character`

Switch to different character.

**Request**:
```json
{
  "character_name": "gerald"  // "gerald", "jarvis", "friday"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "previous_character": "jarvis",
    "current_character": "gerald"
  },
  "message": "Character switched to Gerald"
}
```

---

## Command Service API

**Base URL**: `http://localhost:8003`

### Health Check

#### `GET /health`

Check if Command service is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "command_service",
  "version": "1.0.0",
  "modules_loaded": ["app_launcher", "file_ops", "terminal", "music_control", "settings"]
}
```

---

### Execute Command

#### `POST /execute`

Execute a parsed command.

**Request**:
```json
{
  "intent": "app_launch",
  "params": {
    "app_name": "chrome"
  },
  "user_id": "user_123",
  "confirmed": false  // true if user confirmed dangerous operation
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "intent": "app_launch",
    "result": {
      "app_name": "Google Chrome",
      "process_id": 12345,
      "launched": true
    }
  },
  "message": "Application launched successfully"
}
```

**Response (Needs Confirmation)**:
```json
{
  "status": "needs_confirmation",
  "data": {
    "confirmation_required": true,
    "confirmation_message": "This will delete file important.txt. Confirm deletion?",
    "command_id": "cmd_789"
  }
}
```

**To confirm**, make the same request with:
```json
{
  "intent": "file_delete",
  "params": {...},
  "confirmed": true,
  "command_id": "cmd_789"
}
```

---

### Application Control

#### `POST /app/launch`

Launch an application.

**Request**:
```json
{
  "app_name": "chrome",
  "fuzzy_match": true  // Enable fuzzy matching
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "app_name": "Google Chrome",
    "app_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "process_id": 12345,
    "launched_at": "2025-11-22T10:30:00Z"
  }
}
```

#### `POST /app/close`

Close a running application.

**Request**:
```json
{
  "app_name": "chrome",
  "force_close": false  // true = kill process immediately
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "app_name": "Google Chrome",
    "process_id": 12345,
    "closed": true
  }
}
```

#### `GET /app/list`

List all running applications.

**Response**:
```json
{
  "status": "success",
  "data": {
    "applications": [
      {
        "name": "Google Chrome",
        "process_id": 12345,
        "memory_mb": 450,
        "cpu_percent": 2.5
      },
      {
        "name": "Visual Studio Code",
        "process_id": 23456,
        "memory_mb": 380,
        "cpu_percent": 1.2
      }
    ],
    "total_count": 2
  }
}
```

---

### File Operations

#### `POST /file/create`

Create a new file.

**Request**:
```json
{
  "file_path": "C:\\Users\\John\\Documents\\notes.txt",
  "content": "Hello World",  // Optional initial content
  "overwrite": false
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "file_path": "C:\\Users\\John\\Documents\\notes.txt",
    "created": true,
    "size_bytes": 11
  }
}
```

#### `POST /file/delete`

Delete a file (requires confirmation).

**Request**:
```json
{
  "file_path": "C:\\Users\\John\\Documents\\old_notes.txt",
  "confirmed": false
}
```

**Response** (if confirmed = false):
```json
{
  "status": "needs_confirmation",
  "data": {
    "file_path": "C:\\Users\\John\\Documents\\old_notes.txt",
    "file_size_bytes": 1024,
    "confirmation_required": true
  }
}
```

#### `POST /folder/create`

Create a new folder.

**Request**:
```json
{
  "folder_path": "C:\\Users\\John\\Documents\\Projects"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "folder_path": "C:\\Users\\John\\Documents\\Projects",
    "created": true
  }
}
```

---

### Terminal Execution

#### `POST /terminal/execute`

Execute a terminal command (requires confirmation for most commands).

**Request**:
```json
{
  "command": "ipconfig",
  "shell": "cmd",  // "cmd" or "powershell"
  "timeout_seconds": 30,
  "confirmed": false
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "command": "ipconfig",
    "output": "Windows IP Configuration\n\nEthernet adapter...",
    "exit_code": 0,
    "execution_time_ms": 234
  }
}
```

**Forbidden Command Response**:
```json
{
  "status": "error",
  "error_code": "FORBIDDEN_COMMAND",
  "message": "This command is forbidden for safety reasons",
  "data": {
    "command": "format C:",
    "reason": "Would damage system"
  }
}
```

---

### Music Control

#### `POST /music/play`

Control music playback.

**Request**:
```json
{
  "action": "play",  // "play", "pause", "next", "previous", "stop"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "action": "play",
    "executed": true
  }
}
```

#### `POST /music/volume`

Control volume.

**Request**:
```json
{
  "action": "up",  // "up", "down", "set", "mute", "unmute"
  "value": 10  // Optional: volume level (0-100) for "set" action
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "action": "up",
    "current_volume": 65
  }
}
```

---

### Settings Management

#### `GET /settings`

Get all settings.

**Response**:
```json
{
  "status": "success",
  "data": {
    "language": "en",
    "auto_start": true,
    "voice_settings": {
      "rate": 180,
      "volume": 0.9,
      "pitch": 0.5
    },
    "vad_sensitivity": 0.5
  }
}
```

#### `POST /settings/update`

Update a setting.

**Request**:
```json
{
  "setting_name": "language",
  "setting_value": "ru"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "setting_name": "language",
    "old_value": "en",
    "new_value": "ru"
  },
  "message": "Setting updated successfully"
}
```

---

## Error Handling

### Error Response Format

All services use consistent error responses:

```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  },
  "timestamp": "2025-11-22T10:30:00Z"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request body |
| `MISSING_PARAMETER` | 400 | Required parameter missing |
| `AUTHENTICATION_FAILED` | 401 | Auth token invalid/missing |
| `FORBIDDEN_COMMAND` | 403 | Command blocked for safety |
| `RESOURCE_NOT_FOUND` | 404 | Resource doesn't exist |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Example Error Response

```json
{
  "status": "error",
  "error_code": "MISSING_PARAMETER",
  "message": "Required parameter 'audio_data' is missing",
  "details": {
    "parameter": "audio_data",
    "expected_type": "string (base64)"
  },
  "timestamp": "2025-11-22T10:30:00Z"
}
```

---

## Rate Limiting

Currently, no rate limiting is enforced for local services.

Future versions may implement:
- Max 100 requests per minute per client
- Max 10 concurrent requests
- Throttling for expensive operations (LLM inference)

---

## Authentication

**v1.0.0**: No authentication required (local-only services)

**Future versions** may add:
- API keys for external access
- JWT tokens for session management
- OAuth2 for third-party integrations

---

## WebSocket Support

**Coming in v1.1.0**

Planned WebSocket endpoints for real-time communication:

```javascript
// ASR Service - Real-time audio streaming
ws://localhost:8001/ws/stream

// LLM Service - Streaming responses
ws://localhost:8002/ws/generate

// Command Service - Command status updates
ws://localhost:8003/ws/status
```

---

## SDKs and Libraries

### Python Client

```python
from gerald_client import GeraldClient

# Initialize client
client = GeraldClient(
    asr_url="http://localhost:8001",
    llm_url="http://localhost:8002",
    command_url="http://localhost:8003"
)

# Speech recognition
result = client.asr.recognize(audio_data, language="auto")

# Generate response
response = client.llm.generate("open chrome", scenario="command_confirmation")

# Execute command
client.commands.execute(intent="app_launch", params={"app_name": "chrome"})
```

### JavaScript Client

```javascript
const GeraldClient = require('gerald-client-js');

const client = new GeraldClient({
  asrUrl: 'http://localhost:8001',
  llmUrl: 'http://localhost:8002',
  commandUrl: 'http://localhost:8003'
});

// Speech recognition
const result = await client.asr.recognize(audioData, 'auto');

// Generate response
const response = await client.llm.generate('open chrome', 'command_confirmation');

// Execute command
await client.commands.execute('app_launch', { app_name: 'chrome' });
```

**Note**: Official SDKs coming in v1.1.0

---

## Testing APIs

### Using curl

```bash
# Health check
curl http://localhost:8001/health

# Recognize speech
curl -X POST http://localhost:8001/recognize \
  -H "Content-Type: application/json" \
  -d '{"audio_data":"BASE64","language":"auto"}'

# Generate response
curl -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{"user_input":"who are you?","scenario":"self_description"}'

# Launch app
curl -X POST http://localhost:8003/app/launch \
  -H "Content-Type: application/json" \
  -d '{"app_name":"chrome"}'
```

### Using Postman

1. Import collection: `docs/postman/gerald_api_collection.json` (coming soon)
2. Set environment variables
3. Run tests

### Using Python

```python
import requests

# ASR - Recognize speech
response = requests.post('http://localhost:8001/recognize', json={
    "audio_data": "BASE64_AUDIO",
    "language": "auto"
})
print(response.json())

# LLM - Generate response
response = requests.post('http://localhost:8002/generate', json={
    "user_input": "open chrome",
    "scenario": "command_confirmation"
})
print(response.json())

# Command - Launch app
response = requests.post('http://localhost:8003/app/launch', json={
    "app_name": "chrome"
})
print(response.json())
```

---

## Changelog

### v1.0.0 (2025-11-22)
- Initial API release
- All core endpoints implemented
- REST API for all three services

### Planned for v1.1.0
- WebSocket support
- Official Python/JavaScript SDKs
- API authentication
- Rate limiting
- Batch operations

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development guidelines
- [USER_GUIDE.md](USER_GUIDE.md) - User documentation

---

**Last Updated**: 2025-11-22
**API Version**: 1.0.0
**Maintained by**: Agent 4 (Testing & Documentation)

"""
ASR Service Main Module

FastAPI service that provides speech recognition, voice/face recognition,
and text-to-speech capabilities for the Gerald Desktop Manager.
"""

import os
import sys
import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Import ASR modules
from audio_input_manager import AudioInputManager
from voice_detection import VoiceActivityDetector, SpeechSegmenter
from speech_recognition import SpeechRecognizer
from command_parser import CommandParser
from tts_engine import TextToSpeech, GeraldVoice, CharacterVoiceProfile
from face_recognition import FaceRecognizer
from voice_biometrics import VoiceBiometrics, SpeakerVerifier
from user_features_db import UserFeaturesDB


# Pydantic models for API
class RecognitionResult(BaseModel):
    """Speech recognition result"""
    text: str
    language: str
    confidence: float
    success: bool


class CommandResult(BaseModel):
    """Parsed command result"""
    command_id: str
    timestamp: str
    language: str
    raw_text: str
    command_type: str
    parsed_params: Dict[str, Any]
    confidence: float


class SpeakRequest(BaseModel):
    """Text-to-speech request"""
    text: str
    language: Optional[str] = "en"
    blocking: bool = False


class UserEnrollmentRequest(BaseModel):
    """User enrollment request"""
    name: str
    language_preference: Optional[str] = "en"


class ServiceStatus(BaseModel):
    """Service status"""
    is_running: bool
    is_listening: bool
    audio_stats: Dict[str, Any]
    available_languages: List[str]
    users_count: int
    active_character: Optional[str] = "gerald"


class SetCharacterRequest(BaseModel):
    """Set character request"""
    character_id: str
    language: Optional[str] = "en"


class CharacterInfo(BaseModel):
    """Character information"""
    character_id: str
    name: str
    description: str
    voice_settings: Dict[str, Any]


class TestVoiceRequest(BaseModel):
    """Test voice request"""
    character_id: str
    language: Optional[str] = "en"
    test_text: Optional[str] = None


# Global service state
class ASRServiceState:
    """Global state for ASR service"""

    def __init__(self):
        self.config: Optional[Dict[str, Any]] = None
        self.audio_manager: Optional[AudioInputManager] = None
        self.vad: Optional[VoiceActivityDetector] = None
        self.speech_segmenter: Optional[SpeechSegmenter] = None
        self.speech_recognizer: Optional[SpeechRecognizer] = None
        self.command_parser: Optional[CommandParser] = None
        self.tts_en: Optional[TextToSpeech] = None
        self.tts_ru: Optional[TextToSpeech] = None
        self.face_recognizer: Optional[FaceRecognizer] = None
        self.voice_biometrics: Optional[VoiceBiometrics] = None
        self.user_db: Optional[UserFeaturesDB] = None

        self.is_listening = False
        self.listening_thread: Optional[threading.Thread] = None
        self.stop_listening = False

        # Command callback
        self.command_callback = None

        # Character management
        self.active_character: str = "gerald"
        self.character_tts_engines: Dict[str, Dict[str, TextToSpeech]] = {}
        # Structure: {"character_id": {"en": TextToSpeech, "ru": TextToSpeech}}


# Create global state
state = ASRServiceState()


# Initialize FastAPI app
app = FastAPI(
    title="Gerald ASR Service",
    description="Speech recognition and voice/face recognition service",
    version="1.0.0"
)


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML files"""
    # Load main config
    main_config_path = "config/main_config.yaml"
    asr_config_path = "services/asr_service/config/asr_config.yaml"

    config = {}

    # Load main config
    if os.path.exists(main_config_path):
        with open(main_config_path, 'r') as f:
            main_config = yaml.safe_load(f)
            config.update(main_config.get('asr', {}))

    # Load ASR-specific config
    if os.path.exists(asr_config_path):
        with open(asr_config_path, 'r') as f:
            asr_config = yaml.safe_load(f)
            config.update(asr_config)

    return config


async def initialize_service():
    """Initialize all ASR service components"""
    logger.info("Initializing ASR service...")

    # Load configuration
    state.config = load_config()

    # Initialize audio manager
    audio_config = state.config.get('audio', {})
    state.audio_manager = AudioInputManager(
        sample_rate=audio_config.get('sample_rate', 16000),
        channels=audio_config.get('channels', 1),
        chunk_size=audio_config.get('chunk_size', 1024),
        buffer_seconds=audio_config.get('buffer_seconds', 0.5)
    )

    # Initialize VAD
    vad_config = state.config.get('vad', {})
    state.vad = VoiceActivityDetector(
        engine=vad_config.get('engine', 'silero'),
        sample_rate=audio_config.get('sample_rate', 16000),
        threshold=vad_config.get('threshold', 0.5),
        min_speech_duration_ms=vad_config.get('min_speech_duration_ms', 250),
        max_speech_duration_s=vad_config.get('max_speech_duration_s', 30),
        padding_duration_ms=vad_config.get('padding_duration_ms', 300)
    )

    # Initialize speech segmenter
    state.speech_segmenter = SpeechSegmenter(
        vad=state.vad,
        min_speech_duration_ms=vad_config.get('min_speech_duration_ms', 250),
        max_speech_duration_s=vad_config.get('max_speech_duration_s', 30),
        padding_duration_ms=vad_config.get('padding_duration_ms', 300)
    )

    # Initialize speech recognizer
    asr_config = state.config.get('asr', {})
    models_config = asr_config.get('models', {})

    state.speech_recognizer = SpeechRecognizer(
        model_path_en=models_config.get('en', {}).get('path', 'shared/models/asr/vosk-model-small-en-us-0.15'),
        model_path_ru=models_config.get('ru', {}).get('path', 'shared/models/asr/vosk-model-small-ru-0.22'),
        sample_rate=audio_config.get('sample_rate', 16000),
        default_language=asr_config.get('default_language', 'en'),
        auto_detect_language=asr_config.get('auto_detect_language', True),
        confidence_threshold=asr_config.get('confidence_threshold', 0.6)
    )

    # Initialize command parser
    command_config = state.config.get('commands', {})
    state.command_parser = CommandParser(config=command_config)

    # Initialize TTS engines
    tts_config = state.config.get('tts', {})
    state.tts_en = GeraldVoice.create_english()
    state.tts_ru = GeraldVoice.create_russian()

    # Initialize face recognizer
    face_config = state.config.get('face_recognition', {})
    if face_config.get('enabled', True):
        state.face_recognizer = FaceRecognizer(
            camera_index=face_config.get('camera_index', 0),
            detection_method=face_config.get('detection_method', 'hog'),
            tolerance=face_config.get('tolerance', 0.6),
            num_jitters=face_config.get('num_jitters', 1),
            min_face_size=face_config.get('min_face_size', 80),
            capture_timeout=face_config.get('capture_timeout', 10)
        )

    # Initialize voice biometrics
    voice_config = state.config.get('voice_biometrics', {})
    if voice_config.get('enabled', False):
        try:
            state.voice_biometrics = VoiceBiometrics(
                model_name=voice_config.get('model', 'speechbrain/spkrec-ecapa-voxceleb'),
                similarity_threshold=voice_config.get('similarity_threshold', 0.7),
                embedding_dim=voice_config.get('embedding_dim', 192)
            )
        except Exception as e:
            logger.warning(f"Voice biometrics initialization failed: {e}")
            state.voice_biometrics = None

    # Initialize user database
    db_config = state.config.get('database', {})
    state.user_db = UserFeaturesDB(
        db_path=db_config.get('path', 'shared/user_data.db'),
        async_mode=True
    )
    await state.user_db.initialize_async()

    logger.info("ASR service initialized successfully")


async def shutdown_service():
    """Shutdown ASR service"""
    logger.info("Shutting down ASR service...")

    # Stop listening
    if state.is_listening:
        await stop_listening()

    # Cleanup components
    if state.audio_manager:
        state.audio_manager.stop()

    if state.tts_en:
        state.tts_en.shutdown()

    if state.tts_ru:
        state.tts_ru.shutdown()

    if state.face_recognizer:
        state.face_recognizer.close_camera()

    if state.user_db:
        await state.user_db.close_async()

    logger.info("ASR service shutdown complete")


@app.on_event("startup")
async def startup_event():
    """FastAPI startup event"""
    await initialize_service()


@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI shutdown event"""
    await shutdown_service()


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Gerald ASR Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/status", response_model=ServiceStatus)
async def get_status():
    """Get service status"""
    audio_stats = state.audio_manager.get_stats() if state.audio_manager else {}
    available_languages = state.speech_recognizer.get_available_languages() if state.speech_recognizer else []

    # Count users
    users = await state.user_db.get_all_users_async() if state.user_db else []

    return ServiceStatus(
        is_running=True,
        is_listening=state.is_listening,
        audio_stats=audio_stats,
        available_languages=available_languages,
        users_count=len(users),
        active_character=state.active_character
    )


@app.post("/asr/start")
async def start_listening():
    """Start continuous listening"""
    if state.is_listening:
        return {"status": "already_listening"}

    # Start audio input
    state.audio_manager.start()
    state.is_listening = True
    state.stop_listening = False

    # Start listening thread
    state.listening_thread = threading.Thread(target=listening_worker, daemon=True)
    state.listening_thread.start()

    logger.info("Started listening")
    return {"status": "started"}


@app.post("/asr/stop")
async def stop_listening():
    """Stop continuous listening"""
    if not state.is_listening:
        return {"status": "not_listening"}

    state.stop_listening = True
    state.is_listening = False

    # Wait for thread to stop
    if state.listening_thread:
        state.listening_thread.join(timeout=2.0)

    # Stop audio input
    if state.audio_manager:
        state.audio_manager.stop()

    logger.info("Stopped listening")
    return {"status": "stopped"}


@app.post("/asr/recognize", response_model=RecognitionResult)
async def recognize_audio(audio_data: Dict[str, Any]):
    """
    Recognize speech from audio data.

    Request body:
    {
        "audio": [float array],
        "language": "en" or "ru" (optional)
    }
    """
    if not state.speech_recognizer:
        raise HTTPException(status_code=503, detail="Speech recognizer not initialized")

    # Extract audio data
    audio_array = np.array(audio_data.get('audio', []), dtype=np.float32)
    language = audio_data.get('language')

    if len(audio_array) == 0:
        raise HTTPException(status_code=400, detail="No audio data provided")

    # Recognize
    result = state.speech_recognizer.recognize(audio_array, language)

    return RecognitionResult(**result)


@app.post("/asr/speak")
async def speak_text(request: SpeakRequest):
    """Speak text using TTS"""
    if request.language == "ru":
        tts = state.tts_ru
    else:
        tts = state.tts_en

    if not tts:
        raise HTTPException(status_code=503, detail="TTS engine not initialized")

    tts.speak(request.text, blocking=request.blocking)

    return {"status": "speaking", "text": request.text}


@app.post("/asr/enroll_face")
async def enroll_face(request: UserEnrollmentRequest):
    """Enroll user face"""
    if not state.face_recognizer:
        raise HTTPException(status_code=503, detail="Face recognizer not available")

    # Capture and enroll face
    encodings = state.face_recognizer.enroll_user(request.name, num_samples=3)

    if not encodings:
        raise HTTPException(status_code=500, detail="Failed to capture face")

    # Average encodings
    face_encoding = np.mean(encodings, axis=0)

    # Store in database
    user_id = await state.user_db.add_user_async(
        name=request.name,
        face_encoding=face_encoding,
        language_preference=request.language_preference
    )

    return {
        "status": "enrolled",
        "user_id": user_id,
        "name": request.name,
        "samples_captured": len(encodings)
    }


@app.get("/asr/identify_user")
async def identify_user():
    """Identify user using face recognition"""
    if not state.face_recognizer:
        raise HTTPException(status_code=503, detail="Face recognizer not available")

    # Get known face encodings from database
    known_encodings = await state.user_db.get_all_face_encodings_async()

    if not known_encodings:
        raise HTTPException(status_code=404, detail="No enrolled users found")

    # Identify user
    result = state.face_recognizer.identify_user(known_encodings)

    if result is None:
        return {"status": "no_match", "user_id": None}

    user_id, confidence = result

    # Update last seen
    await state.user_db.update_last_seen_async(user_id)

    # Get user info
    user = await state.user_db.get_user_by_id_async(user_id)

    return {
        "status": "identified",
        "user_id": user_id,
        "name": user['name'],
        "confidence": confidence
    }


@app.get("/users")
async def get_users():
    """Get all enrolled users"""
    users = await state.user_db.get_all_users_async()
    return {"users": users}


# Character Management Endpoints

@app.get("/asr/characters")
async def get_characters():
    """
    Get list of available characters with their voice profiles.

    Returns:
        List of available characters with voice settings
    """
    characters = []

    for char_id in CharacterVoiceProfile.get_available_characters():
        profile = CharacterVoiceProfile.get_profile(char_id)

        if profile:
            characters.append(CharacterInfo(
                character_id=char_id,
                name=profile["name"],
                description=profile["description"],
                voice_settings={
                    "english": profile["en"],
                    "russian": profile["ru"]
                }
            ))

    return {
        "characters": characters,
        "active_character": state.active_character
    }


@app.post("/asr/set_character")
async def set_character(request: SetCharacterRequest):
    """
    Switch active character for TTS.

    Args:
        request: Character ID and language

    Returns:
        Status and character information
    """
    character_id = request.character_id.lower()
    language = request.language

    # Validate character
    profile = CharacterVoiceProfile.get_profile(character_id)
    if not profile:
        available = CharacterVoiceProfile.get_available_characters()
        raise HTTPException(
            status_code=400,
            detail=f"Invalid character ID: {character_id}. Available: {available}"
        )

    # Create TTS engines for this character if not already created
    if character_id not in state.character_tts_engines:
        state.character_tts_engines[character_id] = {
            "en": CharacterVoiceProfile.create_voice(character_id, "en"),
            "ru": CharacterVoiceProfile.create_voice(character_id, "ru")
        }

    # Update active character
    state.active_character = character_id

    # Update main TTS engines to point to new character
    state.tts_en = state.character_tts_engines[character_id]["en"]
    state.tts_ru = state.character_tts_engines[character_id]["ru"]

    logger.info(f"Switched to character: {character_id} ({profile['name']})")

    return {
        "status": "success",
        "character_id": character_id,
        "character_name": profile["name"],
        "description": profile["description"],
        "language": language
    }


@app.post("/asr/test_voice")
async def test_voice(request: TestVoiceRequest):
    """
    Test character voice by speaking sample text.

    Args:
        request: Character ID, language, and optional test text

    Returns:
        Status of voice test
    """
    character_id = request.character_id.lower()
    language = request.language

    # Validate character
    profile = CharacterVoiceProfile.get_profile(character_id)
    if not profile:
        available = CharacterVoiceProfile.get_available_characters()
        raise HTTPException(
            status_code=400,
            detail=f"Invalid character ID: {character_id}. Available: {available}"
        )

    # Get or create TTS engine for this character
    if character_id not in state.character_tts_engines:
        state.character_tts_engines[character_id] = {
            "en": CharacterVoiceProfile.create_voice(character_id, "en"),
            "ru": CharacterVoiceProfile.create_voice(character_id, "ru")
        }

    tts = state.character_tts_engines[character_id].get(language)
    if not tts:
        raise HTTPException(
            status_code=400,
            detail=f"Language {language} not available for character {character_id}"
        )

    # Default test texts for each character
    default_test_texts = {
        "gerald": {
            "en": "I am Gerald, your loyal virtual assistant. Ready to serve.",
            "ru": "Я Джеральд, ваш верный виртуальный помощник. Готов служить."
        },
        "winnie": {
            "en": "Oh bother. Think, think, think. Perhaps a little something to help me think.",
            "ru": "Ох, беспокойство. Думай, думай, думай. Может быть, что-нибудь сладенькое поможет мне думать."
        },
        "rapunzel": {
            "en": "Hello! I'm Rapunzel! This is so exciting! Let's explore the world together!",
            "ru": "Привет! Я Рапунцель! Это так увлекательно! Давайте вместе исследовать мир!"
        },
        "terminator": {
            "en": "I am Terminator. Mission objectives identified. Ready for execution.",
            "ru": "Я Терминатор. Цели миссии определены. Готов к выполнению."
        }
    }

    # Use custom text or default
    test_text = request.test_text
    if not test_text:
        test_text = default_test_texts.get(character_id, {}).get(language, "Test voice.")

    # Speak test text
    tts.speak(test_text, blocking=False)

    logger.info(f"Testing voice for {character_id} ({language}): {test_text}")

    return {
        "status": "speaking",
        "character_id": character_id,
        "character_name": profile["name"],
        "language": language,
        "test_text": test_text,
        "voice_settings": profile[language] if language in ["en", "ru"] else profile["english"]
    }


def listening_worker():
    """Background worker for continuous listening"""
    logger.info("Listening worker started")

    while not state.stop_listening:
        # Get audio chunk
        audio_chunk = state.audio_manager.get_chunk(timeout=0.5)

        if audio_chunk is None:
            continue

        # Process with speech segmenter
        speech_segment = state.speech_segmenter.process_frame(audio_chunk)

        if speech_segment is not None and len(speech_segment) > 0:
            # We have a complete speech segment
            logger.info(f"Processing speech segment: {len(speech_segment)} samples")

            # Recognize speech
            result = state.speech_recognizer.recognize(speech_segment)

            if result['success']:
                logger.info(f"Recognized: '{result['text']}' ({result['language']})")

                # Parse command
                command = state.command_parser.parse(
                    result['text'],
                    result['language'],
                    result['confidence']
                )

                logger.info(f"Command: {command['command_type']}")

                # Handle command (send to command service or callback)
                if state.command_callback:
                    state.command_callback(command)

                # Provide audio feedback (optional)
                # state.tts_en.speak_async("Command received")

    logger.info("Listening worker stopped")


if __name__ == "__main__":
    import uvicorn

    # Configure logging
    logger.add(
        "logs/asr_service.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )

    # Run service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

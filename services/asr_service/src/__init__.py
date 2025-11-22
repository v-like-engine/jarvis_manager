"""
ASR Service Package

Provides speech recognition, voice activity detection, face recognition,
voice biometrics, and text-to-speech capabilities.
"""

__version__ = "1.0.0"

from .audio_input_manager import AudioInputManager
from .voice_detection import VoiceActivityDetector, SpeechSegmenter
from .speech_recognition import SpeechRecognizer, StreamingRecognizer
from .command_parser import CommandParser, CommandType
from .tts_engine import TextToSpeech, GeraldVoice
from .face_recognition import FaceRecognizer
from .voice_biometrics import VoiceBiometrics, SpeakerVerifier
from .user_features_db import UserFeaturesDB

__all__ = [
    "AudioInputManager",
    "VoiceActivityDetector",
    "SpeechSegmenter",
    "SpeechRecognizer",
    "StreamingRecognizer",
    "CommandParser",
    "CommandType",
    "TextToSpeech",
    "GeraldVoice",
    "FaceRecognizer",
    "VoiceBiometrics",
    "SpeakerVerifier",
    "UserFeaturesDB",
]

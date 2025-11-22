"""
Speech Recognition Module

Offline speech recognition using Vosk ASR for Russian and English.
Supports real-time and batch recognition with automatic language detection.
"""

import os
import json
from typing import Optional, Dict, Any, List
from enum import Enum
import numpy as np
from loguru import logger

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("Vosk is not installed. Install with: pip install vosk")

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger.warning("langdetect not available, language detection disabled")


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    RUSSIAN = "ru"


class SpeechRecognizer:
    """
    Offline speech recognizer using Vosk.

    Supports multiple languages with automatic detection.
    Optimized for command recognition with confidence scoring.
    """

    def __init__(
        self,
        model_path_en: str = "shared/models/asr/vosk-model-small-en-us-0.15",
        model_path_ru: str = "shared/models/asr/vosk-model-small-ru-0.22",
        sample_rate: int = 16000,
        default_language: str = "en",
        auto_detect_language: bool = True,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize speech recognizer.

        Args:
            model_path_en: Path to English Vosk model
            model_path_ru: Path to Russian Vosk model
            sample_rate: Audio sample rate
            default_language: Default language if detection fails
            auto_detect_language: Enable automatic language detection
            confidence_threshold: Minimum confidence for valid recognition
        """
        if not VOSK_AVAILABLE:
            raise RuntimeError("Vosk is not installed. Install with: pip install vosk")

        self.sample_rate = sample_rate
        self.default_language = Language(default_language)
        self.auto_detect_language = auto_detect_language
        self.confidence_threshold = confidence_threshold

        # Load models
        self.models: Dict[Language, Model] = {}
        self.recognizers: Dict[Language, KaldiRecognizer] = {}

        # Load English model
        if os.path.exists(model_path_en):
            logger.info(f"Loading English model from {model_path_en}")
            self.models[Language.ENGLISH] = Model(model_path_en)
            self.recognizers[Language.ENGLISH] = KaldiRecognizer(
                self.models[Language.ENGLISH],
                sample_rate
            )
            logger.info("English model loaded successfully")
        else:
            logger.warning(f"English model not found at {model_path_en}")

        # Load Russian model
        if os.path.exists(model_path_ru):
            logger.info(f"Loading Russian model from {model_path_ru}")
            self.models[Language.RUSSIAN] = Model(model_path_ru)
            self.recognizers[Language.RUSSIAN] = KaldiRecognizer(
                self.models[Language.RUSSIAN],
                sample_rate
            )
            logger.info("Russian model loaded successfully")
        else:
            logger.warning(f"Russian model not found at {model_path_ru}")

        if not self.models:
            raise RuntimeError("No Vosk models loaded. Please download models first.")

        logger.info(
            f"SpeechRecognizer initialized: "
            f"languages={list(self.models.keys())}, "
            f"default={default_language}, "
            f"auto_detect={auto_detect_language}"
        )

    def recognize(
        self,
        audio: np.ndarray,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recognize speech from audio.

        Args:
            audio: Audio data as numpy array (float32, mono)
            language: Language code ("en" or "ru"), None for auto-detection

        Returns:
            Dictionary with recognition results:
            {
                "text": str,
                "language": str,
                "confidence": float,
                "success": bool,
                "partial": bool
            }
        """
        # Determine language
        if language:
            lang = Language(language)
        elif self.auto_detect_language and len(self.models) > 1:
            # Try to detect language by recognizing with both models
            lang = self._detect_language_by_recognition(audio)
        else:
            lang = self.default_language

        # Check if model is available
        if lang not in self.recognizers:
            logger.error(f"Model for language {lang.value} not available")
            return {
                "text": "",
                "language": lang.value,
                "confidence": 0.0,
                "success": False,
                "partial": False
            }

        # Convert audio to int16 PCM
        audio_int16 = self._convert_to_int16(audio)

        # Reset recognizer
        recognizer = self.recognizers[lang]
        recognizer.Reset()

        # Feed audio to recognizer
        recognizer.AcceptWaveform(audio_int16.tobytes())

        # Get final result
        result_json = recognizer.FinalResult()
        result = json.loads(result_json)

        # Extract text and confidence
        text = result.get("text", "").strip()

        # Calculate confidence (Vosk doesn't always provide it)
        # If alternatives are available, use the best one
        if "result" in result and result["result"]:
            # Average confidence of words
            confidences = [word.get("conf", 0.0) for word in result["result"]]
            confidence = sum(confidences) / len(confidences) if confidences else 0.0
        else:
            # No detailed results, estimate from text presence
            confidence = 0.5 if text else 0.0

        success = bool(text) and confidence >= self.confidence_threshold

        return {
            "text": text,
            "language": lang.value,
            "confidence": confidence,
            "success": success,
            "partial": False,
            "raw_result": result
        }

    def recognize_partial(
        self,
        audio: np.ndarray,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recognize partial speech (for real-time recognition).

        Args:
            audio: Audio chunk
            language: Language code

        Returns:
            Partial recognition result
        """
        # Determine language
        lang = Language(language) if language else self.default_language

        if lang not in self.recognizers:
            return {
                "text": "",
                "language": lang.value,
                "confidence": 0.0,
                "success": False,
                "partial": True
            }

        # Convert audio to int16
        audio_int16 = self._convert_to_int16(audio)

        # Feed audio
        recognizer = self.recognizers[lang]
        recognizer.AcceptWaveform(audio_int16.tobytes())

        # Get partial result
        partial_result_json = recognizer.PartialResult()
        result = json.loads(partial_result_json)

        text = result.get("partial", "").strip()

        return {
            "text": text,
            "language": lang.value,
            "confidence": 0.5,  # Partial results don't have confidence
            "success": bool(text),
            "partial": True
        }

    def _detect_language_by_recognition(self, audio: np.ndarray) -> Language:
        """
        Detect language by trying recognition with multiple models.

        Args:
            audio: Audio data

        Returns:
            Detected language
        """
        best_lang = self.default_language
        best_confidence = 0.0

        # Try each available model
        for lang, recognizer in self.recognizers.items():
            recognizer.Reset()
            audio_int16 = self._convert_to_int16(audio)
            recognizer.AcceptWaveform(audio_int16.tobytes())

            result_json = recognizer.FinalResult()
            result = json.loads(result_json)

            text = result.get("text", "").strip()

            if not text:
                continue

            # Calculate confidence
            if "result" in result and result["result"]:
                confidences = [word.get("conf", 0.0) for word in result["result"]]
                confidence = sum(confidences) / len(confidences) if confidences else 0.0
            else:
                confidence = 0.3

            # Update best match
            if confidence > best_confidence:
                best_confidence = confidence
                best_lang = lang

        logger.debug(f"Detected language: {best_lang.value} (confidence: {best_confidence:.2f})")
        return best_lang

    def detect_language_from_text(self, text: str) -> Optional[str]:
        """
        Detect language from recognized text using langdetect.

        Args:
            text: Recognized text

        Returns:
            Language code or None
        """
        if not LANGDETECT_AVAILABLE or not text:
            return None

        try:
            detected = detect(text)
            # Map detected language to supported languages
            if detected == "en":
                return "en"
            elif detected == "ru":
                return "ru"
            else:
                logger.debug(f"Detected unsupported language: {detected}")
                return None
        except LangDetectException as e:
            logger.debug(f"Language detection failed: {e}")
            return None

    def _convert_to_int16(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert float32 audio to int16 PCM.

        Args:
            audio: Audio as float32 (-1.0 to 1.0)

        Returns:
            Audio as int16
        """
        # Clip to valid range
        audio = np.clip(audio, -1.0, 1.0)

        # Convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)

        return audio_int16

    def reset(self, language: Optional[str] = None):
        """
        Reset recognizer state.

        Args:
            language: Specific language to reset, or None for all
        """
        if language:
            lang = Language(language)
            if lang in self.recognizers:
                self.recognizers[lang].Reset()
        else:
            for recognizer in self.recognizers.values():
                recognizer.Reset()

        logger.debug("Recognizer reset")

    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return [lang.value for lang in self.models.keys()]

    def is_language_available(self, language: str) -> bool:
        """Check if language is available"""
        try:
            lang = Language(language)
            return lang in self.models
        except ValueError:
            return False


class StreamingRecognizer:
    """
    Streaming speech recognizer for continuous recognition.

    Processes audio chunks in real-time and provides both
    partial and final results.
    """

    def __init__(
        self,
        recognizer: SpeechRecognizer,
        language: Optional[str] = None
    ):
        """
        Initialize streaming recognizer.

        Args:
            recognizer: SpeechRecognizer instance
            language: Language to use (None for auto-detection)
        """
        self.recognizer = recognizer
        self.language = language or recognizer.default_language.value
        self.is_active = False

    def start(self):
        """Start streaming recognition"""
        self.recognizer.reset(self.language)
        self.is_active = True
        logger.info(f"Streaming recognition started (language: {self.language})")

    def stop(self):
        """Stop streaming recognition"""
        self.is_active = False
        logger.info("Streaming recognition stopped")

    def process_chunk(self, audio_chunk: np.ndarray) -> Dict[str, Any]:
        """
        Process audio chunk.

        Args:
            audio_chunk: Audio data

        Returns:
            Partial recognition result
        """
        if not self.is_active:
            logger.warning("Streaming recognition not active")
            return {
                "text": "",
                "language": self.language,
                "confidence": 0.0,
                "success": False,
                "partial": True
            }

        return self.recognizer.recognize_partial(audio_chunk, self.language)

    def finalize(self) -> Dict[str, Any]:
        """
        Get final recognition result.

        Returns:
            Final recognition result
        """
        # For finalization, we would need to track accumulated audio
        # This is a simplified version
        self.is_active = False
        return {
            "text": "",
            "language": self.language,
            "confidence": 0.0,
            "success": False,
            "partial": False
        }


def test_speech_recognition():
    """Test speech recognition"""
    logger.info("Testing Speech Recognition...")

    try:
        # Initialize recognizer
        recognizer = SpeechRecognizer()

        # Generate test audio (silence)
        test_audio = np.zeros(16000 * 2, dtype=np.float32)  # 2 seconds

        # Test recognition
        result = recognizer.recognize(test_audio)
        logger.info(f"Recognition result: {result}")

        # Test available languages
        languages = recognizer.get_available_languages()
        logger.info(f"Available languages: {languages}")

    except Exception as e:
        logger.error(f"Speech recognition test failed: {e}")

    logger.info("Test completed!")


if __name__ == "__main__":
    test_speech_recognition()

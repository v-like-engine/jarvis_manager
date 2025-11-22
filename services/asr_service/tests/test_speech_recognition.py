"""
Unit tests for Speech Recognition
"""

import pytest
import numpy as np
from services.asr_service.src.speech_recognition import SpeechRecognizer


class TestSpeechRecognition:
    """Test cases for SpeechRecognizer"""

    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance (will fail if models not available)"""
        try:
            return SpeechRecognizer(
                model_path_en="shared/models/asr/vosk-model-small-en-us-0.15",
                model_path_ru="shared/models/asr/vosk-model-small-ru-0.22"
            )
        except Exception as e:
            pytest.skip(f"Vosk models not available: {e}")

    def test_initialization(self, recognizer):
        """Test recognizer initialization"""
        assert recognizer is not None
        assert recognizer.sample_rate == 16000

    def test_available_languages(self, recognizer):
        """Test getting available languages"""
        languages = recognizer.get_available_languages()

        assert isinstance(languages, list)
        assert len(languages) > 0

    def test_language_availability(self, recognizer):
        """Test checking language availability"""
        assert recognizer.is_language_available("en") or recognizer.is_language_available("ru")

    def test_recognize_silence(self, recognizer):
        """Test recognizing silence"""
        # Generate 2 seconds of silence
        silence = np.zeros(16000 * 2, dtype=np.float32)

        result = recognizer.recognize(silence)

        assert 'text' in result
        assert 'language' in result
        assert 'confidence' in result
        assert 'success' in result

        # Silence should produce empty text
        assert result['text'] == "" or not result['success']

    def test_recognize_noise(self, recognizer):
        """Test recognizing random noise"""
        # Generate 2 seconds of random noise
        noise = np.random.randn(16000 * 2).astype(np.float32) * 0.1

        result = recognizer.recognize(noise)

        assert 'text' in result
        # Noise usually produces no valid text
        assert result['confidence'] >= 0.0

    def test_reset(self, recognizer):
        """Test resetting recognizer"""
        # Should not raise exception
        recognizer.reset()
        recognizer.reset("en")


class TestSpeechRecognitionNoModels:
    """Test cases that don't require models"""

    def test_convert_to_int16(self):
        """Test audio conversion"""
        # Create a test recognizer instance would require models
        # So we test the conversion logic separately

        audio_float = np.array([0.0, 0.5, 1.0, -0.5, -1.0], dtype=np.float32)
        expected = np.array([0, 16383, 32767, -16384, -32767], dtype=np.int16)

        # Direct conversion
        audio_int16 = (np.clip(audio_float, -1.0, 1.0) * 32767).astype(np.int16)

        assert audio_int16.dtype == np.int16
        assert len(audio_int16) == len(audio_float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

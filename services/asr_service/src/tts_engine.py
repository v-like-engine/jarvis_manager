"""
Text-to-Speech Engine Module

Provides text-to-speech functionality for Gerald's voice responses.
Supports pyttsx3 (offline) with customizable voice settings.
"""

import threading
import queue
from typing import Optional, Dict, Any, List
from enum import Enum
from loguru import logger

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available. Install with: pip install pyttsx3")


class TTSEngine(Enum):
    """Supported TTS engines"""
    PYTTSX3 = "pyttsx3"
    SILERO = "silero"


class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"


class TextToSpeech:
    """
    Text-to-Speech engine with character voice customization.

    Supports offline TTS using pyttsx3 with configurable voice settings
    for Gerald's strict, authoritative character.
    """

    def __init__(
        self,
        engine: str = "pyttsx3",
        rate: int = 180,
        volume: float = 0.9,
        voice_id: Optional[str] = None,
        pitch: int = -20,
        language: str = "en"
    ):
        """
        Initialize Text-to-Speech engine.

        Args:
            engine: TTS engine ("pyttsx3" or "silero")
            rate: Speech rate (words per minute)
            volume: Volume (0.0 to 1.0)
            voice_id: Specific voice ID (None = default)
            pitch: Pitch adjustment (-50 to 50, negative = lower)
            language: Language code ("en" or "ru")
        """
        self.engine_type = TTSEngine(engine)
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        self.pitch = pitch
        self.language = language

        # Initialize engine
        self.engine: Optional[pyttsx3.Engine] = None
        self.is_speaking = False
        self.speech_queue: queue.Queue = queue.Queue()

        # Thread for async speaking
        self.speech_thread: Optional[threading.Thread] = None
        self.stop_thread = False

        if self.engine_type == TTSEngine.PYTTSX3:
            self._init_pyttsx3()
        else:
            raise NotImplementedError(f"TTS engine {engine} not implemented yet")

        logger.info(
            f"TextToSpeech initialized: engine={engine}, rate={rate}, "
            f"volume={volume}, pitch={pitch}, language={language}"
        )

    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        if not PYTTSX3_AVAILABLE:
            raise RuntimeError("pyttsx3 is not installed. Install with: pip install pyttsx3")

        try:
            self.engine = pyttsx3.init()

            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)

            # Set voice
            if self.voice_id:
                self.engine.setProperty('voice', self.voice_id)
            else:
                # Auto-select voice based on language and gender
                voice = self._select_best_voice()
                if voice:
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"Selected voice: {voice.name}")

            logger.info("pyttsx3 engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            raise

    def _select_best_voice(self, prefer_male: bool = True) -> Optional[Any]:
        """
        Select best voice based on language and gender preference.

        Args:
            prefer_male: Prefer male voice (for Gerald's character)

        Returns:
            Voice object or None
        """
        if not self.engine:
            return None

        voices = self.engine.getProperty('voices')

        if not voices:
            logger.warning("No voices available")
            return None

        # Filter by language
        lang_code = self.language.lower()
        matching_voices = []

        for voice in voices:
            voice_lang = voice.languages[0] if voice.languages else ""

            # Check if voice matches language
            if lang_code in voice_lang.lower():
                matching_voices.append(voice)

        # If no exact language match, use first available voice
        if not matching_voices:
            logger.warning(f"No voices found for language {self.language}, using default")
            matching_voices = voices

        # Prefer male voices for Gerald
        if prefer_male:
            for voice in matching_voices:
                if "male" in voice.name.lower() and "female" not in voice.name.lower():
                    return voice

        # Return first matching voice
        return matching_voices[0] if matching_voices else None

    def speak(self, text: str, blocking: bool = True):
        """
        Speak text.

        Args:
            text: Text to speak
            blocking: Wait for speech to complete
        """
        if not text:
            logger.warning("Empty text provided for TTS")
            return

        if not self.engine:
            logger.error("TTS engine not initialized")
            return

        logger.info(f"Speaking: '{text}' (blocking={blocking})")

        try:
            if blocking:
                # Synchronous speech
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
            else:
                # Asynchronous speech (add to queue)
                self.speech_queue.put(text)
                if not self.speech_thread or not self.speech_thread.is_alive():
                    self._start_speech_thread()

        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.is_speaking = False

    def speak_async(self, text: str):
        """
        Speak text asynchronously (non-blocking).

        Args:
            text: Text to speak
        """
        self.speak(text, blocking=False)

    def _start_speech_thread(self):
        """Start background thread for async speech"""
        self.stop_thread = False
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        logger.debug("Speech thread started")

    def _speech_worker(self):
        """Worker thread for async speech"""
        while not self.stop_thread:
            try:
                # Get text from queue (with timeout)
                text = self.speech_queue.get(timeout=1.0)

                if text:
                    self.is_speaking = True
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.is_speaking = False

                self.speech_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Speech worker error: {e}")
                self.is_speaking = False

        logger.debug("Speech thread stopped")

    def stop(self):
        """Stop current speech"""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                logger.info("Speech stopped")
            except Exception as e:
                logger.error(f"Error stopping speech: {e}")

    def is_busy(self) -> bool:
        """Check if TTS is currently speaking"""
        return self.is_speaking

    def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices.

        Returns:
            List of voice information dictionaries
        """
        if not self.engine:
            return []

        voices = self.engine.getProperty('voices')
        voice_list = []

        for voice in voices:
            voice_info = {
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': voice.gender if hasattr(voice, 'gender') else 'unknown',
                'age': voice.age if hasattr(voice, 'age') else 'unknown'
            }
            voice_list.append(voice_info)

        return voice_list

    def set_voice(self, voice_id: str):
        """
        Set specific voice by ID.

        Args:
            voice_id: Voice ID
        """
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
                self.voice_id = voice_id
                logger.info(f"Voice changed to: {voice_id}")
            except Exception as e:
                logger.error(f"Failed to set voice: {e}")

    def set_rate(self, rate: int):
        """
        Set speech rate.

        Args:
            rate: Words per minute
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
            self.rate = rate
            logger.info(f"Speech rate set to: {rate}")

    def set_volume(self, volume: float):
        """
        Set speech volume.

        Args:
            volume: Volume (0.0 to 1.0)
        """
        if self.engine:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            self.volume = volume
            logger.info(f"Volume set to: {volume}")

    def save_to_file(self, text: str, filename: str):
        """
        Save speech to audio file.

        Args:
            text: Text to convert
            filename: Output filename
        """
        if not self.engine:
            logger.error("TTS engine not initialized")
            return

        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            logger.info(f"Speech saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save speech: {e}")

    def shutdown(self):
        """Shutdown TTS engine"""
        # Stop speech thread
        self.stop_thread = True
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=2.0)

        # Stop engine
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

        logger.info("TTS engine shutdown")

    def __del__(self):
        """Cleanup on deletion"""
        self.shutdown()


class CharacterVoiceProfile:
    """
    Character voice profile with personality-specific TTS settings.

    Supports multiple characters with unique voice characteristics.
    """

    # Voice profile definitions
    PROFILES = {
        "gerald": {
            "name": "Gerald",
            "description": "Strict knight, authoritative, commanding",
            "en": {
                "rate": 180,      # Steady, measured pace
                "volume": 0.9,    # Strong, confident
                "pitch": -20,     # Lower, authoritative
                "gender": "male"
            },
            "ru": {
                "rate": 175,      # Slightly slower for Russian
                "volume": 0.9,
                "pitch": -20,
                "gender": "male"
            }
        },
        "winnie": {
            "name": "Винни Пух (Winnie the Pooh)",
            "description": "Gentle, thoughtful, slow-paced, warm",
            "en": {
                "rate": 140,      # Slow, thoughtful
                "volume": 0.8,    # Softer, gentle
                "pitch": -10,     # Slightly lower, warm
                "gender": "male"
            },
            "ru": {
                "rate": 135,      # Even slower for Russian thoughtfulness
                "volume": 0.8,
                "pitch": -10,
                "gender": "male"
            }
        },
        "rapunzel": {
            "name": "Rapunzel (Рапунцель)",
            "description": "Disney princess, cheerful, curious, energetic",
            "en": {
                "rate": 190,      # Energetic, quick
                "volume": 0.85,   # Bright, clear
                "pitch": 15,      # Higher, cheerful
                "gender": "female"
            },
            "ru": {
                "rate": 185,      # Slightly slower for Russian
                "volume": 0.85,
                "pitch": 15,
                "gender": "female"
            }
        },
        "terminator": {
            "name": "Терминатор (Terminator)",
            "description": "Robotic, direct, monotone, stern, mechanical",
            "en": {
                "rate": 160,      # Mechanical, steady
                "volume": 1.0,    # Loud, commanding
                "pitch": -30,     # Very deep, robotic
                "gender": "male"
            },
            "ru": {
                "rate": 160,      # Same mechanical pace
                "volume": 1.0,
                "pitch": -30,
                "gender": "male"
            }
        }
    }

    @classmethod
    def get_profile(cls, character: str) -> Optional[Dict[str, Any]]:
        """
        Get voice profile for character.

        Args:
            character: Character ID (gerald, winnie, rapunzel, terminator)

        Returns:
            Voice profile dictionary or None
        """
        return cls.PROFILES.get(character.lower())

    @classmethod
    def get_available_characters(cls) -> List[str]:
        """Get list of available character IDs"""
        return list(cls.PROFILES.keys())

    @classmethod
    def create_voice(cls, character: str, language: str = "en") -> Optional[TextToSpeech]:
        """
        Create TTS engine for character.

        Args:
            character: Character ID
            language: Language code (en or ru)

        Returns:
            Configured TextToSpeech instance or None
        """
        profile = cls.get_profile(character)
        if not profile:
            logger.error(f"Unknown character: {character}")
            return None

        lang_settings = profile.get(language, profile.get("en"))

        logger.info(
            f"Creating voice for {profile['name']} ({language}): "
            f"rate={lang_settings['rate']}, pitch={lang_settings['pitch']}, "
            f"volume={lang_settings['volume']}"
        )

        return TextToSpeech(
            engine="pyttsx3",
            rate=lang_settings["rate"],
            volume=lang_settings["volume"],
            pitch=lang_settings["pitch"],
            language=language
        )


class GeraldVoice:
    """
    Gerald's character voice configuration.

    Provides pre-configured TTS settings for Gerald's strict,
    authoritative character personality.

    NOTE: This class is kept for backward compatibility.
    Use CharacterVoiceProfile for new implementations.
    """

    @staticmethod
    def create_english() -> TextToSpeech:
        """
        Create Gerald's English voice.

        Returns:
            Configured TextToSpeech instance
        """
        return CharacterVoiceProfile.create_voice("gerald", "en")

    @staticmethod
    def create_russian() -> TextToSpeech:
        """
        Create Gerald's Russian voice.

        Returns:
            Configured TextToSpeech instance
        """
        return CharacterVoiceProfile.create_voice("gerald", "ru")


def test_tts():
    """Test Text-to-Speech"""
    logger.info("Testing Text-to-Speech...")

    try:
        # List available voices
        tts = TextToSpeech()
        voices = tts.get_voices()

        logger.info(f"\nAvailable voices ({len(voices)}):")
        for i, voice in enumerate(voices[:5]):  # Show first 5
            logger.info(f"  {i+1}. {voice['name']} ({voice['languages']})")

        # Test all character voices
        logger.info("\n=== Testing Character Voices ===")

        # Gerald - Strict Knight
        logger.info("\n1. Testing Gerald (Strict Knight)...")
        gerald_en = CharacterVoiceProfile.create_voice("gerald", "en")
        gerald_en.speak("I am Gerald, your loyal virtual assistant. Ready to serve.", blocking=True)

        # Winnie the Pooh - Gentle and thoughtful
        logger.info("\n2. Testing Winnie the Pooh (Gentle, Thoughtful)...")
        winnie_en = CharacterVoiceProfile.create_voice("winnie", "en")
        winnie_en.speak("Oh bother. Think, think, think. Perhaps a little something to help me think.", blocking=True)

        winnie_ru = CharacterVoiceProfile.create_voice("winnie", "ru")
        winnie_ru.speak("Ох, беспокойство. Думай, думай, думай. Может быть, что-нибудь сладенькое поможет мне думать.", blocking=True)

        # Rapunzel - Cheerful Princess
        logger.info("\n3. Testing Rapunzel (Cheerful Princess)...")
        rapunzel_en = CharacterVoiceProfile.create_voice("rapunzel", "en")
        rapunzel_en.speak("Hello! I'm Rapunzel! This is so exciting! Let's explore the world together!", blocking=True)

        rapunzel_ru = CharacterVoiceProfile.create_voice("rapunzel", "ru")
        rapunzel_ru.speak("Привет! Я Рапунцель! Это так увлекательно! Давайте вместе исследовать мир!", blocking=True)

        # Terminator - Robotic
        logger.info("\n4. Testing Terminator (Robotic, Direct)...")
        terminator_en = CharacterVoiceProfile.create_voice("terminator", "en")
        terminator_en.speak("I am Terminator. Mission objectives identified. Ready for execution.", blocking=True)

        terminator_ru = CharacterVoiceProfile.create_voice("terminator", "ru")
        terminator_ru.speak("Я Терминатор. Цели миссии определены. Готов к выполнению.", blocking=True)

        # Test async speech with Gerald
        logger.info("\n=== Testing Async Speech ===")
        gerald_en.speak_async("This is asynchronous speech.")
        gerald_en.speak_async("Multiple sentences can be queued.")

        import time
        time.sleep(5)  # Wait for async speech to complete

        # Cleanup
        gerald_en.shutdown()
        winnie_en.shutdown()
        winnie_ru.shutdown()
        rapunzel_en.shutdown()
        rapunzel_ru.shutdown()
        terminator_en.shutdown()
        terminator_ru.shutdown()

        # Display character profiles
        logger.info("\n=== Available Character Profiles ===")
        for char_id in CharacterVoiceProfile.get_available_characters():
            profile = CharacterVoiceProfile.get_profile(char_id)
            logger.info(f"\n{profile['name']}: {profile['description']}")
            logger.info(f"  EN: rate={profile['en']['rate']}, pitch={profile['en']['pitch']}, volume={profile['en']['volume']}")
            logger.info(f"  RU: rate={profile['ru']['rate']}, pitch={profile['ru']['pitch']}, volume={profile['ru']['volume']}")

    except Exception as e:
        logger.error(f"TTS test failed: {e}")

    logger.info("\nTest completed!")


if __name__ == "__main__":
    test_tts()

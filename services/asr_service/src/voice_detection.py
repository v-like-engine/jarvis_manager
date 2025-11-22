"""
Voice Activity Detection (VAD) Module

Detects voice activity in audio streams using Silero VAD or WebRTC VAD.
Optimized for low CPU usage and high accuracy.
"""

import os
from typing import Optional, List, Tuple
from enum import Enum
import numpy as np
import torch
from loguru import logger

try:
    import webrtcvad
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    logger.warning("webrtcvad not available")


class VADEngine(Enum):
    """Supported VAD engines"""
    SILERO = "silero"
    WEBRTC = "webrtc"


class VoiceActivityDetector:
    """
    Voice Activity Detector supporting multiple backends.

    Supports:
    - Silero VAD (neural network-based, high accuracy)
    - WebRTC VAD (classic algorithm, fast)
    """

    def __init__(
        self,
        engine: str = "silero",
        sample_rate: int = 16000,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        max_speech_duration_s: int = 30,
        padding_duration_ms: int = 300,
        frame_duration_ms: int = 30
    ):
        """
        Initialize Voice Activity Detector.

        Args:
            engine: VAD engine ("silero" or "webrtc")
            sample_rate: Audio sample rate (8000, 16000, 32000, or 48000)
            threshold: VAD threshold (0.0-1.0 for Silero, not used for WebRTC)
            min_speech_duration_ms: Minimum speech duration to trigger
            max_speech_duration_s: Maximum speech duration before auto-stop
            padding_duration_ms: Padding before/after speech
            frame_duration_ms: Frame duration (10, 20, or 30 ms for WebRTC)
        """
        self.engine = VADEngine(engine)
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.max_speech_duration_s = max_speech_duration_s
        self.padding_duration_ms = padding_duration_ms
        self.frame_duration_ms = frame_duration_ms

        # Calculate frame size
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)

        # State tracking
        self.is_speech = False
        self.speech_frames = 0
        self.silence_frames = 0

        # Initialize VAD engine
        if self.engine == VADEngine.SILERO:
            self._init_silero_vad()
        elif self.engine == VADEngine.WEBRTC:
            self._init_webrtc_vad()

        logger.info(
            f"VoiceActivityDetector initialized: engine={engine}, "
            f"sample_rate={sample_rate}, threshold={threshold}"
        )

    def _init_silero_vad(self):
        """Initialize Silero VAD model"""
        try:
            # Check if model exists
            model_path = "shared/models/vad/silero_vad.jit"

            if os.path.exists(model_path):
                # Load from local file
                self.model = torch.jit.load(model_path)
                logger.info(f"Loaded Silero VAD model from {model_path}")
            else:
                # Load from torch hub (will download if needed)
                self.model, utils = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad',
                    force_reload=False,
                    onnx=False
                )
                logger.info("Loaded Silero VAD model from torch hub")

            self.model.eval()

            # Check if GPU is available
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)

            logger.info(f"Silero VAD using device: {self.device}")

        except Exception as e:
            logger.error(f"Failed to initialize Silero VAD: {e}")
            raise

    def _init_webrtc_vad(self):
        """Initialize WebRTC VAD"""
        if not WEBRTC_AVAILABLE:
            raise RuntimeError("webrtcvad is not installed. Install with: pip install webrtcvad")

        # WebRTC VAD aggressiveness: 0-3 (3 = most aggressive)
        # Map threshold to aggressiveness
        if self.threshold < 0.3:
            aggressiveness = 1
        elif self.threshold < 0.6:
            aggressiveness = 2
        else:
            aggressiveness = 3

        self.vad = webrtcvad.Vad(aggressiveness)
        logger.info(f"WebRTC VAD initialized with aggressiveness={aggressiveness}")

    def detect_silero(self, audio: np.ndarray) -> float:
        """
        Detect speech using Silero VAD.

        Args:
            audio: Audio chunk as numpy array

        Returns:
            Speech probability (0.0-1.0)
        """
        # Convert to torch tensor
        audio_tensor = torch.from_numpy(audio).float()

        # Ensure correct shape (1D)
        if audio_tensor.dim() > 1:
            audio_tensor = audio_tensor.squeeze()

        # Move to device
        audio_tensor = audio_tensor.to(self.device)

        # Get speech probability
        with torch.no_grad():
            speech_prob = self.model(audio_tensor, self.sample_rate).item()

        return speech_prob

    def detect_webrtc(self, audio: np.ndarray) -> bool:
        """
        Detect speech using WebRTC VAD.

        Args:
            audio: Audio chunk as numpy array (must be frame_duration_ms length)

        Returns:
            True if speech detected, False otherwise
        """
        # Convert float32 to int16
        audio_int16 = (audio * 32767).astype(np.int16)

        # Convert to bytes
        audio_bytes = audio_int16.tobytes()

        # Detect speech
        try:
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
            return is_speech
        except Exception as e:
            logger.error(f"WebRTC VAD error: {e}")
            return False

    def process_chunk(self, audio: np.ndarray) -> Tuple[bool, float]:
        """
        Process audio chunk and detect speech.

        Args:
            audio: Audio chunk as numpy array

        Returns:
            Tuple of (is_speech, confidence)
        """
        # Ensure audio is the right length
        if len(audio) != self.frame_size:
            # Pad or truncate
            if len(audio) < self.frame_size:
                audio = np.pad(audio, (0, self.frame_size - len(audio)))
            else:
                audio = audio[:self.frame_size]

        # Detect speech
        if self.engine == VADEngine.SILERO:
            confidence = self.detect_silero(audio)
            is_speech = confidence >= self.threshold
        elif self.engine == VADEngine.WEBRTC:
            is_speech = self.detect_webrtc(audio)
            confidence = 1.0 if is_speech else 0.0
        else:
            raise ValueError(f"Unknown VAD engine: {self.engine}")

        return is_speech, confidence

    def process_audio_stream(
        self,
        audio: np.ndarray,
        return_speech_segments: bool = False
    ) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Process audio stream and detect speech segments.

        Args:
            audio: Audio data as numpy array
            return_speech_segments: If True, return list of speech segments

        Returns:
            Tuple of (has_speech, speech_segments)
            speech_segments is list of (start_sample, end_sample) tuples
        """
        # Split audio into frames
        num_frames = len(audio) // self.frame_size
        speech_segments = []
        current_segment_start = None

        for i in range(num_frames):
            start = i * self.frame_size
            end = start + self.frame_size
            frame = audio[start:end]

            is_speech, confidence = self.process_chunk(frame)

            if return_speech_segments:
                if is_speech and current_segment_start is None:
                    current_segment_start = start
                elif not is_speech and current_segment_start is not None:
                    speech_segments.append((current_segment_start, start))
                    current_segment_start = None

        # Close last segment if still open
        if current_segment_start is not None:
            speech_segments.append((current_segment_start, len(audio)))

        has_speech = len(speech_segments) > 0

        return has_speech, speech_segments

    def is_speech_detected(self, audio: np.ndarray) -> bool:
        """
        Simple speech detection for audio chunk.

        Args:
            audio: Audio chunk

        Returns:
            True if speech detected
        """
        has_speech, _ = self.process_audio_stream(audio)
        return has_speech

    def get_speech_segments(self, audio: np.ndarray) -> List[np.ndarray]:
        """
        Extract speech segments from audio.

        Args:
            audio: Full audio data

        Returns:
            List of speech segments as numpy arrays
        """
        has_speech, segments = self.process_audio_stream(audio, return_speech_segments=True)

        if not has_speech:
            return []

        # Extract audio segments
        speech_chunks = []
        for start, end in segments:
            # Add padding
            padding_samples = int(self.sample_rate * self.padding_duration_ms / 1000)
            padded_start = max(0, start - padding_samples)
            padded_end = min(len(audio), end + padding_samples)

            speech_chunks.append(audio[padded_start:padded_end])

        return speech_chunks

    def reset(self):
        """Reset VAD state"""
        self.is_speech = False
        self.speech_frames = 0
        self.silence_frames = 0
        logger.debug("VAD state reset")


class SpeechSegmenter:
    """
    Helper class for segmenting continuous audio into speech segments.

    Uses VAD to detect start and end of speech, with buffering and
    minimum duration enforcement.
    """

    def __init__(
        self,
        vad: VoiceActivityDetector,
        min_speech_duration_ms: int = 250,
        max_speech_duration_s: int = 30,
        padding_duration_ms: int = 300
    ):
        """
        Initialize speech segmenter.

        Args:
            vad: Voice Activity Detector instance
            min_speech_duration_ms: Minimum speech duration
            max_speech_duration_s: Maximum speech duration
            padding_duration_ms: Padding around speech
        """
        self.vad = vad
        self.min_speech_duration_ms = min_speech_duration_ms
        self.max_speech_duration_s = max_speech_duration_s
        self.padding_duration_ms = padding_duration_ms

        # State
        self.is_speaking = False
        self.speech_buffer = []
        self.silence_buffer = []

        # Calculate durations in frames
        frame_duration_ms = 1000 * vad.frame_size / vad.sample_rate
        self.min_speech_frames = int(min_speech_duration_ms / frame_duration_ms)
        self.max_speech_frames = int(max_speech_duration_s * 1000 / frame_duration_ms)
        self.padding_frames = int(padding_duration_ms / frame_duration_ms)

        logger.info(
            f"SpeechSegmenter initialized: min={min_speech_duration_ms}ms, "
            f"max={max_speech_duration_s}s, padding={padding_duration_ms}ms"
        )

    def process_frame(self, audio_frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Process audio frame and return complete speech segment if ready.

        Args:
            audio_frame: Audio frame

        Returns:
            Complete speech segment or None if not ready
        """
        is_speech, confidence = self.vad.process_chunk(audio_frame)

        if is_speech:
            # Add to speech buffer
            self.speech_buffer.append(audio_frame)

            # Clear silence buffer
            self.silence_buffer = []

            # Check if max duration reached
            if len(self.speech_buffer) >= self.max_speech_frames:
                logger.info("Max speech duration reached, finalizing segment")
                return self._finalize_segment()

        else:
            # Add to silence buffer
            self.silence_buffer.append(audio_frame)

            # Check if speech ended
            if len(self.speech_buffer) > 0 and len(self.silence_buffer) >= self.padding_frames:
                # Check if minimum duration met
                if len(self.speech_buffer) >= self.min_speech_frames:
                    logger.debug(f"Speech segment complete: {len(self.speech_buffer)} frames")
                    return self._finalize_segment()
                else:
                    # Too short, reset
                    logger.debug("Speech too short, discarding")
                    self.speech_buffer = []
                    self.silence_buffer = []

        return None

    def _finalize_segment(self) -> np.ndarray:
        """Finalize and return speech segment"""
        # Concatenate speech buffer
        if len(self.speech_buffer) == 0:
            return np.array([], dtype=np.float32)

        segment = np.concatenate(self.speech_buffer)

        # Reset buffers
        self.speech_buffer = []
        self.silence_buffer = []

        return segment

    def reset(self):
        """Reset segmenter state"""
        self.speech_buffer = []
        self.silence_buffer = []
        self.is_speaking = False
        logger.debug("SpeechSegmenter reset")


def test_vad():
    """Test Voice Activity Detection"""
    logger.info("Testing Voice Activity Detection...")

    # Test Silero VAD
    logger.info("\n=== Testing Silero VAD ===")
    try:
        vad_silero = VoiceActivityDetector(engine="silero", sample_rate=16000)

        # Generate test audio (silent)
        silent_audio = np.zeros(480, dtype=np.float32)
        is_speech, confidence = vad_silero.process_chunk(silent_audio)
        logger.info(f"Silent audio: is_speech={is_speech}, confidence={confidence:.3f}")

        # Generate test audio (noise)
        noisy_audio = np.random.randn(480).astype(np.float32) * 0.1
        is_speech, confidence = vad_silero.process_chunk(noisy_audio)
        logger.info(f"Noisy audio: is_speech={is_speech}, confidence={confidence:.3f}")

    except Exception as e:
        logger.error(f"Silero VAD test failed: {e}")

    # Test WebRTC VAD
    logger.info("\n=== Testing WebRTC VAD ===")
    if WEBRTC_AVAILABLE:
        try:
            vad_webrtc = VoiceActivityDetector(engine="webrtc", sample_rate=16000)

            # Generate test audio
            silent_audio = np.zeros(480, dtype=np.float32)
            is_speech, confidence = vad_webrtc.process_chunk(silent_audio)
            logger.info(f"Silent audio: is_speech={is_speech}, confidence={confidence:.3f}")

            noisy_audio = np.random.randn(480).astype(np.float32) * 0.1
            is_speech, confidence = vad_webrtc.process_chunk(noisy_audio)
            logger.info(f"Noisy audio: is_speech={is_speech}, confidence={confidence:.3f}")

        except Exception as e:
            logger.error(f"WebRTC VAD test failed: {e}")
    else:
        logger.warning("WebRTC VAD not available")

    logger.info("\nVAD tests completed!")


if __name__ == "__main__":
    test_vad()

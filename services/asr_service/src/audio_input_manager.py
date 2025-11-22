"""
Audio Input Manager Module

Handles continuous microphone input with efficient buffering and minimal CPU usage.
Designed for low-latency audio capture optimized for voice activity detection.
"""

import threading
import queue
import time
from typing import Optional, Callable, List
import numpy as np
import sounddevice as sd
from loguru import logger


class AudioInputManager:
    """
    Manages continuous microphone input with efficient buffering.

    Features:
    - Low-latency audio capture
    - Efficient circular buffering
    - Thread-safe audio streaming
    - Minimal CPU usage when idle
    - Automatic device selection
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        device_index: Optional[int] = None,
        buffer_seconds: float = 0.5
    ):
        """
        Initialize the audio input manager.

        Args:
            sample_rate: Audio sample rate (Hz)
            channels: Number of audio channels (1=mono, 2=stereo)
            chunk_size: Size of audio chunks to process
            device_index: Microphone device index (None = default)
            buffer_seconds: Size of circular buffer in seconds
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.buffer_seconds = buffer_seconds

        # Audio stream
        self.stream: Optional[sd.InputStream] = None
        self.is_running = False

        # Thread-safe queue for audio chunks
        self.audio_queue: queue.Queue = queue.Queue(maxsize=100)

        # Circular buffer for storing recent audio
        buffer_size = int(sample_rate * buffer_seconds)
        self.circular_buffer = np.zeros(buffer_size, dtype=np.float32)
        self.buffer_index = 0

        # Callback for processing audio
        self.audio_callback: Optional[Callable[[np.ndarray], None]] = None

        # Lock for thread safety
        self.lock = threading.Lock()

        # Statistics
        self.frames_processed = 0
        self.start_time = 0.0

        logger.info(
            f"AudioInputManager initialized: {sample_rate}Hz, "
            f"{channels}ch, chunk={chunk_size}, buffer={buffer_seconds}s"
        )

    def list_devices(self) -> List[dict]:
        """
        List all available audio input devices.

        Returns:
            List of device information dictionaries
        """
        devices = sd.query_devices()
        input_devices = []

        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': idx,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })

        return input_devices

    def get_default_device(self) -> dict:
        """
        Get default input device information.

        Returns:
            Default device information dictionary
        """
        device_idx = sd.default.device[0]  # Input device
        device = sd.query_devices(device_idx)
        return {
            'index': device_idx,
            'name': device['name'],
            'channels': device['max_input_channels'],
            'sample_rate': device['default_samplerate']
        }

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback function for audio stream (called by sounddevice).

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Status flags
        """
        if status:
            logger.warning(f"Audio callback status: {status}")

        # Convert to float32 and flatten to mono if needed
        audio_data = indata.copy()
        if self.channels == 1 and audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        audio_data = audio_data.astype(np.float32).flatten()

        # Update circular buffer
        with self.lock:
            chunk_len = len(audio_data)
            buffer_len = len(self.circular_buffer)

            if self.buffer_index + chunk_len <= buffer_len:
                self.circular_buffer[self.buffer_index:self.buffer_index + chunk_len] = audio_data
                self.buffer_index = (self.buffer_index + chunk_len) % buffer_len
            else:
                # Wrap around
                first_part = buffer_len - self.buffer_index
                self.circular_buffer[self.buffer_index:] = audio_data[:first_part]
                self.circular_buffer[:chunk_len - first_part] = audio_data[first_part:]
                self.buffer_index = chunk_len - first_part

            self.frames_processed += frames

        # Add to queue for processing (non-blocking)
        try:
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            logger.warning("Audio queue is full, dropping frame")

        # Call user-defined callback if set
        if self.audio_callback:
            try:
                self.audio_callback(audio_data)
            except Exception as e:
                logger.error(f"Error in audio callback: {e}")

    def start(self, callback: Optional[Callable[[np.ndarray], None]] = None):
        """
        Start continuous audio input.

        Args:
            callback: Optional callback function to process each audio chunk
        """
        if self.is_running:
            logger.warning("Audio input is already running")
            return

        self.audio_callback = callback
        self.start_time = time.time()

        try:
            # Get device info
            if self.device_index is None:
                device_info = self.get_default_device()
                logger.info(f"Using default device: {device_info['name']}")
            else:
                device_info = sd.query_devices(self.device_index)
                logger.info(f"Using device {self.device_index}: {device_info['name']}")

            # Start audio stream
            self.stream = sd.InputStream(
                device=self.device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype='float32',
                callback=self._audio_callback
            )

            self.stream.start()
            self.is_running = True

            logger.info("Audio input started successfully")

        except Exception as e:
            logger.error(f"Failed to start audio input: {e}")
            raise

    def stop(self):
        """Stop continuous audio input"""
        if not self.is_running:
            logger.warning("Audio input is not running")
            return

        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            self.is_running = False

            # Calculate statistics
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                fps = self.frames_processed / elapsed
                logger.info(
                    f"Audio input stopped. Processed {self.frames_processed} frames "
                    f"in {elapsed:.2f}s ({fps:.1f} fps)"
                )

        except Exception as e:
            logger.error(f"Error stopping audio input: {e}")

    def get_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get next audio chunk from queue.

        Args:
            timeout: Maximum time to wait for chunk (seconds)

        Returns:
            Audio chunk as numpy array, or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_buffer(self) -> np.ndarray:
        """
        Get current circular buffer contents.

        Returns:
            Audio buffer as numpy array (ordered chronologically)
        """
        with self.lock:
            # Reorder buffer so oldest data is first
            if self.buffer_index == 0:
                return self.circular_buffer.copy()
            else:
                return np.concatenate([
                    self.circular_buffer[self.buffer_index:],
                    self.circular_buffer[:self.buffer_index]
                ])

    def get_recent_audio(self, duration_seconds: float) -> np.ndarray:
        """
        Get recent audio from buffer.

        Args:
            duration_seconds: Duration of audio to retrieve

        Returns:
            Recent audio as numpy array
        """
        num_samples = int(self.sample_rate * duration_seconds)
        buffer = self.get_buffer()

        if num_samples >= len(buffer):
            return buffer
        else:
            return buffer[-num_samples:]

    def clear_queue(self):
        """Clear the audio queue"""
        with self.lock:
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break

    def get_stats(self) -> dict:
        """
        Get audio input statistics.

        Returns:
            Dictionary with statistics
        """
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0
        fps = self.frames_processed / elapsed if elapsed > 0 else 0

        return {
            'is_running': self.is_running,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size,
            'frames_processed': self.frames_processed,
            'elapsed_seconds': elapsed,
            'fps': fps,
            'queue_size': self.audio_queue.qsize(),
            'buffer_seconds': self.buffer_seconds
        }

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def __del__(self):
        """Cleanup on deletion"""
        if self.is_running:
            self.stop()


def test_audio_input():
    """Test audio input manager"""
    logger.info("Testing Audio Input Manager...")

    # List devices
    manager = AudioInputManager()
    devices = manager.list_devices()
    logger.info(f"Found {len(devices)} input devices:")
    for device in devices:
        logger.info(f"  [{device['index']}] {device['name']}")

    # Test audio capture
    logger.info("\nTesting audio capture for 3 seconds...")

    def audio_callback(audio_chunk):
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        logger.debug(f"Audio chunk: {len(audio_chunk)} samples, RMS: {rms:.4f}")

    with AudioInputManager(callback=audio_callback) as manager:
        time.sleep(3)
        stats = manager.get_stats()
        logger.info(f"\nStats: {stats}")

    logger.info("Test completed!")


if __name__ == "__main__":
    test_audio_input()

"""
Voice Biometrics Module

Speaker identification using voice embeddings.
Uses SpeechBrain for extracting speaker embeddings and matching.
"""

from typing import Optional, Dict, Tuple
import numpy as np
import torch
from loguru import logger

try:
    from speechbrain.pretrained import EncoderClassifier
    SPEECHBRAIN_AVAILABLE = True
except ImportError:
    SPEECHBRAIN_AVAILABLE = False
    logger.warning("SpeechBrain not available. Install with: pip install speechbrain")


class VoiceBiometrics:
    """
    Voice biometrics for speaker identification.

    Uses speaker embeddings to identify users by their voice patterns.
    """

    def __init__(
        self,
        model_name: str = "speechbrain/spkrec-ecapa-voxceleb",
        similarity_threshold: float = 0.7,
        embedding_dim: int = 192
    ):
        """
        Initialize voice biometrics.

        Args:
            model_name: SpeechBrain model name
            similarity_threshold: Threshold for speaker match (0.0-1.0)
            embedding_dim: Embedding dimension
        """
        if not SPEECHBRAIN_AVAILABLE:
            raise RuntimeError(
                "SpeechBrain is not installed. "
                "Install with: pip install speechbrain"
            )

        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.embedding_dim = embedding_dim

        # Model (lazy loading)
        self.model: Optional[EncoderClassifier] = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        logger.info(
            f"VoiceBiometrics initialized: model={model_name}, "
            f"threshold={similarity_threshold}, device={self.device}"
        )

    def _load_model(self):
        """Load SpeechBrain model (lazy loading)"""
        if self.model is not None:
            return

        try:
            logger.info(f"Loading SpeechBrain model: {self.model_name}")

            self.model = EncoderClassifier.from_hparams(
                source=self.model_name,
                savedir=f"shared/models/voice/{self.model_name.split('/')[-1]}",
                run_opts={"device": self.device}
            )

            logger.info("SpeechBrain model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load SpeechBrain model: {e}")
            raise

    def extract_embedding(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000
    ) -> Optional[np.ndarray]:
        """
        Extract speaker embedding from audio.

        Args:
            audio: Audio data as numpy array (mono, float32)
            sample_rate: Audio sample rate

        Returns:
            Speaker embedding as numpy array or None
        """
        # Load model if needed
        if self.model is None:
            self._load_model()

        try:
            # Convert to torch tensor
            if isinstance(audio, np.ndarray):
                audio_tensor = torch.from_numpy(audio).float()
            else:
                audio_tensor = audio

            # Ensure correct shape (1D)
            if audio_tensor.dim() > 1:
                audio_tensor = audio_tensor.squeeze()

            # Add batch dimension
            audio_tensor = audio_tensor.unsqueeze(0)

            # Move to device
            audio_tensor = audio_tensor.to(self.device)

            # Extract embedding
            with torch.no_grad():
                embeddings = self.model.encode_batch(audio_tensor)

            # Convert to numpy
            embedding = embeddings.squeeze().cpu().numpy()

            logger.debug(f"Extracted embedding with shape: {embedding.shape}")

            return embedding

        except Exception as e:
            logger.error(f"Failed to extract embedding: {e}")
            return None

    def compare_embeddings(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compare two speaker embeddings using cosine similarity.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0.0 to 1.0, higher = more similar)
        """
        # Normalize embeddings
        emb1_norm = embedding1 / np.linalg.norm(embedding1)
        emb2_norm = embedding2 / np.linalg.norm(embedding2)

        # Compute cosine similarity
        similarity = np.dot(emb1_norm, emb2_norm)

        # Convert to 0-1 range
        similarity = (similarity + 1) / 2

        return float(similarity)

    def verify_speaker(
        self,
        audio: np.ndarray,
        reference_embedding: np.ndarray,
        sample_rate: int = 16000
    ) -> Tuple[bool, float]:
        """
        Verify if audio matches reference speaker.

        Args:
            audio: Audio data
            reference_embedding: Reference speaker embedding
            sample_rate: Audio sample rate

        Returns:
            Tuple of (is_match, similarity_score)
        """
        # Extract embedding from audio
        embedding = self.extract_embedding(audio, sample_rate)

        if embedding is None:
            logger.error("Failed to extract embedding for verification")
            return False, 0.0

        # Compare embeddings
        similarity = self.compare_embeddings(embedding, reference_embedding)

        is_match = similarity >= self.similarity_threshold

        logger.info(
            f"Speaker verification: similarity={similarity:.3f}, "
            f"match={is_match} (threshold={self.similarity_threshold})"
        )

        return is_match, similarity

    def identify_speaker(
        self,
        audio: np.ndarray,
        known_embeddings: Dict[int, np.ndarray],
        sample_rate: int = 16000
    ) -> Optional[Tuple[int, float]]:
        """
        Identify speaker from audio by comparing with known embeddings.

        Args:
            audio: Audio data
            known_embeddings: Dictionary mapping user_id to embedding
            sample_rate: Audio sample rate

        Returns:
            Tuple of (user_id, similarity) or None if no match
        """
        if not known_embeddings:
            logger.warning("No known speakers in database")
            return None

        # Extract embedding from audio
        embedding = self.extract_embedding(audio, sample_rate)

        if embedding is None:
            logger.error("Failed to extract embedding for identification")
            return None

        # Compare with all known embeddings
        best_match_id = None
        best_similarity = 0.0

        for user_id, ref_embedding in known_embeddings.items():
            similarity = self.compare_embeddings(embedding, ref_embedding)

            logger.debug(f"User {user_id}: similarity={similarity:.3f}")

            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = user_id

        # Check if best match exceeds threshold
        if best_similarity >= self.similarity_threshold:
            logger.info(
                f"Speaker identified: user_id={best_match_id}, "
                f"similarity={best_similarity:.3f}"
            )
            return best_match_id, best_similarity
        else:
            logger.info(
                f"No speaker match found (best similarity: {best_similarity:.3f})"
            )
            return None

    def enroll_speaker(
        self,
        audio_samples: list,
        sample_rate: int = 16000
    ) -> Optional[np.ndarray]:
        """
        Enroll speaker by averaging embeddings from multiple audio samples.

        Args:
            audio_samples: List of audio samples
            sample_rate: Audio sample rate

        Returns:
            Averaged speaker embedding or None
        """
        if not audio_samples:
            logger.error("No audio samples provided for enrollment")
            return None

        embeddings = []

        for i, audio in enumerate(audio_samples):
            logger.info(f"Processing sample {i+1}/{len(audio_samples)}...")

            embedding = self.extract_embedding(audio, sample_rate)

            if embedding is not None:
                embeddings.append(embedding)
            else:
                logger.warning(f"Failed to extract embedding from sample {i+1}")

        if not embeddings:
            logger.error("Failed to extract any embeddings for enrollment")
            return None

        # Average embeddings
        averaged_embedding = np.mean(embeddings, axis=0)

        logger.info(
            f"Speaker enrolled successfully with {len(embeddings)} samples"
        )

        return averaged_embedding

    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension.

        Returns:
            Embedding dimension
        """
        return self.embedding_dim


class SpeakerVerifier:
    """
    Simple wrapper for speaker verification tasks.
    """

    def __init__(
        self,
        biometrics: VoiceBiometrics,
        enrollment_duration: int = 5,
        sample_rate: int = 16000
    ):
        """
        Initialize speaker verifier.

        Args:
            biometrics: VoiceBiometrics instance
            enrollment_duration: Duration of audio for enrollment (seconds)
            sample_rate: Audio sample rate
        """
        self.biometrics = biometrics
        self.enrollment_duration = enrollment_duration
        self.sample_rate = sample_rate

        self.enrollment_samples_needed = enrollment_duration

    def enroll_from_audio(
        self,
        audio: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Enroll speaker from single audio recording.

        Args:
            audio: Audio data (should be at least enrollment_duration long)

        Returns:
            Speaker embedding or None
        """
        # Check audio length
        min_samples = self.sample_rate * self.enrollment_duration
        if len(audio) < min_samples:
            logger.warning(
                f"Audio too short for enrollment: {len(audio)} samples "
                f"(need at least {min_samples})"
            )

        # Split audio into chunks for better averaging
        chunk_duration = 2  # 2 seconds per chunk
        chunk_samples = self.sample_rate * chunk_duration

        chunks = []
        for i in range(0, len(audio) - chunk_samples, chunk_samples):
            chunk = audio[i:i + chunk_samples]
            chunks.append(chunk)

        if not chunks:
            # Use full audio if no chunks
            chunks = [audio]

        # Enroll from chunks
        return self.biometrics.enroll_speaker(chunks, self.sample_rate)


def test_voice_biometrics():
    """Test voice biometrics"""
    logger.info("Testing Voice Biometrics...")

    try:
        # Initialize biometrics
        biometrics = VoiceBiometrics()

        # Generate test audio (2 seconds of random noise)
        test_audio = np.random.randn(16000 * 2).astype(np.float32) * 0.1

        # Extract embedding
        logger.info("\nExtracting embedding from test audio...")
        embedding = biometrics.extract_embedding(test_audio)

        if embedding is not None:
            logger.info(f"Embedding shape: {embedding.shape}")
            logger.info(f"Embedding dimension: {biometrics.get_embedding_dimension()}")

            # Test comparison with itself
            similarity = biometrics.compare_embeddings(embedding, embedding)
            logger.info(f"Self-similarity: {similarity:.3f}")

            # Test enrollment
            logger.info("\nTesting speaker enrollment...")
            samples = [test_audio, test_audio * 0.9, test_audio * 1.1]
            enrolled_embedding = biometrics.enroll_speaker(samples)

            if enrolled_embedding is not None:
                logger.info(f"Enrolled embedding shape: {enrolled_embedding.shape}")

        else:
            logger.warning("Failed to extract embedding (model may not be available)")

    except Exception as e:
        logger.error(f"Voice biometrics test failed: {e}")
        logger.info("Note: This test requires the SpeechBrain model to be downloaded")

    logger.info("\nTest completed!")


if __name__ == "__main__":
    test_voice_biometrics()

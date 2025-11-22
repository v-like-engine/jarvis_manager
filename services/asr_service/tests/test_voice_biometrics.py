"""
Unit tests for Voice Biometrics
"""

import pytest
import numpy as np


class TestVoiceBiometrics:
    """Test cases for VoiceBiometrics"""

    @pytest.fixture
    def biometrics(self):
        """Create biometrics instance"""
        try:
            from services.asr_service.src.voice_biometrics import VoiceBiometrics
            return VoiceBiometrics()
        except Exception as e:
            pytest.skip(f"VoiceBiometrics not available: {e}")

    def test_initialization(self, biometrics):
        """Test biometrics initialization"""
        assert biometrics is not None
        assert biometrics.similarity_threshold > 0.0
        assert biometrics.embedding_dim > 0

    def test_embedding_dimension(self, biometrics):
        """Test embedding dimension"""
        dim = biometrics.get_embedding_dimension()

        assert isinstance(dim, int)
        assert dim > 0

    def test_compare_embeddings(self, biometrics):
        """Test embedding comparison"""
        # Create two identical embeddings
        emb1 = np.random.randn(192).astype(np.float32)
        emb2 = emb1.copy()

        similarity = biometrics.compare_embeddings(emb1, emb2)

        # Identical embeddings should have high similarity
        assert similarity > 0.99

        # Create different embeddings
        emb3 = np.random.randn(192).astype(np.float32)

        similarity2 = biometrics.compare_embeddings(emb1, emb3)

        # Different embeddings should have lower similarity
        assert similarity2 < similarity


class TestVoiceBiometricsUtils:
    """Test utility functions"""

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        # Two identical vectors should have similarity of 1.0
        v1 = np.array([1, 0, 0])
        v2 = np.array([1, 0, 0])

        # Normalize
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)

        # Compute similarity
        similarity = np.dot(v1_norm, v2_norm)

        assert np.isclose(similarity, 1.0)

        # Orthogonal vectors should have similarity of 0.0
        v3 = np.array([0, 1, 0])
        v3_norm = v3 / np.linalg.norm(v3)

        similarity2 = np.dot(v1_norm, v3_norm)

        assert np.isclose(similarity2, 0.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

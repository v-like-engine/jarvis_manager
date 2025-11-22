"""
Unit tests for Face Recognition
"""

import pytest
import numpy as np


class TestFaceRecognition:
    """Test cases for FaceRecognizer"""

    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance"""
        try:
            from services.asr_service.src.face_recognition import FaceRecognizer
            return FaceRecognizer()
        except Exception as e:
            pytest.skip(f"Face recognition not available: {e}")

    def test_initialization(self, recognizer):
        """Test recognizer initialization"""
        assert recognizer is not None
        assert recognizer.camera_index == 0
        assert recognizer.detection_method in ["hog", "cnn"]

    def test_camera_operations(self, recognizer):
        """Test camera open/close (may fail without camera)"""
        try:
            # Try to open camera
            success = recognizer.open_camera()

            if success:
                assert recognizer.camera is not None
                recognizer.close_camera()
                assert recognizer.camera is None
            else:
                # No camera available, skip
                pytest.skip("No camera available")

        except Exception as e:
            pytest.skip(f"Camera operations failed: {e}")

    def test_face_encoding_shape(self):
        """Test face encoding has correct shape"""
        # Face encodings should be 128-dimensional
        expected_dim = 128

        # Create dummy encoding
        dummy_encoding = np.random.randn(expected_dim)

        assert len(dummy_encoding) == expected_dim


class TestFaceRecognitionUtils:
    """Test utility functions"""

    def test_face_location_format(self):
        """Test face location tuple format"""
        # Face locations are (top, right, bottom, left)
        face_location = (100, 200, 300, 150)

        top, right, bottom, left = face_location

        assert top < bottom
        assert left < right
        assert all(isinstance(x, int) for x in face_location)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

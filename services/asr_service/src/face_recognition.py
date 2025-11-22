"""
Face Recognition Module

Provides face detection, encoding, and recognition using webcam.
Based on face_recognition library (dlib-based) with optimization for real-time use.
"""

import time
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
from loguru import logger

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Install with: pip install opencv-python")

try:
    import face_recognition as fr
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition not available. Install with: pip install face-recognition")


class FaceRecognizer:
    """
    Face recognition system for user identification.

    Uses webcam to capture faces, create encodings, and match against
    stored user database.
    """

    def __init__(
        self,
        camera_index: int = 0,
        detection_method: str = "hog",
        tolerance: float = 0.6,
        num_jitters: int = 1,
        min_face_size: int = 80,
        capture_timeout: int = 10
    ):
        """
        Initialize face recognizer.

        Args:
            camera_index: Webcam index (0 = default)
            detection_method: "hog" (fast) or "cnn" (accurate)
            tolerance: Face matching tolerance (lower = stricter)
            num_jitters: Number of jitters for encoding (higher = more accurate)
            min_face_size: Minimum face size in pixels
            capture_timeout: Timeout for face capture (seconds)
        """
        if not CV2_AVAILABLE:
            raise RuntimeError("OpenCV is not installed. Install with: pip install opencv-python")

        if not FACE_RECOGNITION_AVAILABLE:
            raise RuntimeError("face_recognition is not installed. Install with: pip install face-recognition")

        self.camera_index = camera_index
        self.detection_method = detection_method
        self.tolerance = tolerance
        self.num_jitters = num_jitters
        self.min_face_size = min_face_size
        self.capture_timeout = capture_timeout

        # Camera
        self.camera: Optional[cv2.VideoCapture] = None

        # Known faces database (in-memory cache)
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_user_ids: List[int] = []

        logger.info(
            f"FaceRecognizer initialized: camera={camera_index}, "
            f"method={detection_method}, tolerance={tolerance}"
        )

    def open_camera(self) -> bool:
        """
        Open webcam.

        Returns:
            True if camera opened successfully
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)

            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False

            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            logger.info("Camera opened successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to open camera: {e}")
            return False

    def close_camera(self):
        """Close webcam"""
        if self.camera:
            self.camera.release()
            self.camera = None
            logger.info("Camera closed")

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture single frame from camera.

        Returns:
            Frame as numpy array (BGR format) or None
        """
        if not self.camera or not self.camera.isOpened():
            logger.error("Camera not opened")
            return None

        ret, frame = self.camera.read()

        if not ret or frame is None:
            logger.error("Failed to capture frame")
            return None

        return frame

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame.

        Args:
            frame: Image frame (BGR format)

        Returns:
            List of face locations as (top, right, bottom, left) tuples
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = fr.face_locations(
            rgb_frame,
            model=self.detection_method
        )

        # Filter by minimum size
        filtered_faces = []
        for top, right, bottom, left in face_locations:
            width = right - left
            height = bottom - top

            if width >= self.min_face_size and height >= self.min_face_size:
                filtered_faces.append((top, right, bottom, left))

        return filtered_faces

    def encode_face(
        self,
        frame: np.ndarray,
        face_location: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Create face encoding.

        Args:
            frame: Image frame (BGR format)
            face_location: Face location (top, right, bottom, left)

        Returns:
            Face encoding as numpy array or None
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Generate encoding
        encodings = fr.face_encodings(
            rgb_frame,
            known_face_locations=[face_location],
            num_jitters=self.num_jitters
        )

        if not encodings:
            logger.warning("Failed to generate face encoding")
            return None

        return encodings[0]

    def capture_and_encode_face(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Capture face from camera and create encoding.

        Returns:
            Tuple of (frame, encoding) or None
        """
        if not self.camera or not self.camera.isOpened():
            if not self.open_camera():
                return None

        start_time = time.time()

        logger.info("Waiting for face...")

        while time.time() - start_time < self.capture_timeout:
            frame = self.capture_frame()

            if frame is None:
                continue

            # Detect faces
            face_locations = self.detect_faces(frame)

            if not face_locations:
                time.sleep(0.1)
                continue

            # Use first face
            face_location = face_locations[0]

            # Encode face
            encoding = self.encode_face(frame, face_location)

            if encoding is not None:
                logger.info("Face captured and encoded successfully")
                return frame, encoding

            time.sleep(0.1)

        logger.warning("Face capture timeout")
        return None

    def recognize_face(
        self,
        face_encoding: np.ndarray,
        known_encodings: Dict[int, np.ndarray]
    ) -> Optional[Tuple[int, float]]:
        """
        Recognize face by comparing with known encodings.

        Args:
            face_encoding: Face encoding to match
            known_encodings: Dictionary mapping user_id to encoding

        Returns:
            Tuple of (user_id, distance) or None if no match
        """
        if not known_encodings:
            logger.warning("No known faces in database")
            return None

        # Calculate distances to all known faces
        user_ids = list(known_encodings.keys())
        encodings = list(known_encodings.values())

        distances = fr.face_distance(encodings, face_encoding)

        # Find best match
        best_match_idx = np.argmin(distances)
        best_distance = distances[best_match_idx]

        # Check if within tolerance
        if best_distance <= self.tolerance:
            user_id = user_ids[best_match_idx]
            confidence = 1.0 - best_distance
            logger.info(f"Face recognized: user_id={user_id}, confidence={confidence:.2f}")
            return user_id, confidence
        else:
            logger.info(f"No match found (best distance: {best_distance:.2f})")
            return None

    def enroll_user(
        self,
        user_name: str,
        num_samples: int = 3
    ) -> Optional[List[np.ndarray]]:
        """
        Enroll new user by capturing multiple face samples.

        Args:
            user_name: User's name
            num_samples: Number of face samples to capture

        Returns:
            List of face encodings or None
        """
        logger.info(f"Enrolling user: {user_name}")

        if not self.open_camera():
            return None

        encodings = []

        for i in range(num_samples):
            logger.info(f"Capturing sample {i+1}/{num_samples}...")

            result = self.capture_and_encode_face()

            if result is None:
                logger.error(f"Failed to capture sample {i+1}")
                continue

            frame, encoding = result
            encodings.append(encoding)

            # Wait between samples
            if i < num_samples - 1:
                logger.info("Please move slightly and wait...")
                time.sleep(2)

        self.close_camera()

        if len(encodings) < num_samples:
            logger.warning(f"Only captured {len(encodings)}/{num_samples} samples")

        if not encodings:
            logger.error("Failed to enroll user - no samples captured")
            return None

        # Average encodings for better accuracy
        averaged_encoding = np.mean(encodings, axis=0)

        logger.info(f"User {user_name} enrolled successfully with {len(encodings)} samples")
        return encodings

    def identify_user(
        self,
        known_encodings: Dict[int, np.ndarray]
    ) -> Optional[Tuple[int, float]]:
        """
        Identify user from camera.

        Args:
            known_encodings: Dictionary mapping user_id to face encoding

        Returns:
            Tuple of (user_id, confidence) or None
        """
        logger.info("Starting user identification...")

        result = self.capture_and_encode_face()

        if result is None:
            logger.error("Failed to capture face for identification")
            return None

        frame, encoding = result

        # Recognize face
        match = self.recognize_face(encoding, known_encodings)

        self.close_camera()

        return match

    def load_known_faces(self, encodings_dict: Dict[int, np.ndarray]):
        """
        Load known faces into memory.

        Args:
            encodings_dict: Dictionary mapping user_id to face encoding
        """
        self.known_face_user_ids = list(encodings_dict.keys())
        self.known_face_encodings = list(encodings_dict.values())

        logger.info(f"Loaded {len(self.known_face_user_ids)} known faces")

    def draw_face_box(
        self,
        frame: np.ndarray,
        face_location: Tuple[int, int, int, int],
        label: str = "",
        color: Tuple[int, int, int] = (0, 255, 0)
    ) -> np.ndarray:
        """
        Draw bounding box around face.

        Args:
            frame: Image frame
            face_location: Face location (top, right, bottom, left)
            label: Text label to display
            color: Box color (BGR)

        Returns:
            Frame with box drawn
        """
        top, right, bottom, left = face_location

        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Draw label
        if label:
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, cv2.FILLED)
            cv2.putText(
                frame,
                label,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

        return frame

    def __enter__(self):
        """Context manager entry"""
        self.open_camera()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_camera()

    def __del__(self):
        """Cleanup on deletion"""
        self.close_camera()


def test_face_recognition():
    """Test face recognition"""
    logger.info("Testing Face Recognition...")

    try:
        # Initialize recognizer
        recognizer = FaceRecognizer()

        # Test camera
        logger.info("\nTesting camera access...")
        if recognizer.open_camera():
            frame = recognizer.capture_frame()

            if frame is not None:
                logger.info(f"Captured frame: {frame.shape}")

                # Detect faces
                faces = recognizer.detect_faces(frame)
                logger.info(f"Detected {len(faces)} face(s)")

                if faces:
                    # Try encoding
                    encoding = recognizer.encode_face(frame, faces[0])
                    if encoding is not None:
                        logger.info(f"Face encoding shape: {encoding.shape}")

            recognizer.close_camera()
        else:
            logger.warning("Camera test skipped - no camera available")

    except Exception as e:
        logger.error(f"Face recognition test failed: {e}")

    logger.info("\nTest completed!")


if __name__ == "__main__":
    test_face_recognition()

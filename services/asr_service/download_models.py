#!/usr/bin/env python3
"""
Model Download Script for ASR Service

Downloads required models for speech recognition, VAD, face recognition, etc.
Run this script before first use to download all necessary models.
"""

import os
import sys
import zipfile
import tarfile
import requests
from pathlib import Path
from typing import Optional
from loguru import logger


class ModelDownloader:
    """Downloads and extracts models for ASR service"""

    def __init__(self, models_dir: str = "shared/models"):
        """
        Initialize model downloader.

        Args:
            models_dir: Base directory for model storage
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Model downloader initialized: {self.models_dir}")

    def download_file(
        self,
        url: str,
        output_path: Path,
        chunk_size: int = 8192
    ) -> bool:
        """
        Download file from URL.

        Args:
            url: Download URL
            output_path: Output file path
            chunk_size: Download chunk size

        Returns:
            True if successful
        """
        try:
            logger.info(f"Downloading: {url}")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rProgress: {progress:.1f}%", end='', flush=True)

            print()  # New line after progress
            logger.info(f"Downloaded: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False

    def extract_zip(self, zip_path: Path, extract_dir: Path) -> bool:
        """
        Extract ZIP archive.

        Args:
            zip_path: Path to ZIP file
            extract_dir: Extraction directory

        Returns:
            True if successful
        """
        try:
            logger.info(f"Extracting: {zip_path}")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            logger.info(f"Extracted to: {extract_dir}")
            return True

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

    def extract_tar(self, tar_path: Path, extract_dir: Path) -> bool:
        """
        Extract TAR archive.

        Args:
            tar_path: Path to TAR file
            extract_dir: Extraction directory

        Returns:
            True if successful
        """
        try:
            logger.info(f"Extracting: {tar_path}")

            with tarfile.open(tar_path, 'r') as tar_ref:
                tar_ref.extractall(extract_dir)

            logger.info(f"Extracted to: {extract_dir}")
            return True

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

    def download_vosk_model(
        self,
        model_name: str,
        url: str,
        extract: bool = True
    ) -> bool:
        """
        Download Vosk ASR model.

        Args:
            model_name: Model name
            url: Download URL
            extract: Extract after download

        Returns:
            True if successful
        """
        model_dir = self.models_dir / "asr"
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / model_name

        # Check if already exists
        if model_path.exists():
            logger.info(f"Model already exists: {model_name}")
            return True

        # Download
        zip_path = model_dir / f"{model_name}.zip"

        if not self.download_file(url, zip_path):
            return False

        # Extract
        if extract:
            if not self.extract_zip(zip_path, model_dir):
                return False

            # Remove zip file
            zip_path.unlink()
            logger.info(f"Removed archive: {zip_path}")

        logger.info(f"Vosk model installed: {model_name}")
        return True

    def download_silero_vad(self) -> bool:
        """
        Download Silero VAD model.

        Returns:
            True if successful
        """
        vad_dir = self.models_dir / "vad"
        vad_dir.mkdir(parents=True, exist_ok=True)

        model_path = vad_dir / "silero_vad.jit"

        # Check if already exists
        if model_path.exists():
            logger.info("Silero VAD model already exists")
            return True

        # Download
        url = "https://raw.githubusercontent.com/snakers4/silero-vad/master/files/silero_vad.jit"

        if not self.download_file(url, model_path):
            return False

        logger.info("Silero VAD model installed")
        return True

    def download_dlib_models(self) -> bool:
        """
        Download dlib models for face recognition.

        Returns:
            True if successful
        """
        face_dir = self.models_dir / "face"
        face_dir.mkdir(parents=True, exist_ok=True)

        # Face recognition model
        face_model_path = face_dir / "dlib_face_recognition_resnet_model_v1.dat"

        if not face_model_path.exists():
            logger.info("Downloading dlib face recognition model...")
            url = "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2"
            bz2_path = face_dir / "dlib_face_recognition_resnet_model_v1.dat.bz2"

            if self.download_file(url, bz2_path):
                # Extract bz2
                import bz2
                with bz2.open(bz2_path, 'rb') as f_in:
                    with open(face_model_path, 'wb') as f_out:
                        f_out.write(f_in.read())

                bz2_path.unlink()
                logger.info("Face recognition model installed")

        # Landmark detection model
        landmark_model_path = face_dir / "shape_predictor_68_face_landmarks.dat"

        if not landmark_model_path.exists():
            logger.info("Downloading dlib landmark detection model...")
            url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            bz2_path = face_dir / "shape_predictor_68_face_landmarks.dat.bz2"

            if self.download_file(url, bz2_path):
                # Extract bz2
                import bz2
                with bz2.open(bz2_path, 'rb') as f_in:
                    with open(landmark_model_path, 'wb') as f_out:
                        f_out.write(f_in.read())

                bz2_path.unlink()
                logger.info("Landmark detection model installed")

        return True

    def download_all_models(self):
        """Download all required models"""
        logger.info("=" * 60)
        logger.info("Downloading ASR Service Models")
        logger.info("=" * 60)

        # Vosk English model
        logger.info("\n[1/4] Downloading Vosk English model...")
        self.download_vosk_model(
            model_name="vosk-model-small-en-us-0.15",
            url="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        )

        # Vosk Russian model
        logger.info("\n[2/4] Downloading Vosk Russian model...")
        self.download_vosk_model(
            model_name="vosk-model-small-ru-0.22",
            url="https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
        )

        # Silero VAD
        logger.info("\n[3/4] Downloading Silero VAD model...")
        self.download_silero_vad()

        # Dlib models (optional - can be skipped if face recognition not needed)
        logger.info("\n[4/4] Downloading face recognition models (optional)...")
        try:
            self.download_dlib_models()
        except Exception as e:
            logger.warning(f"Face recognition models download failed: {e}")
            logger.warning("Face recognition will not be available")

        logger.info("\n" + "=" * 60)
        logger.info("Model download complete!")
        logger.info("=" * 60)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print summary of downloaded models"""
        logger.info("\nInstalled models:")

        asr_dir = self.models_dir / "asr"
        if asr_dir.exists():
            models = list(asr_dir.iterdir())
            logger.info(f"  ASR models: {len([m for m in models if m.is_dir()])} models")

        vad_dir = self.models_dir / "vad"
        if vad_dir.exists() and (vad_dir / "silero_vad.jit").exists():
            logger.info("  VAD model: Silero VAD ✓")

        face_dir = self.models_dir / "face"
        if face_dir.exists():
            face_models = list(face_dir.glob("*.dat"))
            logger.info(f"  Face recognition models: {len(face_models)} models")

        logger.info("\nASR service is ready to use!")


def main():
    """Main function"""
    logger.info("ASR Service Model Downloader")
    logger.info("This will download required models for speech recognition\n")

    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)

    logger.info(f"Project root: {project_root}")

    # Create downloader
    downloader = ModelDownloader()

    # Download all models
    try:
        downloader.download_all_models()
    except KeyboardInterrupt:
        logger.warning("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nDownload failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

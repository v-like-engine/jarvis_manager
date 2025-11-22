"""
Model Manager - Download and manage LLM models

Handles:
- Downloading models from HuggingFace
- Verifying model integrity
- Managing local model storage
- Model metadata and configuration
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from huggingface_hub import hf_hub_download, HfApi

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages LLM model downloads and storage"""

    def __init__(self, config_path: str):
        """
        Initialize ModelManager

        Args:
            config_path: Path to llm_config.yaml
        """
        self.config = self._load_config(config_path)
        self.models_dir = Path(self.config["service"]["model"]["models_dir"])
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.model_config = self.config["service"]["model"]
        self.api = HfApi()

        logger.info(f"ModelManager initialized. Models directory: {self.models_dir}")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_model_path(self) -> Path:
        """
        Get the path to the local model file

        Returns:
            Path to the model file
        """
        model_filename = self.model_config["filename"]
        return self.models_dir / model_filename

    def is_model_downloaded(self) -> bool:
        """
        Check if the model is already downloaded

        Returns:
            True if model exists locally
        """
        model_path = self.get_model_path()
        return model_path.exists() and model_path.is_file()

    def get_model_size(self) -> Optional[int]:
        """
        Get the size of the downloaded model in bytes

        Returns:
            Size in bytes, or None if not downloaded
        """
        if not self.is_model_downloaded():
            return None

        return self.get_model_path().stat().st_size

    def get_model_size_mb(self) -> Optional[float]:
        """
        Get the size of the downloaded model in MB

        Returns:
            Size in MB, or None if not downloaded
        """
        size_bytes = self.get_model_size()
        if size_bytes is None:
            return None

        return size_bytes / (1024 * 1024)

    def download_model(self, force: bool = False) -> Path:
        """
        Download the model from HuggingFace

        Args:
            force: If True, re-download even if model exists

        Returns:
            Path to the downloaded model

        Raises:
            Exception: If download fails
        """
        model_path = self.get_model_path()

        if self.is_model_downloaded() and not force:
            logger.info(f"Model already downloaded: {model_path}")
            return model_path

        repo_id = self.model_config["repo_id"]
        filename = self.model_config["filename"]

        logger.info(f"Downloading model: {repo_id}/{filename}")
        logger.info("This may take several minutes...")

        try:
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=str(self.models_dir),
                local_dir=str(self.models_dir),
                local_dir_use_symlinks=False,
            )

            logger.info(f"Model downloaded successfully: {downloaded_path}")

            # Verify the download
            if not os.path.exists(downloaded_path):
                raise FileNotFoundError(f"Downloaded model not found: {downloaded_path}")

            size_mb = os.path.getsize(downloaded_path) / (1024 * 1024)
            logger.info(f"Model size: {size_mb:.2f} MB")

            return Path(downloaded_path)

        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise

    def verify_model(self) -> bool:
        """
        Verify that the model file is valid

        Returns:
            True if model is valid
        """
        model_path = self.get_model_path()

        if not self.is_model_downloaded():
            logger.error("Model not downloaded")
            return False

        # Basic verification: check file size
        size = self.get_model_size()
        if size is None or size < 1024 * 1024:  # Less than 1MB is suspicious
            logger.error(f"Model file seems too small: {size} bytes")
            return False

        # Check if file is readable
        try:
            with open(model_path, "rb") as f:
                # Read first few bytes to check if file is accessible
                header = f.read(4)
                if len(header) < 4:
                    logger.error("Model file appears to be empty or corrupt")
                    return False
        except Exception as e:
            logger.error(f"Failed to read model file: {e}")
            return False

        logger.info("Model verification passed")
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model

        Returns:
            Dictionary with model information
        """
        info = {
            "name": self.model_config["name"],
            "variant": self.model_config["variant"],
            "repo_id": self.model_config["repo_id"],
            "filename": self.model_config["filename"],
            "downloaded": self.is_model_downloaded(),
            "path": str(self.get_model_path()) if self.is_model_downloaded() else None,
            "size_mb": self.get_model_size_mb(),
        }

        return info

    def delete_model(self) -> bool:
        """
        Delete the downloaded model

        Returns:
            True if deleted successfully
        """
        model_path = self.get_model_path()

        if not self.is_model_downloaded():
            logger.warning("No model to delete")
            return False

        try:
            model_path.unlink()
            logger.info(f"Model deleted: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            return False

    def ensure_model_ready(self) -> Path:
        """
        Ensure the model is downloaded and ready to use

        Returns:
            Path to the model file

        Raises:
            Exception: If model cannot be prepared
        """
        if not self.is_model_downloaded():
            logger.info("Model not found. Downloading...")
            if self.model_config.get("auto_download", True):
                self.download_model()
            else:
                raise FileNotFoundError(
                    "Model not downloaded and auto_download is disabled. "
                    "Please download the model manually."
                )

        if not self.verify_model():
            raise ValueError("Model verification failed. Model may be corrupted.")

        return self.get_model_path()


if __name__ == "__main__":
    # Test the model manager
    logging.basicConfig(level=logging.INFO)

    config_path = "/home/user/jarvis_manager/services/llm_service/config/llm_config.yaml"
    manager = ModelManager(config_path)

    print("Model Info:")
    print(manager.get_model_info())

    if not manager.is_model_downloaded():
        print("\nModel not downloaded. Run download_model() to download.")
    else:
        print("\nModel is ready!")

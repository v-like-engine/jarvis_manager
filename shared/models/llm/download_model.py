#!/usr/bin/env python3
"""
LLM Model Download Script

Downloads the configured LLM model from HuggingFace.
This script can be run standalone or will be called automatically
by the LLM service on first startup.
"""

import sys
import logging
from pathlib import Path

# Add service src to path
SERVICE_SRC = Path(__file__).parent.parent.parent / "services" / "llm_service" / "src"
sys.path.insert(0, str(SERVICE_SRC))

from model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Download the LLM model"""
    print("=" * 60)
    print("Jarvis LLM Model Downloader")
    print("=" * 60)
    print()

    # Configuration path
    config_path = Path(__file__).parent.parent.parent / "services" / "llm_service" / "config" / "llm_config.yaml"

    if not config_path.exists():
        logger.error(f"Configuration not found: {config_path}")
        sys.exit(1)

    try:
        # Initialize model manager
        logger.info("Initializing model manager...")
        manager = ModelManager(str(config_path))

        # Get model info
        model_info = manager.get_model_info()
        print(f"\nModel: {model_info['name']}")
        print(f"Variant: {model_info['variant']}")
        print(f"Repository: {model_info['repo_id']}")
        print(f"Filename: {model_info['filename']}")
        print()

        # Check if already downloaded
        if manager.is_model_downloaded():
            size_mb = manager.get_model_size_mb()
            print(f"✓ Model already downloaded ({size_mb:.2f} MB)")
            print(f"  Path: {manager.get_model_path()}")
            print()

            response = input("Re-download? [y/N]: ").strip().lower()
            if response != 'y':
                print("Skipping download.")

                # Verify existing model
                print("\nVerifying model...")
                if manager.verify_model():
                    print("✓ Model verification passed!")
                    print("\nModel is ready to use.")
                    return 0
                else:
                    print("✗ Model verification failed!")
                    print("Re-downloading...")

        # Download model
        print("\nDownloading model...")
        print("This may take several minutes depending on your connection.")
        print("(Model size: ~2.3 GB)")
        print()

        model_path = manager.download_model(force=True)

        print()
        print("✓ Download complete!")
        print(f"  Path: {model_path}")

        # Verify model
        print("\nVerifying model...")
        if manager.verify_model():
            print("✓ Model verification passed!")

            # Show final info
            size_mb = manager.get_model_size_mb()
            print()
            print("=" * 60)
            print("Model Ready!")
            print("=" * 60)
            print(f"Model: {model_info['name']}")
            print(f"Size: {size_mb:.2f} MB")
            print(f"Path: {model_path}")
            print()
            print("You can now start the LLM service.")
            print("=" * 60)

            return 0
        else:
            print("✗ Model verification failed!")
            print("The downloaded model may be corrupted.")
            print("Please try downloading again.")
            return 1

    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        return 1

    except Exception as e:
        logger.error(f"Download failed: {e}", exc_info=True)
        print()
        print("=" * 60)
        print("Download Failed!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Ensure you have ~5GB free disk space")
        print("3. Check HuggingFace is accessible: ping huggingface.co")
        print("4. Try again later if HuggingFace is down")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

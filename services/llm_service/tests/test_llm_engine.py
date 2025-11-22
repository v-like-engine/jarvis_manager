"""
Unit tests for LLMEngine

Note: These tests require the model to be downloaded.
They will be skipped if the model is not available.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_engine import LLMEngine

# Test configuration
MODEL_PATH = "/home/user/jarvis_manager/shared/models/llm/Phi-3-mini-4k-instruct-q4.gguf"
SETTINGS_PATH = str(Path(__file__).parent.parent / "config" / "model_settings.yaml")


@pytest.fixture
def model_available():
    """Check if model is available"""
    return Path(MODEL_PATH).exists()


@pytest.fixture
def llm_engine(model_available):
    """Create LLMEngine instance (skip if model not available)"""
    if not model_available:
        pytest.skip("Model not downloaded")

    return LLMEngine(
        model_path=MODEL_PATH,
        model_settings_path=SETTINGS_PATH,
        n_ctx=512,  # Smaller context for faster tests
    )


def test_initialization(llm_engine):
    """Test LLMEngine initialization"""
    assert llm_engine is not None
    assert llm_engine.llm is not None


def test_count_tokens(llm_engine):
    """Test token counting"""
    text = "Hello, world!"
    tokens = llm_engine.count_tokens(text)

    assert tokens > 0
    assert tokens < len(text)  # Should be fewer tokens than characters


def test_get_max_context_length(llm_engine):
    """Test getting max context length"""
    max_ctx = llm_engine.get_max_context_length()
    assert max_ctx > 0


def test_get_model_info(llm_engine):
    """Test getting model info"""
    info = llm_engine.get_model_info()

    assert info is not None
    assert "model_path" in info
    assert "n_ctx" in info
    assert "generation_params" in info


@pytest.mark.slow
def test_generate(llm_engine):
    """Test basic text generation"""
    prompt = "Hello! My name is"
    response = llm_engine.generate(prompt, max_tokens=10)

    assert response is not None
    assert len(response) > 0


@pytest.mark.slow
def test_generate_with_params(llm_engine):
    """Test generation with custom parameters"""
    prompt = "The capital of France is"
    response = llm_engine.generate(
        prompt,
        max_tokens=10,
        temperature=0.1,  # Low temperature for deterministic output
        top_p=0.9
    )

    assert response is not None
    assert len(response) > 0


@pytest.mark.slow
def test_generate_with_character(llm_engine):
    """Test generation with character-specific settings"""
    prompt = "Hello!"
    response = llm_engine.generate_with_character(
        prompt,
        character_name="gerald",
        scenario="chat"
    )

    assert response is not None
    assert len(response) > 0


def test_generation_params_override(llm_engine):
    """Test that generation parameters can be overridden"""
    # This test doesn't actually generate, just checks the structure
    assert llm_engine.generation_params is not None
    assert "temperature" in llm_engine.generation_params
    assert "max_tokens" in llm_engine.generation_params


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])

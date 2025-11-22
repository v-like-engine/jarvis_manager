"""
Unit tests for PromptBuilder
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_builder import PromptBuilder


@pytest.fixture
def prompts_dir():
    """Get prompts directory path"""
    return str(Path(__file__).parent.parent / "prompts")


@pytest.fixture
def prompt_builder(prompts_dir):
    """Create PromptBuilder instance"""
    return PromptBuilder(prompts_dir)


@pytest.fixture
def sample_system_prompt():
    """Sample system prompt"""
    return "You are a helpful assistant."


def test_initialization(prompt_builder):
    """Test PromptBuilder initialization"""
    assert prompt_builder is not None
    assert prompt_builder.system_prompts is not None
    assert prompt_builder.safety_prompts is not None
    assert prompt_builder.greeting_templates is not None


def test_build_simple_prompt(prompt_builder, sample_system_prompt):
    """Test building a simple prompt"""
    prompt = prompt_builder.build_simple_prompt(
        system_prompt=sample_system_prompt,
        user_message="Hello"
    )

    assert prompt is not None
    assert sample_system_prompt in prompt
    assert "Hello" in prompt


def test_build_chat_prompt(prompt_builder, sample_system_prompt):
    """Test building a chat prompt"""
    prompt = prompt_builder.build_chat_prompt(
        user_input="Hello, how are you?",
        system_prompt=sample_system_prompt,
        context=None,
        language="en"
    )

    assert prompt is not None
    assert sample_system_prompt in prompt
    assert "Hello, how are you?" in prompt


def test_build_chat_prompt_with_context(prompt_builder, sample_system_prompt):
    """Test building a chat prompt with context"""
    context = "User: Hi\nAssistant: Hello!"

    prompt = prompt_builder.build_chat_prompt(
        user_input="How are you?",
        system_prompt=sample_system_prompt,
        context=context,
        language="en"
    )

    assert prompt is not None
    assert context in prompt
    assert "How are you?" in prompt


def test_build_confirmation_prompt(prompt_builder, sample_system_prompt):
    """Test building a confirmation prompt"""
    prompt = prompt_builder.build_confirmation_prompt(
        command="shutdown system",
        system_prompt=sample_system_prompt,
        language="en"
    )

    assert prompt is not None
    assert "shutdown system" in prompt


def test_build_safety_prompt(prompt_builder, sample_system_prompt):
    """Test building a safety prompt"""
    prompt = prompt_builder.build_safety_prompt(
        command="rm -rf /",
        description="delete all files",
        system_prompt=sample_system_prompt,
        language="en"
    )

    assert prompt is not None
    assert "rm -rf /" in prompt


def test_build_clarification_prompt(prompt_builder, sample_system_prompt):
    """Test building a clarification prompt"""
    prompt = prompt_builder.build_clarification_prompt(
        user_input="do the thing",
        system_prompt=sample_system_prompt,
        context=None,
        language="en"
    )

    assert prompt is not None
    assert "do the thing" in prompt


def test_build_error_prompt(prompt_builder, sample_system_prompt):
    """Test building an error prompt"""
    prompt = prompt_builder.build_error_prompt(
        error="Connection timeout",
        system_prompt=sample_system_prompt,
        language="en"
    )

    assert prompt is not None
    assert "Connection timeout" in prompt or "Error" in prompt


def test_get_safety_warning(prompt_builder):
    """Test getting safety warnings"""
    warning = prompt_builder.get_safety_warning(
        operation_type="file_deletion",
        language="en",
        target="/important/file.txt"
    )

    assert warning is not None
    assert len(warning) > 0


def test_get_safety_warning_russian(prompt_builder):
    """Test getting safety warnings in Russian"""
    warning = prompt_builder.get_safety_warning(
        operation_type="file_deletion",
        language="ru",
        target="/важный/файл.txt"
    )

    assert warning is not None
    assert len(warning) > 0


def test_format_context(prompt_builder):
    """Test context formatting"""
    long_context = "A" * 1000

    formatted = prompt_builder.format_context(long_context, max_length=100)
    assert len(formatted) <= 100


def test_format_empty_context(prompt_builder):
    """Test formatting empty context"""
    formatted = prompt_builder.format_context("")
    assert formatted == ""


def test_multilanguage_prompts(prompt_builder, sample_system_prompt):
    """Test building prompts in different languages"""
    # English
    prompt_en = prompt_builder.build_chat_prompt(
        user_input="Test",
        system_prompt=sample_system_prompt,
        language="en"
    )

    # Russian
    prompt_ru = prompt_builder.build_chat_prompt(
        user_input="Тест",
        system_prompt=sample_system_prompt,
        language="ru"
    )

    assert prompt_en is not None
    assert prompt_ru is not None


def test_scenario_template(prompt_builder, sample_system_prompt):
    """Test scenario-specific templates"""
    scenarios = ["chat", "confirmation", "safety_check", "clarification"]

    for scenario in scenarios:
        prompt = prompt_builder.build_prompt(
            user_input="test",
            system_prompt=sample_system_prompt,
            scenario=scenario,
            language="en"
        )
        assert prompt is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

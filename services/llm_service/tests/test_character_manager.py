"""
Unit tests for CharacterManager
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from character_manager import CharacterManager


@pytest.fixture
def characters_dir():
    """Get characters directory path"""
    return str(Path(__file__).parent.parent / "characters")


@pytest.fixture
def character_manager(characters_dir):
    """Create CharacterManager instance"""
    return CharacterManager(characters_dir)


def test_initialization(character_manager):
    """Test CharacterManager initialization"""
    assert character_manager is not None
    assert len(character_manager.characters) > 0
    assert character_manager.current_language == "en"


def test_list_characters(character_manager):
    """Test listing available characters"""
    characters = character_manager.list_characters()
    assert isinstance(characters, list)
    assert "gerald" in characters


def test_load_character(character_manager):
    """Test loading a character"""
    character = character_manager.load_character("gerald")
    assert character is not None
    assert character.name == "Gerald"
    assert character_manager.current_character == character


def test_load_invalid_character(character_manager):
    """Test loading non-existent character"""
    with pytest.raises(ValueError):
        character_manager.load_character("nonexistent")


def test_get_system_prompt(character_manager):
    """Test getting system prompt"""
    character_manager.load_character("gerald")

    # Test English prompt
    prompt_en = character_manager.get_system_prompt("en")
    assert prompt_en is not None
    assert len(prompt_en) > 0
    assert "Gerald" in prompt_en

    # Test Russian prompt
    prompt_ru = character_manager.get_system_prompt("ru")
    assert prompt_ru is not None
    assert len(prompt_ru) > 0
    assert "Геральд" in prompt_ru


def test_get_template(character_manager):
    """Test getting template responses"""
    character_manager.load_character("gerald")

    # Test greeting template
    greeting = character_manager.get_template("greeting", "en")
    assert greeting is not None
    assert len(greeting) > 0

    # Test confirmation template
    confirmation = character_manager.get_template("confirmation", "en")
    assert confirmation is not None
    assert len(confirmation) > 0


def test_get_template_with_format(character_manager):
    """Test template formatting"""
    character_manager.load_character("gerald")

    # Test safety warning with format arguments
    warning = character_manager.get_template(
        "safety_warning",
        "en",
        action="delete all files"
    )
    assert warning is not None
    assert "delete all files" in warning


def test_set_language(character_manager):
    """Test setting language"""
    character_manager.load_character("gerald")

    character_manager.set_language("ru")
    assert character_manager.current_language == "ru"

    character_manager.set_language("en")
    assert character_manager.current_language == "en"


def test_set_emotion(character_manager):
    """Test setting emotion"""
    character_manager.load_character("gerald")

    character_manager.set_emotion("stern")
    assert character_manager.current_emotion == "stern"

    character_manager.set_emotion("neutral")
    assert character_manager.current_emotion == "neutral"


def test_get_voice_settings(character_manager):
    """Test getting voice settings"""
    character_manager.load_character("gerald")

    # Test English voice settings
    voice_en = character_manager.get_voice_settings("en")
    assert voice_en is not None
    assert "rate" in voice_en
    assert "pitch" in voice_en

    # Test Russian voice settings
    voice_ru = character_manager.get_voice_settings("ru")
    assert voice_ru is not None
    assert "rate" in voice_ru


def test_get_response_rules(character_manager):
    """Test getting response rules"""
    character_manager.load_character("gerald")

    rules = character_manager.get_response_rules()
    assert rules is not None
    assert rules.max_length > 0
    assert rules.temperature > 0


def test_get_character_info(character_manager):
    """Test getting character info"""
    character_manager.load_character("gerald")

    info = character_manager.get_character_info()
    assert info is not None
    assert info["name"] == "Gerald"
    assert "traits" in info
    assert "archetype" in info


def test_multiple_characters(character_manager):
    """Test switching between characters"""
    # Load first character
    char1 = character_manager.load_character("gerald")
    assert character_manager.current_character.name == "Gerald"

    # If there are other characters, test switching
    characters = character_manager.list_characters()
    if len(characters) > 1:
        other_char = [c for c in characters if c != "gerald"][0]
        char2 = character_manager.load_character(other_char)
        assert character_manager.current_character != char1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

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


def test_winnie_pooh_character(character_manager):
    """Test Winnie Pooh character"""
    characters = character_manager.list_characters()

    if "winnie pooh" in characters:
        character = character_manager.load_character("winnie pooh")
        assert character is not None
        assert character.name == "Winnie Pooh"
        assert "gentle" in character.personality.traits
        assert "philosophical" in character.personality.traits

        # Test Russian and English prompts
        prompt_ru = character_manager.get_system_prompt("ru")
        assert "Винни Пух" in prompt_ru

        prompt_en = character_manager.get_system_prompt("en")
        assert "Winnie" in prompt_en or "Pooh" in prompt_en

        # Test greeting templates
        greeting_ru = character_manager.get_template("greeting", "ru")
        assert greeting_ru is not None
        assert len(greeting_ru) > 0


def test_rapunzel_character(character_manager):
    """Test Rapunzel character"""
    characters = character_manager.list_characters()

    if "rapunzel" in characters:
        character = character_manager.load_character("rapunzel")
        assert character is not None
        assert character.name == "Rapunzel"
        assert "cheerful" in character.personality.traits
        assert "curious" in character.personality.traits

        # Test bilingual prompts
        prompt_en = character_manager.get_system_prompt("en")
        assert "Rapunzel" in prompt_en
        assert "princess" in prompt_en.lower()

        prompt_ru = character_manager.get_system_prompt("ru")
        assert "Рапунцель" in prompt_ru

        # Test enthusiastic responses
        greeting_en = character_manager.get_template("greeting", "en")
        assert greeting_en is not None
        # Rapunzel should be enthusiastic (likely has exclamation marks)

        # Test voice settings (should be energetic)
        voice_en = character_manager.get_voice_settings("en")
        assert voice_en["rate"] >= 180  # Energetic rate


def test_terminator_character(character_manager):
    """Test Terminator character"""
    characters = character_manager.list_characters()

    if "terminator" in characters:
        character = character_manager.load_character("terminator")
        assert character is not None
        assert character.name == "Terminator"
        assert "robotic" in character.personality.traits
        assert "mission_focused" in character.personality.traits

        # Test bilingual prompts
        prompt_en = character_manager.get_system_prompt("en")
        assert "Terminator" in prompt_en or "cybernetic" in prompt_en.lower()

        prompt_ru = character_manager.get_system_prompt("ru")
        assert "Терминатор" in prompt_ru or "кибернетический" in prompt_ru

        # Test direct responses
        confirmation_en = character_manager.get_template("confirmation", "en")
        assert confirmation_en is not None
        # Terminator should be very brief
        assert len(confirmation_en) < 30  # Short responses

        # Test voice settings (should be deep and robotic)
        voice_en = character_manager.get_voice_settings("en")
        assert voice_en["pitch"] < 0  # Lower pitch
        assert voice_en["volume"] >= 0.9  # Loud


def test_character_switching(character_manager):
    """Test switching between all available characters"""
    characters = character_manager.list_characters()

    # Should have at least Gerald + 3 new characters
    assert len(characters) >= 4

    # Test switching between characters
    for char_name in ["gerald", "winnie pooh", "rapunzel", "terminator"]:
        if char_name in characters:
            char = character_manager.load_character(char_name)
            assert character_manager.current_character == char

            # Test that each character has unique traits
            info = character_manager.get_character_info()
            assert "traits" in info
            assert len(info["traits"]) > 0


def test_character_previews(character_manager):
    """Test character preview functionality"""
    characters = character_manager.list_characters()

    for char_name in characters:
        preview = character_manager.get_character_preview(char_name, "en")

        assert "name" in preview
        assert "description" in preview
        assert "archetype" in preview
        assert "traits" in preview
        assert "sample_responses" in preview
        assert "greeting" in preview["sample_responses"]
        assert "confirmation" in preview["sample_responses"]

        # Test voice settings in preview
        if "voice_settings" in preview:
            voice = preview["voice_settings"]
            if voice:
                assert "rate" in voice
                assert voice["rate"] > 0


def test_all_characters_info(character_manager):
    """Test getting info for all characters at once"""
    all_info = character_manager.get_all_characters_info()

    assert isinstance(all_info, list)
    assert len(all_info) >= 4  # Gerald + 3 new characters

    # Verify each character has required fields
    for char_info in all_info:
        assert "name" in char_info
        assert "description" in char_info
        assert "archetype" in char_info
        assert "languages" in char_info
        assert "traits" in char_info


def test_character_personalities_differ(character_manager):
    """Test that each character has a distinct personality"""
    characters_to_test = []

    # Load each character and check personality
    for char_name in ["gerald", "winnie pooh", "rapunzel", "terminator"]:
        if char_name in character_manager.list_characters():
            char = character_manager.load_character(char_name)
            characters_to_test.append({
                "name": char.name,
                "archetype": char.personality.archetype,
                "traits": set(char.personality.traits),
                "verbosity": char.personality.communication_style.get("verbosity"),
            })

    # Should have at least 3 different characters
    assert len(characters_to_test) >= 3

    # Check that archetypes are different
    archetypes = [c["archetype"] for c in characters_to_test]
    assert len(set(archetypes)) == len(archetypes)  # All unique

    # Check that trait sets are different
    for i, char1 in enumerate(characters_to_test):
        for char2 in characters_to_test[i+1:]:
            # Traits should not be identical
            assert char1["traits"] != char2["traits"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Integration tests for character switching functionality
"""

import pytest
import sys
from pathlib import Path

# Add service paths
llm_service_path = Path(__file__).parent.parent.parent / "services" / "llm_service" / "src"
sys.path.insert(0, str(llm_service_path))

from character_manager import CharacterManager


@pytest.fixture
def characters_dir():
    """Get characters directory"""
    return str(Path(__file__).parent.parent.parent / "services" / "llm_service" / "characters")


@pytest.fixture
def character_manager(characters_dir):
    """Create CharacterManager instance"""
    return CharacterManager(characters_dir)


def test_list_available_characters(character_manager):
    """Test listing all available characters"""
    characters = character_manager.list_characters()

    assert isinstance(characters, list)
    assert len(characters) > 0
    assert "gerald" in characters
    print(f"Available characters: {characters}")


def test_switch_to_gerald(character_manager):
    """Test switching to Gerald character"""
    character = character_manager.load_character("gerald")

    assert character is not None
    assert character.name == "Gerald"
    assert character_manager.current_character.name == "Gerald"
    assert "en" in character.language_support
    assert "ru" in character.language_support


def test_switch_to_winnie_pooh(character_manager):
    """Test switching to Winnie Pooh character"""
    characters = character_manager.list_characters()

    if "winnie pooh" in characters or "winnie_pooh" in characters:
        try:
            character = character_manager.load_character("winnie pooh")
        except ValueError:
            character = character_manager.load_character("winnie_pooh")

        assert character is not None
        assert "Winnie" in character.name or "Pooh" in character.name
        assert character_manager.current_character == character
        assert "en" in character.language_support
        assert "ru" in character.language_support


def test_switch_between_characters(character_manager):
    """Test switching between multiple characters"""
    # Load Gerald
    gerald = character_manager.load_character("gerald")
    assert character_manager.current_character.name == "Gerald"

    # Get prompt from Gerald
    gerald_prompt = character_manager.get_system_prompt("en")
    assert "Gerald" in gerald_prompt or "knight" in gerald_prompt.lower()

    # Load Winnie Pooh (if available)
    characters = character_manager.list_characters()
    if "winnie pooh" in characters or "winnie_pooh" in characters:
        try:
            winnie = character_manager.load_character("winnie pooh")
        except ValueError:
            winnie = character_manager.load_character("winnie_pooh")

        assert character_manager.current_character != gerald
        assert character_manager.current_character == winnie

        # Get prompt from Winnie
        winnie_prompt = character_manager.get_system_prompt("en")
        assert winnie_prompt != gerald_prompt
        assert "Pooh" in winnie_prompt or "bear" in winnie_prompt.lower()

        # Switch back to Gerald
        gerald2 = character_manager.load_character("gerald")
        assert character_manager.current_character == gerald2
        assert character_manager.get_system_prompt("en") == gerald_prompt


def test_character_voice_settings(character_manager):
    """Test that each character has unique voice settings"""
    character_manager.load_character("gerald")

    voice_en = character_manager.get_voice_settings("en")
    assert voice_en is not None
    assert "rate" in voice_en
    assert "pitch" in voice_en

    voice_ru = character_manager.get_voice_settings("ru")
    assert voice_ru is not None


def test_character_personality_preserved(character_manager):
    """Test that character personality is preserved across operations"""
    character_manager.load_character("gerald")

    # Get various templates
    greeting1 = character_manager.get_template("greeting", "en")
    confirmation1 = character_manager.get_template("confirmation", "en")

    # Change language
    character_manager.set_language("ru")

    # Get Russian templates
    greeting_ru = character_manager.get_template("greeting", "ru")
    confirmation_ru = character_manager.get_template("confirmation", "ru")

    # Switch back to English
    character_manager.set_language("en")

    # Verify English templates still work
    greeting2 = character_manager.get_template("greeting", "en")
    confirmation2 = character_manager.get_template("confirmation", "en")

    assert greeting1 is not None
    assert greeting2 is not None
    assert greeting_ru is not None


def test_character_bilingual_support(character_manager):
    """Test bilingual support for characters"""
    characters = character_manager.list_characters()

    for char_name in characters:
        character = character_manager.load_character(char_name)

        # Test English prompts
        prompt_en = character_manager.get_system_prompt("en")
        assert prompt_en is not None
        assert len(prompt_en) > 0

        # Test Russian prompts
        prompt_ru = character_manager.get_system_prompt("ru")
        assert prompt_ru is not None
        assert len(prompt_ru) > 0

        # Prompts should be different
        assert prompt_en != prompt_ru

        print(f"Character '{char_name}' supports both English and Russian")


def test_character_response_rules(character_manager):
    """Test that each character has response generation rules"""
    characters = character_manager.list_characters()

    for char_name in characters:
        character_manager.load_character(char_name)
        rules = character_manager.get_response_rules()

        assert rules is not None
        assert rules.max_length > 0
        assert rules.temperature > 0
        assert rules.temperature <= 2.0
        assert rules.warn_on_dangerous_commands is True
        assert rules.require_confirmation_for_destructive is True

        print(f"Character '{char_name}' has valid response rules")


def test_character_templates_all_types(character_manager):
    """Test that all characters have required templates"""
    characters = character_manager.list_characters()
    required_templates = ["greeting", "confirmation", "refusal", "error"]

    for char_name in characters:
        character_manager.load_character(char_name)

        for template_type in required_templates:
            # Test English
            template_en = character_manager.get_template(template_type, "en")
            assert template_en is not None
            assert len(template_en) > 0

            # Test Russian
            template_ru = character_manager.get_template(template_type, "ru")
            assert template_ru is not None
            assert len(template_ru) > 0

        print(f"Character '{char_name}' has all required templates")


def test_character_info_retrieval(character_manager):
    """Test getting character information"""
    characters = character_manager.list_characters()

    for char_name in characters:
        character_manager.load_character(char_name)
        info = character_manager.get_character_info()

        assert info is not None
        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "archetype" in info
        assert "traits" in info
        assert "languages" in info
        assert "current_language" in info

        assert len(info["name"]) > 0
        assert len(info["traits"]) > 0
        assert len(info["languages"]) > 0

        print(f"Character info: {info['name']} - {info['archetype']}")


def test_character_emotion_system(character_manager):
    """Test character emotion state management"""
    character_manager.load_character("gerald")

    # Test default emotion
    assert character_manager.current_emotion == "neutral"

    # Test setting emotions
    character_manager.set_emotion("stern")
    assert character_manager.current_emotion == "stern"

    character_manager.set_emotion("helpful")
    assert character_manager.current_emotion == "helpful"

    # Reset to neutral
    character_manager.set_emotion("neutral")
    assert character_manager.current_emotion == "neutral"


def test_character_language_switching(character_manager):
    """Test language switching within a character"""
    character_manager.load_character("gerald")

    # Start with English
    character_manager.set_language("en")
    assert character_manager.current_language == "en"

    greeting_en = character_manager.get_template("greeting", "en")
    assert greeting_en is not None

    # Switch to Russian
    character_manager.set_language("ru")
    assert character_manager.current_language == "ru"

    greeting_ru = character_manager.get_template("greeting", "ru")
    assert greeting_ru is not None

    # Greetings should be different
    assert greeting_en != greeting_ru


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

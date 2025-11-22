#!/usr/bin/env python3
"""
Demonstration script for the 3 new characters:
- Винни Пух (Winnie the Pooh)
- Rapunzel (Рапунцель)
- Терминатор (Terminator)

This script showcases each character's unique personality, communication style,
and sample responses in both Russian and English.
"""

import yaml
from pathlib import Path


def load_character(filename):
    """Load a character from YAML file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def display_character_info(character_data, char_file):
    """Display detailed character information"""
    print("=" * 80)
    print(f"CHARACTER: {character_data['name']}")
    print("=" * 80)
    print(f"Source: {char_file}")
    print(f"Version: {character_data['version']}")
    print(f"Description: {character_data['description']}")
    print()

    # Personality
    personality = character_data['personality']
    print("PERSONALITY:")
    print(f"  Archetype: {personality['archetype']}")
    print(f"  Traits: {', '.join(personality['traits'][:8])}")
    print()

    # Communication Style
    comm_style = personality['communication_style']
    print("COMMUNICATION STYLE:")
    for key, value in comm_style.items():
        print(f"  {key}: {value}")
    print()

    # Voice Settings
    voice_settings = character_data.get('voice_settings', {})
    print("VOICE SETTINGS:")
    for lang in ['en', 'ru']:
        if lang in voice_settings:
            settings = voice_settings[lang]
            print(f"  {lang.upper()}: rate={settings.get('rate')} WPM, "
                  f"pitch={settings.get('pitch')}, "
                  f"volume={settings.get('volume')}")
    print()

    # Sample Responses
    prompts = character_data['prompts']
    print("SAMPLE RESPONSES:")
    print()

    print("  ENGLISH:")
    print(f"    Greeting: {prompts.get('greeting_en', ['N/A'])[0]}")
    print(f"    Confirmation: {prompts.get('confirmation_en', ['N/A'])[0]}")
    print(f"    Clarification: {prompts.get('clarification_en', ['N/A'])[0]}")
    print()

    print("  RUSSIAN:")
    print(f"    Приветствие: {prompts.get('greeting_ru', ['N/A'])[0]}")
    print(f"    Подтверждение: {prompts.get('confirmation_ru', ['N/A'])[0]}")
    print(f"    Уточнение: {prompts.get('clarification_ru', ['N/A'])[0]}")
    print()

    # System Prompts (excerpts)
    print("SYSTEM PROMPT EXCERPTS:")
    system_en = prompts.get('system_en', '')
    system_ru = prompts.get('system_ru', '')

    if system_en:
        lines = system_en.strip().split('\n')[:3]
        print("  English:")
        for line in lines:
            if line.strip():
                print(f"    {line.strip()}")

    if system_ru:
        lines = system_ru.strip().split('\n')[:3]
        print("  Russian:")
        for line in lines:
            if line.strip():
                print(f"    {line.strip()}")
    print()

    # Response Rules
    rules = character_data.get('response_rules', {})
    print("RESPONSE GENERATION RULES:")
    print(f"  Max Length: {rules.get('max_length')} words")
    print(f"  Temperature: {rules.get('temperature')}")
    print(f"  Prefer Short: {rules.get('prefer_short_responses')}")
    print()

    # Emotions/Modes
    emotions = character_data.get('emotions', {})
    if emotions:
        print(f"AVAILABLE EMOTIONS/MODES: {', '.join(emotions.keys())}")
        print()


def main():
    """Main demonstration"""
    characters_dir = Path("services/llm_service/characters")

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  GERALD DESKTOP MANAGER - NEW CHARACTERS DEMONSTRATION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Character files to demonstrate
    character_files = [
        ("winnie_pooh.yaml", "Винни Пух (Winnie the Pooh)"),
        ("rapunzel.yaml", "Rapunzel (Рапунцель)"),
        ("terminator.yaml", "Терминатор (Terminator)"),
    ]

    for filename, display_name in character_files:
        file_path = characters_dir / filename

        if file_path.exists():
            character_data = load_character(file_path)
            display_character_info(character_data, filename)
        else:
            print(f"ERROR: Character file not found: {file_path}")
            print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Three new characters have been successfully added to Gerald Desktop Manager:")
    print()
    print("1. ВИННИ ПУХ (Winnie the Pooh)")
    print("   - Gentle, philosophical, and thoughtful")
    print("   - Perfect for a calm, contemplative interaction")
    print("   - Slow-paced, warm communication style")
    print()
    print("2. RAPUNZEL (Рапунцель)")
    print("   - Cheerful, curious, and enthusiastic")
    print("   - Energetic and optimistic responses")
    print("   - Asks questions and encourages users")
    print()
    print("3. ТЕРМИНАТОР (Terminator)")
    print("   - Robotic, direct, and mission-focused")
    print("   - No emotions, pure logic and efficiency")
    print("   - Very brief, technical communication")
    print()
    print("All characters support both English and Russian languages!")
    print("Each has unique voice settings, personality traits, and response styles.")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()

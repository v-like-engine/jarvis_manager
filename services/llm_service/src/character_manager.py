"""
Character Manager - Load and manage character personalities

Handles:
- Loading character configurations from YAML files
- Managing character state and settings
- Providing character-specific prompts and templates
- Multi-language support
"""

import logging
import random
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class CharacterPersonality(BaseModel):
    """Character personality model"""
    archetype: str
    traits: List[str]
    communication_style: Dict[str, str]
    behavior: Dict[str, Any]


class CharacterPrompts(BaseModel):
    """Character prompts model"""
    system_en: Optional[str] = None
    system_ru: Optional[str] = None
    greeting_en: Optional[List[str]] = Field(default_factory=list)
    greeting_ru: Optional[List[str]] = Field(default_factory=list)
    confirmation_en: Optional[List[str]] = Field(default_factory=list)
    confirmation_ru: Optional[List[str]] = Field(default_factory=list)
    safety_warning_en: Optional[str] = None
    safety_warning_ru: Optional[str] = None
    refusal_en: Optional[List[str]] = Field(default_factory=list)
    refusal_ru: Optional[List[str]] = Field(default_factory=list)
    clarification_en: Optional[List[str]] = Field(default_factory=list)
    clarification_ru: Optional[List[str]] = Field(default_factory=list)
    error_en: Optional[List[str]] = Field(default_factory=list)
    error_ru: Optional[List[str]] = Field(default_factory=list)
    self_description_en: Optional[str] = None
    self_description_ru: Optional[str] = None


class CharacterResponseRules(BaseModel):
    """Character response generation rules"""
    max_length: int = 150
    max_tokens: int = 150
    require_context: bool = True
    context_window: int = 5
    temperature: float = 0.7
    top_p: float = 0.9
    repetition_penalty: float = 1.1
    prefer_short_responses: bool = False
    use_templates_when_possible: bool = True
    warn_on_dangerous_commands: bool = True
    require_confirmation_for_destructive: bool = True


class Character(BaseModel):
    """Complete character configuration"""
    name: str
    version: str
    description: str
    language_support: List[str]
    personality: CharacterPersonality
    voice_settings: Optional[Dict[str, Dict[str, Any]]] = None
    prompts: CharacterPrompts
    response_rules: CharacterResponseRules
    emotions: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CharacterManager:
    """Manages character personalities and configurations"""

    def __init__(self, characters_dir: str):
        """
        Initialize CharacterManager

        Args:
            characters_dir: Directory containing character YAML files
        """
        self.characters_dir = Path(characters_dir)
        if not self.characters_dir.exists():
            raise FileNotFoundError(f"Characters directory not found: {characters_dir}")

        self.characters: Dict[str, Character] = {}
        self.current_character: Optional[Character] = None
        self.current_language: str = "en"
        self.current_emotion: str = "neutral"

        # Load all characters
        self._load_all_characters()

        logger.info(f"CharacterManager initialized with {len(self.characters)} characters")

    def _load_all_characters(self):
        """Load all character files from the characters directory"""
        for yaml_file in self.characters_dir.glob("*.yaml"):
            # Skip base template and README
            if yaml_file.name in ["character_base.yaml", "README.md"]:
                continue

            try:
                character = self._load_character_file(yaml_file)
                self.characters[character.name.lower()] = character
                logger.info(f"Loaded character: {character.name}")
            except Exception as e:
                logger.error(f"Failed to load character from {yaml_file}: {e}")

    def _load_character_file(self, file_path: Path) -> Character:
        """Load a character from a YAML file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return Character(**data)

    def load_character(self, character_name: str) -> Character:
        """
        Load and set a character as current

        Args:
            character_name: Name of the character to load

        Returns:
            The loaded Character object

        Raises:
            ValueError: If character not found
        """
        char_name_lower = character_name.lower()

        if char_name_lower not in self.characters:
            available = ", ".join(self.characters.keys())
            raise ValueError(
                f"Character '{character_name}' not found. "
                f"Available characters: {available}"
            )

        self.current_character = self.characters[char_name_lower]
        logger.info(f"Current character set to: {self.current_character.name}")

        return self.current_character

    def get_character(self, character_name: Optional[str] = None) -> Character:
        """
        Get a character by name or return current character

        Args:
            character_name: Name of character, or None for current

        Returns:
            Character object
        """
        if character_name:
            return self.characters[character_name.lower()]

        if self.current_character is None:
            raise ValueError("No character currently loaded")

        return self.current_character

    def list_characters(self) -> List[str]:
        """
        List all available characters

        Returns:
            List of character names
        """
        return list(self.characters.keys())

    def set_language(self, language: str):
        """
        Set the current language

        Args:
            language: Language code (en, ru)
        """
        if self.current_character and language not in self.current_character.language_support:
            logger.warning(
                f"Language '{language}' not supported by {self.current_character.name}. "
                f"Supported: {self.current_character.language_support}"
            )

        self.current_language = language
        logger.debug(f"Language set to: {language}")

    def set_emotion(self, emotion: str):
        """
        Set the current emotional state

        Args:
            emotion: Emotion name (neutral, stern, helpful, etc.)
        """
        self.current_emotion = emotion
        logger.debug(f"Emotion set to: {emotion}")

    def get_system_prompt(self, language: Optional[str] = None) -> str:
        """
        Get the system prompt for the current character and language

        Args:
            language: Language code, or None for current language

        Returns:
            System prompt text
        """
        if not self.current_character:
            raise ValueError("No character loaded")

        lang = language or self.current_language
        prompt_attr = f"system_{lang}"

        system_prompt = getattr(self.current_character.prompts, prompt_attr, None)

        if not system_prompt:
            logger.warning(f"No system prompt for language '{lang}', using English")
            system_prompt = self.current_character.prompts.system_en

        # Add emotion suffix if available
        if self.current_emotion != "neutral":
            emotion_config = self.current_character.emotions.get(self.current_emotion, {})
            suffix = emotion_config.get("prompt_suffix", "")
            if suffix:
                system_prompt = f"{system_prompt}\n\n{suffix}"

        return system_prompt

    def get_template(
        self,
        template_type: str,
        language: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get a template response (greeting, confirmation, etc.)

        Args:
            template_type: Type of template (greeting, confirmation, refusal, etc.)
            language: Language code, or None for current language
            **kwargs: Format arguments for the template

        Returns:
            Template text (randomly selected if multiple options)
        """
        if not self.current_character:
            raise ValueError("No character loaded")

        lang = language or self.current_language
        template_attr = f"{template_type}_{lang}"

        templates = getattr(self.current_character.prompts, template_attr, None)

        if not templates:
            logger.warning(
                f"No template '{template_type}' for language '{lang}', trying English"
            )
            template_attr = f"{template_type}_en"
            templates = getattr(self.current_character.prompts, template_attr, None)

        if not templates:
            logger.error(f"Template '{template_type}' not found")
            return f"[{template_type}]"

        # If it's a list, randomly select one
        if isinstance(templates, list):
            template = random.choice(templates)
        else:
            template = templates

        # Format template with provided arguments
        if kwargs:
            try:
                template = template.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing template argument: {e}")

        return template

    def get_voice_settings(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get voice settings for TTS

        Args:
            language: Language code, or None for current language

        Returns:
            Voice settings dictionary
        """
        if not self.current_character:
            raise ValueError("No character loaded")

        if not self.current_character.voice_settings:
            return {}

        lang = language or self.current_language
        return self.current_character.voice_settings.get(lang, {})

    def get_response_rules(self) -> CharacterResponseRules:
        """
        Get response generation rules for current character

        Returns:
            Response rules
        """
        if not self.current_character:
            raise ValueError("No character loaded")

        # Apply emotion-based temperature override if available
        rules = self.current_character.response_rules.copy()

        if self.current_emotion != "neutral":
            emotion_config = self.current_character.emotions.get(self.current_emotion, {})
            if "temperature" in emotion_config:
                rules.temperature = emotion_config["temperature"]

        return rules

    def get_character_info(self) -> Dict[str, Any]:
        """
        Get information about the current character

        Returns:
            Character information dictionary
        """
        if not self.current_character:
            return {"error": "No character loaded"}

        return {
            "name": self.current_character.name,
            "version": self.current_character.version,
            "description": self.current_character.description,
            "archetype": self.current_character.personality.archetype,
            "traits": self.current_character.personality.traits,
            "languages": self.current_character.language_support,
            "current_language": self.current_language,
            "current_emotion": self.current_emotion,
        }


if __name__ == "__main__":
    # Test the character manager
    logging.basicConfig(level=logging.INFO)

    characters_dir = "/home/user/jarvis_manager/services/llm_service/characters"
    manager = CharacterManager(characters_dir)

    print("Available characters:", manager.list_characters())

    # Load Gerald
    manager.load_character("gerald")
    print("\nCharacter info:", manager.get_character_info())

    # Test prompts
    print("\nSystem prompt (EN):", manager.get_system_prompt("en")[:100], "...")
    print("\nGreeting (EN):", manager.get_template("greeting", "en"))
    print("Greeting (RU):", manager.get_template("greeting", "ru"))
    print("\nConfirmation (EN):", manager.get_template("confirmation", "en"))

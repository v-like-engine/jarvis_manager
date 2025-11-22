"""
Command Parser Module

Parses recognized text into structured commands for execution.
Supports multiple command types with fuzzy matching and parameter extraction.
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from loguru import logger


class CommandType(Enum):
    """Supported command types"""
    APP_LAUNCH = "app_launch"
    APP_CLOSE = "app_close"
    RECOGNIZE_ME = "recognize_me"
    CHAT = "chat"
    SYSTEM = "system"
    FILE_OP = "file_op"
    TERMINAL = "terminal"
    MUSIC_CONTROL = "music_control"
    UNKNOWN = "unknown"


class CommandParser:
    """
    Parses recognized speech text into structured commands.

    Supports English and Russian with fuzzy matching for trigger words.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize command parser.

        Args:
            config: Configuration dictionary with trigger words
        """
        self.config = config or self._get_default_config()

        # Precompile regex patterns for efficiency
        self._compile_patterns()

        logger.info("CommandParser initialized")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with trigger words"""
        return {
            "app_launch": {
                "en": ["open", "launch", "start", "run"],
                "ru": ["открой", "запусти", "открыть", "запустить", "включи"]
            },
            "app_close": {
                "en": ["close", "exit", "quit", "stop", "kill"],
                "ru": ["закрой", "закрыть", "выключи", "останови", "выйди"]
            },
            "recognize_me": {
                "en": ["recognize me", "who am i", "identify me", "who i am"],
                "ru": ["узнай меня", "кто я", "распознай меня", "определи меня"]
            },
            "system": {
                "en": ["shutdown", "restart", "reboot", "sleep", "lock", "logout"],
                "ru": ["выключи компьютер", "перезагрузи", "перезагрузка", "спать", "заблокируй", "выход"]
            },
            "file_op": {
                "en": ["create file", "delete file", "open file", "create folder", "delete folder"],
                "ru": ["создай файл", "удали файл", "открой файл", "создай папку", "удали папку"]
            },
            "terminal": {
                "en": ["execute", "run command", "terminal", "command line"],
                "ru": ["выполни команду", "терминал", "командная строка"]
            },
            "music_control": {
                "en": ["play", "pause", "stop music", "next", "previous", "volume"],
                "ru": ["играй", "пауза", "останови музыку", "следующая", "предыдущая", "громкость"]
            }
        }

    def _compile_patterns(self):
        """Compile regex patterns for command matching"""
        self.patterns = {}

        for cmd_type, triggers in self.config.items():
            self.patterns[cmd_type] = {}

            for lang, words in triggers.items():
                # Create pattern that matches trigger words at the start
                # Case-insensitive matching
                pattern = r"^(" + "|".join([re.escape(w) for w in words]) + r")\s+(.+)$"
                self.patterns[cmd_type][lang] = re.compile(pattern, re.IGNORECASE | re.UNICODE)

    def parse(
        self,
        text: str,
        language: str = "en",
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Parse recognized text into structured command.

        Args:
            text: Recognized text
            language: Language code ("en" or "ru")
            confidence: Recognition confidence

        Returns:
            Structured command dictionary
        """
        text = text.strip()

        if not text:
            return self._create_command(
                CommandType.UNKNOWN,
                language,
                text,
                {},
                confidence
            )

        # Try to match each command type
        for cmd_type_str, lang_patterns in self.patterns.items():
            if language not in lang_patterns:
                continue

            pattern = lang_patterns[language]
            match = pattern.match(text)

            if match:
                trigger_word = match.group(1)
                remaining_text = match.group(2).strip()

                cmd_type = CommandType(cmd_type_str)
                params = self._extract_params(cmd_type, remaining_text, language)

                return self._create_command(
                    cmd_type,
                    language,
                    text,
                    params,
                    confidence,
                    trigger_word=trigger_word
                )

        # Check for special cases (recognize me - exact phrase match)
        if self._is_recognize_me(text, language):
            return self._create_command(
                CommandType.RECOGNIZE_ME,
                language,
                text,
                {},
                confidence
            )

        # Check if it's a question or chat
        if self._is_chat(text, language):
            return self._create_command(
                CommandType.CHAT,
                language,
                text,
                {"query": text},
                confidence
            )

        # Default to unknown
        return self._create_command(
            CommandType.UNKNOWN,
            language,
            text,
            {},
            confidence
        )

    def _extract_params(
        self,
        cmd_type: CommandType,
        text: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Extract parameters from command text.

        Args:
            cmd_type: Command type
            text: Remaining text after trigger word
            language: Language code

        Returns:
            Dictionary of extracted parameters
        """
        params = {}

        if cmd_type == CommandType.APP_LAUNCH:
            params["app_name"] = text
            params["action"] = "launch"

        elif cmd_type == CommandType.APP_CLOSE:
            params["app_name"] = text
            params["action"] = "close"

        elif cmd_type == CommandType.SYSTEM:
            params["action"] = self._parse_system_action(text, language)

        elif cmd_type == CommandType.FILE_OP:
            file_params = self._parse_file_operation(text, language)
            params.update(file_params)

        elif cmd_type == CommandType.TERMINAL:
            params["command"] = text

        elif cmd_type == CommandType.MUSIC_CONTROL:
            music_params = self._parse_music_control(text, language)
            params.update(music_params)

        return params

    def _parse_system_action(self, text: str, language: str) -> str:
        """Parse system command action"""
        text_lower = text.lower()

        shutdown_words = ["shutdown", "выключи", "выключить"] if language == "ru" else ["shutdown"]
        restart_words = ["restart", "reboot", "перезагрузи", "перезагрузка"] if language == "ru" else ["restart", "reboot"]
        sleep_words = ["sleep", "спать"] if language == "ru" else ["sleep"]
        lock_words = ["lock", "заблокируй"] if language == "ru" else ["lock"]

        for word in shutdown_words:
            if word in text_lower:
                return "shutdown"

        for word in restart_words:
            if word in text_lower:
                return "restart"

        for word in sleep_words:
            if word in text_lower:
                return "sleep"

        for word in lock_words:
            if word in text_lower:
                return "lock"

        return "unknown"

    def _parse_file_operation(self, text: str, language: str) -> Dict[str, Any]:
        """Parse file operation parameters"""
        params = {}
        text_lower = text.lower()

        # Determine operation type
        if language == "ru":
            if "создай файл" in text_lower or "создать файл" in text_lower:
                params["operation"] = "create_file"
            elif "удали файл" in text_lower or "удалить файл" in text_lower:
                params["operation"] = "delete_file"
            elif "открой файл" in text_lower or "открыть файл" in text_lower:
                params["operation"] = "open_file"
            elif "создай папку" in text_lower or "создать папку" in text_lower:
                params["operation"] = "create_folder"
            elif "удали папку" in text_lower or "удалить папку" in text_lower:
                params["operation"] = "delete_folder"
        else:
            if "create file" in text_lower:
                params["operation"] = "create_file"
            elif "delete file" in text_lower:
                params["operation"] = "delete_file"
            elif "open file" in text_lower:
                params["operation"] = "open_file"
            elif "create folder" in text_lower:
                params["operation"] = "create_folder"
            elif "delete folder" in text_lower:
                params["operation"] = "delete_folder"

        # Extract file/folder name (simplified - would need more sophisticated parsing)
        params["target"] = text

        return params

    def _parse_music_control(self, text: str, language: str) -> Dict[str, Any]:
        """Parse music control parameters"""
        params = {}
        text_lower = text.lower()

        if language == "ru":
            if "играй" in text_lower or "воспроизведи" in text_lower:
                params["action"] = "play"
            elif "пауза" in text_lower:
                params["action"] = "pause"
            elif "останови" in text_lower:
                params["action"] = "stop"
            elif "следующая" in text_lower or "следующий" in text_lower:
                params["action"] = "next"
            elif "предыдущая" in text_lower or "предыдущий" in text_lower:
                params["action"] = "previous"
            elif "громкость" in text_lower:
                params["action"] = "volume"
                # Try to extract volume level
                volume_match = re.search(r"(\d+)", text)
                if volume_match:
                    params["level"] = int(volume_match.group(1))
        else:
            if "play" in text_lower:
                params["action"] = "play"
            elif "pause" in text_lower:
                params["action"] = "pause"
            elif "stop" in text_lower:
                params["action"] = "stop"
            elif "next" in text_lower:
                params["action"] = "next"
            elif "previous" in text_lower or "prev" in text_lower:
                params["action"] = "previous"
            elif "volume" in text_lower:
                params["action"] = "volume"
                volume_match = re.search(r"(\d+)", text)
                if volume_match:
                    params["level"] = int(volume_match.group(1))

        return params

    def _is_recognize_me(self, text: str, language: str) -> bool:
        """Check if text is a 'recognize me' command"""
        text_lower = text.lower()

        if language == "ru":
            recognize_phrases = [
                "узнай меня", "кто я", "распознай меня",
                "определи меня", "опознай меня"
            ]
        else:
            recognize_phrases = [
                "recognize me", "who am i", "identify me",
                "who i am", "who am i", "identify myself"
            ]

        for phrase in recognize_phrases:
            if phrase in text_lower:
                return True

        return False

    def _is_chat(self, text: str, language: str) -> bool:
        """Check if text is a chat/question"""
        # Questions usually contain question words or end with ?
        text_lower = text.lower()

        if language == "ru":
            question_words = [
                "кто", "что", "где", "когда", "почему",
                "как", "какой", "сколько", "зачем"
            ]
        else:
            question_words = [
                "who", "what", "where", "when", "why",
                "how", "which", "can", "could", "would",
                "should", "is", "are", "do", "does"
            ]

        # Check for question mark
        if "?" in text:
            return True

        # Check for question words at the start
        for word in question_words:
            if text_lower.startswith(word + " "):
                return True

        return False

    def _create_command(
        self,
        cmd_type: CommandType,
        language: str,
        raw_text: str,
        params: Dict[str, Any],
        confidence: float,
        trigger_word: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create structured command message.

        Args:
            cmd_type: Command type
            language: Language code
            raw_text: Original recognized text
            params: Extracted parameters
            confidence: Recognition confidence
            trigger_word: Matched trigger word

        Returns:
            Structured command dictionary
        """
        command_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        return {
            "command_id": command_id,
            "timestamp": timestamp,
            "language": language,
            "raw_text": raw_text,
            "command_type": cmd_type.value,
            "parsed_params": params,
            "confidence": confidence,
            "trigger_word": trigger_word
        }

    def validate_command(self, command: Dict[str, Any]) -> bool:
        """
        Validate command structure.

        Args:
            command: Command dictionary

        Returns:
            True if valid
        """
        required_fields = [
            "command_id",
            "timestamp",
            "language",
            "raw_text",
            "command_type",
            "parsed_params",
            "confidence"
        ]

        for field in required_fields:
            if field not in command:
                logger.warning(f"Missing required field: {field}")
                return False

        return True


def test_command_parser():
    """Test command parser"""
    logger.info("Testing Command Parser...")

    parser = CommandParser()

    # Test cases
    test_cases = [
        ("Open Yandex Browser", "en"),
        ("Закрой Яндекс браузер", "ru"),
        ("Recognize me", "en"),
        ("Кто я", "ru"),
        ("Who are you?", "en"),
        ("Кто ты?", "ru"),
        ("Launch Chrome", "en"),
        ("Запусти Firefox", "ru"),
    ]

    for text, lang in test_cases:
        logger.info(f"\nInput: '{text}' ({lang})")
        command = parser.parse(text, lang, confidence=0.95)
        logger.info(f"Command type: {command['command_type']}")
        logger.info(f"Params: {command['parsed_params']}")
        logger.info(f"Valid: {parser.validate_command(command)}")

    logger.info("\nTest completed!")


if __name__ == "__main__":
    test_command_parser()

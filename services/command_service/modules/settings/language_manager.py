"""Manage language settings for Gerald."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class LanguageManager:
    """
    Manage language settings for Gerald.

    Note: This manages Gerald's response language, not the OS language.

    Features:
    - Set current language
    - Get available languages
    - Persist language preference
    """

    SUPPORTED_LANGUAGES = ['en', 'ru']
    DEFAULT_LANGUAGE = 'en'

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize language manager.

        Args:
            config_file: Path to language config file
        """
        if config_file is None:
            config_file = Path(__file__).parent.parent.parent / "cache" / "language.json"

        self.config_file = config_file
        self.current_language = self._load_language()

        logger.info(f"Language manager initialized (current: {self.current_language})")

    def _load_language(self) -> str:
        """
        Load language from config file.

        Returns:
            Language code
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang = data.get('language', self.DEFAULT_LANGUAGE)
                    if lang in self.SUPPORTED_LANGUAGES:
                        return lang

        except Exception as e:
            logger.error(f"Failed to load language config: {e}")

        return self.DEFAULT_LANGUAGE

    def _save_language(self, language: str) -> bool:
        """
        Save language to config file.

        Args:
            language: Language code

        Returns:
            True if saved successfully
        """
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'language': language}, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Failed to save language config: {e}")
            return False

    def set_language(self, language: str) -> Dict[str, Any]:
        """
        Set current language.

        Args:
            language: Language code ('en' or 'ru')

        Returns:
            Result dictionary
        """
        if language not in self.SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f'Unsupported language: {language}. Supported: {", ".join(self.SUPPORTED_LANGUAGES)}'
            }

        self.current_language = language

        if self._save_language(language):
            logger.info(f"Language set to: {language}")
            return {
                'success': True,
                'language': language,
                'message': f'Language set to: {language}'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save language preference'
            }

    def get_language(self) -> str:
        """
        Get current language.

        Returns:
            Language code
        """
        return self.current_language

    def get_language_info(self) -> Dict[str, Any]:
        """
        Get language information.

        Returns:
            Language info dictionary
        """
        language_names = {
            'en': 'English',
            'ru': 'Russian (Русский)'
        }

        return {
            'success': True,
            'current_language': self.current_language,
            'current_language_name': language_names.get(self.current_language, 'Unknown'),
            'supported_languages': [
                {
                    'code': code,
                    'name': language_names.get(code, code)
                }
                for code in self.SUPPORTED_LANGUAGES
            ]
        }

    def switch_language(self) -> Dict[str, Any]:
        """
        Toggle between supported languages.

        Returns:
            Result dictionary
        """
        # Find next language
        current_index = self.SUPPORTED_LANGUAGES.index(self.current_language)
        next_index = (current_index + 1) % len(self.SUPPORTED_LANGUAGES)
        next_language = self.SUPPORTED_LANGUAGES[next_index]

        return self.set_language(next_language)

    @staticmethod
    def get_supported_languages() -> List[str]:
        """
        Get list of supported languages.

        Returns:
            List of language codes
        """
        return LanguageManager.SUPPORTED_LANGUAGES.copy()

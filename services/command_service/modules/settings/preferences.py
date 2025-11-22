"""User preferences management."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PreferencesManager:
    """
    Manage user preferences.

    Features:
    - Store and retrieve user preferences
    - Persist to disk
    - Default values
    """

    DEFAULT_PREFERENCES = {
        'language': 'en',
        'voice_enabled': True,
        'auto_confirm_safe_commands': True,
        'music_player': 'yandex_music',
        'volume_step': 5,
        'terminal_shell': 'cmd',
        'show_notifications': True,
    }

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize preferences manager.

        Args:
            config_file: Path to preferences config file
        """
        if config_file is None:
            config_file = Path(__file__).parent.parent.parent / "cache" / "preferences.json"

        self.config_file = config_file
        self.preferences = self._load_preferences()

        logger.info("Preferences manager initialized")

    def _load_preferences(self) -> Dict[str, Any]:
        """
        Load preferences from file.

        Returns:
            Preferences dictionary
        """
        # Start with defaults
        prefs = self.DEFAULT_PREFERENCES.copy()

        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_prefs = json.load(f)
                    # Merge with defaults
                    prefs.update(user_prefs)

        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")

        return prefs

    def _save_preferences(self) -> bool:
        """
        Save preferences to file.

        Returns:
            True if saved successfully
        """
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value.

        Args:
            key: Preference key
            default: Default value if key not found

        Returns:
            Preference value
        """
        return self.preferences.get(key, default)

    def set(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Set a preference value.

        Args:
            key: Preference key
            value: Preference value

        Returns:
            Result dictionary
        """
        self.preferences[key] = value

        if self._save_preferences():
            logger.info(f"Preference set: {key} = {value}")
            return {
                'success': True,
                'key': key,
                'value': value,
                'message': f'Preference updated: {key}'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save preferences'
            }

    def get_all(self) -> Dict[str, Any]:
        """
        Get all preferences.

        Returns:
            Preferences dictionary
        """
        return self.preferences.copy()

    def reset(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Reset preferences to defaults.

        Args:
            key: Specific key to reset (or None for all)

        Returns:
            Result dictionary
        """
        if key:
            # Reset specific key
            if key in self.DEFAULT_PREFERENCES:
                self.preferences[key] = self.DEFAULT_PREFERENCES[key]
                if self._save_preferences():
                    return {
                        'success': True,
                        'message': f'Reset preference: {key}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Unknown preference key: {key}'
                }
        else:
            # Reset all
            self.preferences = self.DEFAULT_PREFERENCES.copy()
            if self._save_preferences():
                return {
                    'success': True,
                    'message': 'All preferences reset to defaults'
                }

        return {
            'success': False,
            'error': 'Failed to save preferences'
        }

    def export_preferences(self, file_path: str) -> Dict[str, Any]:
        """
        Export preferences to a file.

        Args:
            file_path: Path to export file

        Returns:
            Result dictionary
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)

            return {
                'success': True,
                'path': str(path),
                'message': f'Preferences exported to {path}'
            }

        except Exception as e:
            logger.error(f"Failed to export preferences: {e}")
            return {
                'success': False,
                'error': f'Failed to export preferences: {str(e)}'
            }

    def import_preferences(self, file_path: str) -> Dict[str, Any]:
        """
        Import preferences from a file.

        Args:
            file_path: Path to import file

        Returns:
            Result dictionary
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }

            with open(path, 'r', encoding='utf-8') as f:
                imported_prefs = json.load(f)

            # Merge with current preferences
            self.preferences.update(imported_prefs)

            if self._save_preferences():
                return {
                    'success': True,
                    'message': f'Preferences imported from {path}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save imported preferences'
                }

        except Exception as e:
            logger.error(f"Failed to import preferences: {e}")
            return {
                'success': False,
                'error': f'Failed to import preferences: {str(e)}'
            }

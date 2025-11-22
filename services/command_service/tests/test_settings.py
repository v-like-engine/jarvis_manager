"""Tests for settings module."""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.command_service.modules.settings import (
    LanguageManager, PreferencesManager
)


class TestLanguageManager:
    """Test language manager."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create language manager with temp config."""
        config_file = tmp_path / "language.json"
        return LanguageManager(config_file=config_file)

    def test_default_language(self, manager):
        """Test default language."""
        assert manager.get_language() == 'en'

    def test_set_language(self, manager):
        """Test setting language."""
        result = manager.set_language('ru')
        assert result['success']
        assert manager.get_language() == 'ru'

    def test_invalid_language(self, manager):
        """Test setting invalid language."""
        result = manager.set_language('invalid')
        assert not result['success']
        assert 'Unsupported' in result['error']

    def test_switch_language(self, manager):
        """Test switching language."""
        assert manager.get_language() == 'en'

        result = manager.switch_language()
        assert result['success']
        assert manager.get_language() == 'ru'

        result = manager.switch_language()
        assert result['success']
        assert manager.get_language() == 'en'


class TestPreferencesManager:
    """Test preferences manager."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create preferences manager with temp config."""
        config_file = tmp_path / "preferences.json"
        return PreferencesManager(config_file=config_file)

    def test_default_preferences(self, manager):
        """Test default preferences."""
        prefs = manager.get_all()
        assert prefs['language'] == 'en'
        assert prefs['voice_enabled'] is True

    def test_set_preference(self, manager):
        """Test setting a preference."""
        result = manager.set('test_key', 'test_value')
        assert result['success']
        assert manager.get('test_key') == 'test_value'

    def test_reset_preference(self, manager):
        """Test resetting a preference."""
        manager.set('language', 'ru')
        result = manager.reset('language')
        assert result['success']
        assert manager.get('language') == 'en'  # Back to default

    def test_export_import(self, manager, tmp_path):
        """Test exporting and importing preferences."""
        # Set some preferences
        manager.set('test_key', 'test_value')

        # Export
        export_file = tmp_path / "export.json"
        result = manager.export_preferences(str(export_file))
        assert result['success']
        assert export_file.exists()

        # Create new manager and import
        manager2 = PreferencesManager(config_file=tmp_path / "prefs2.json")
        result = manager2.import_preferences(str(export_file))
        assert result['success']
        assert manager2.get('test_key') == 'test_value'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

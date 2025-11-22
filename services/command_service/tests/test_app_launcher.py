"""Tests for app launcher module."""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.command_service.modules.app_launcher import (
    AppFinder, AppDatabase, AppLauncher, AppCloser
)


class TestAppDatabase:
    """Test app database functionality."""

    @pytest.fixture
    def db(self, tmp_path):
        """Create app database with temp cache file."""
        cache_file = tmp_path / "apps.json"
        return AppDatabase(cache_file=cache_file, fuzzy_threshold=70)

    def test_find_exact_match(self, db):
        """Test exact app name matching."""
        # Add some test apps
        test_apps = [
            {'name': 'Google Chrome', 'exe_path': 'C:\\chrome.exe', 'location': 'test'},
            {'name': 'Notepad', 'exe_path': 'C:\\notepad.exe', 'location': 'test'},
        ]
        db.update_apps(test_apps)

        # Find exact match
        result = db.find_exact_match('Google Chrome')
        assert result is not None
        assert result['name'] == 'Google Chrome'

        # Case insensitive
        result = db.find_exact_match('notepad')
        assert result is not None
        assert result['name'] == 'Notepad'

    def test_find_fuzzy_match(self, db):
        """Test fuzzy app name matching."""
        test_apps = [
            {'name': 'Yandex Browser', 'exe_path': 'C:\\yandex.exe', 'location': 'test'},
            {'name': 'Google Chrome', 'exe_path': 'C:\\chrome.exe', 'location': 'test'},
        ]
        db.update_apps(test_apps)

        # Fuzzy match
        matches = db.find_fuzzy_match('yandex bro', limit=1)
        assert len(matches) > 0
        app, score = matches[0]
        assert 'Yandex' in app['name']
        assert score >= 70  # Above threshold

    def test_cache_save_load(self, db, tmp_path):
        """Test saving and loading cache."""
        test_apps = [
            {'name': 'Test App', 'exe_path': 'C:\\test.exe', 'location': 'test'},
        ]
        db.update_apps(test_apps)

        # Save
        assert db.save_cache()

        # Create new database instance and load
        db2 = AppDatabase(cache_file=db.cache_file)
        assert db2.load_cache()
        assert len(db2.apps) == 1
        assert db2.apps[0]['name'] == 'Test App'

    def test_search(self, db):
        """Test app search."""
        test_apps = [
            {'name': 'Visual Studio Code', 'exe_path': 'C:\\vscode.exe', 'location': 'test'},
            {'name': 'Visual Studio', 'exe_path': 'C:\\vs.exe', 'location': 'test'},
            {'name': 'Notepad', 'exe_path': 'C:\\notepad.exe', 'location': 'test'},
        ]
        db.update_apps(test_apps)

        # Search for 'visual'
        results = db.search('visual', limit=10)
        assert len(results) >= 2
        assert all('Visual' in app['name'] for app in results)


class TestAppLauncher:
    """Test app launcher functionality."""

    def test_launch_nonexistent_app(self):
        """Test launching nonexistent app."""
        launcher = AppLauncher()
        result = launcher.launch('C:\\nonexistent.exe')
        assert not result['success']
        assert 'not found' in result['error'].lower()


class TestAppCloser:
    """Test app closer functionality."""

    def test_close_nonexistent_app(self):
        """Test closing nonexistent app."""
        closer = AppCloser()
        result = closer.close_by_name('NonexistentApp12345')
        assert not result['success']
        assert 'not found' in result['error'].lower() or 'no running' in result['error'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

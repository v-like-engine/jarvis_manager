"""Tests for file manager."""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.command_service.modules.file_ops import (
    FileManager, DirectoryManager, FileBrowser, PathResolver
)


class TestPathResolver:
    """Test path resolver."""

    def test_resolve_absolute_path(self):
        """Test resolving absolute path."""
        if sys.platform == 'win32':
            path = PathResolver.resolve('C:\\test\\file.txt')
            assert path.is_absolute()
        else:
            path = PathResolver.resolve('/test/file.txt')
            assert path.is_absolute()

    def test_is_valid(self):
        """Test path validation."""
        assert PathResolver.is_valid('test.txt')
        assert PathResolver.is_valid('C:\\test\\file.txt' if sys.platform == 'win32' else '/test/file.txt')

    def test_is_protected(self):
        """Test protected path detection."""
        if sys.platform == 'win32':
            assert PathResolver.is_protected('C:\\Windows\\System32\\test.dll')
            assert PathResolver.is_protected('C:\\Program Files\\test.exe')
            assert not PathResolver.is_protected('C:\\Users\\test\\file.txt')


class TestFileManager:
    """Test file manager."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create file manager with safety checks enabled."""
        return FileManager(enable_safety_checks=True)

    def test_create_file(self, manager, tmp_path):
        """Test file creation."""
        file_path = tmp_path / "test.txt"
        result = manager.create_file(str(file_path), content="Hello World")

        assert result['success']
        assert file_path.exists()
        assert file_path.read_text() == "Hello World"

    def test_create_file_already_exists(self, manager, tmp_path):
        """Test creating file that already exists."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Original")

        result = manager.create_file(str(file_path), content="New")
        assert not result['success']
        assert 'already exists' in result['error'].lower()

    def test_delete_file(self, manager, tmp_path):
        """Test file deletion."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Test")

        result = manager.delete_file(str(file_path))
        assert result['success']
        assert not file_path.exists()

    def test_read_file(self, manager, tmp_path):
        """Test file reading."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Test Content")

        result = manager.read_file(str(file_path))
        assert result['success']
        assert result['content'] == "Test Content"


class TestDirectoryManager:
    """Test directory manager."""

    @pytest.fixture
    def manager(self):
        """Create directory manager."""
        return DirectoryManager(enable_safety_checks=True)

    def test_create_directory(self, manager, tmp_path):
        """Test directory creation."""
        dir_path = tmp_path / "testdir"
        result = manager.create_directory(str(dir_path))

        assert result['success']
        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_delete_directory(self, manager, tmp_path):
        """Test directory deletion."""
        dir_path = tmp_path / "testdir"
        dir_path.mkdir()

        result = manager.delete_directory(str(dir_path))
        assert result['success']
        assert not dir_path.exists()


class TestFileBrowser:
    """Test file browser."""

    def test_list_directory(self, tmp_path):
        """Test directory listing."""
        # Create some test files
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.txt").write_text("test")
        (tmp_path / "subdir").mkdir()

        result = FileBrowser.list_directory(str(tmp_path))

        assert result['success']
        assert result['count'] == 3
        assert len(result['items']) == 3

    def test_get_file_info(self, tmp_path):
        """Test getting file info."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Test Content")

        result = FileBrowser.get_file_info(str(file_path))

        assert result['success']
        assert result['name'] == 'test.txt'
        assert result['is_file']
        assert not result['is_directory']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

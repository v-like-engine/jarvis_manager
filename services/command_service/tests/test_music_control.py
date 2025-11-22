"""Tests for music control module."""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.command_service.modules.music_control import MusicController


class TestMusicController:
    """Test music controller."""

    @pytest.fixture
    def controller(self):
        """Create music controller."""
        return MusicController(preferred_player='generic')

    def test_controller_initialization(self, controller):
        """Test controller initializes correctly."""
        assert controller.preferred_player == 'generic'
        assert controller.interface is not None

    # Note: Actual media key tests would require Windows and can't run in CI
    # These are basic structural tests


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

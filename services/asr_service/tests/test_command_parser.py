"""
Unit tests for Command Parser
"""

import pytest
from services.asr_service.src.command_parser import CommandParser, CommandType


class TestCommandParser:
    """Test cases for CommandParser"""

    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return CommandParser()

    def test_app_launch_en(self, parser):
        """Test app launch command in English"""
        result = parser.parse("Open Yandex Browser", language="en", confidence=0.95)

        assert result['command_type'] == CommandType.APP_LAUNCH.value
        assert result['language'] == 'en'
        assert result['parsed_params']['app_name'] == 'Yandex Browser'
        assert result['confidence'] == 0.95
        assert parser.validate_command(result)

    def test_app_launch_ru(self, parser):
        """Test app launch command in Russian"""
        result = parser.parse("Открой Яндекс браузер", language="ru", confidence=0.90)

        assert result['command_type'] == CommandType.APP_LAUNCH.value
        assert result['language'] == 'ru'
        assert result['parsed_params']['app_name'] == 'Яндекс браузер'

    def test_app_close_en(self, parser):
        """Test app close command in English"""
        result = parser.parse("Close Chrome", language="en", confidence=0.92)

        assert result['command_type'] == CommandType.APP_CLOSE.value
        assert result['parsed_params']['app_name'] == 'Chrome'

    def test_app_close_ru(self, parser):
        """Test app close command in Russian"""
        result = parser.parse("Закрой Firefox", language="ru", confidence=0.88)

        assert result['command_type'] == CommandType.APP_CLOSE.value
        assert result['parsed_params']['app_name'] == 'Firefox'

    def test_recognize_me_en(self, parser):
        """Test recognize me command in English"""
        result = parser.parse("Recognize me", language="en", confidence=0.95)

        assert result['command_type'] == CommandType.RECOGNIZE_ME.value

    def test_recognize_me_ru(self, parser):
        """Test recognize me command in Russian"""
        result = parser.parse("Кто я", language="ru", confidence=0.93)

        assert result['command_type'] == CommandType.RECOGNIZE_ME.value

    def test_chat_question_en(self, parser):
        """Test chat/question in English"""
        result = parser.parse("Who are you?", language="en", confidence=0.90)

        assert result['command_type'] == CommandType.CHAT.value
        assert 'query' in result['parsed_params']

    def test_chat_question_ru(self, parser):
        """Test chat/question in Russian"""
        result = parser.parse("Кто ты?", language="ru", confidence=0.91)

        assert result['command_type'] == CommandType.CHAT.value

    def test_unknown_command(self, parser):
        """Test unknown command"""
        result = parser.parse("Random gibberish xyz", language="en", confidence=0.50)

        assert result['command_type'] == CommandType.UNKNOWN.value

    def test_empty_text(self, parser):
        """Test empty text"""
        result = parser.parse("", language="en", confidence=0.0)

        assert result['command_type'] == CommandType.UNKNOWN.value

    def test_command_validation(self, parser):
        """Test command validation"""
        result = parser.parse("Open Notepad", language="en", confidence=0.95)

        assert parser.validate_command(result) is True

        # Invalid command (missing fields)
        invalid_command = {
            "command_id": "123",
            "raw_text": "test"
        }

        assert parser.validate_command(invalid_command) is False

    def test_launch_vs_close(self, parser):
        """Test distinguishing between launch and close"""
        launch = parser.parse("Launch Chrome", language="en", confidence=0.95)
        close = parser.parse("Close Chrome", language="en", confidence=0.95)

        assert launch['command_type'] == CommandType.APP_LAUNCH.value
        assert close['command_type'] == CommandType.APP_CLOSE.value

        assert launch['parsed_params']['action'] == 'launch'
        assert close['parsed_params']['action'] == 'close'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Command validation and sanitization."""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class CommandRequest(BaseModel):
    """Command execution request model."""

    command_id: str = Field(..., description="Unique command ID")
    command_type: str = Field(..., description="Type of command")
    language: str = Field(default="en", description="Response language")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    confirmed: bool = Field(default=False, description="User confirmed dangerous operation")

    @validator('command_type')
    def validate_command_type(cls, v):
        """Validate command type."""
        valid_types = [
            'app_launch', 'app_close',
            'terminal', 'terminal_command',
            'file_create', 'file_delete', 'file_read', 'file_copy', 'file_move',
            'dir_create', 'dir_delete', 'dir_list', 'dir_navigate',
            'music_play', 'music_pause', 'music_next', 'music_previous', 'music_stop',
            'volume_up', 'volume_down', 'volume_set', 'volume_mute',
            'language_switch', 'language_set',
            'startup_enable', 'startup_disable',
            'settings_get', 'settings_set',
        ]

        if v not in valid_types:
            logger.warning(f"Unknown command type: {v}")
            # Don't raise error, just log warning

        return v

    @validator('language')
    def validate_language(cls, v):
        """Validate language code."""
        if v not in ['en', 'ru']:
            return 'en'  # Default to English
        return v


class CommandResponse(BaseModel):
    """Command execution response model."""

    success: bool
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CommandValidator:
    """
    Validate and sanitize commands before execution.

    Features:
    - Validate command structure
    - Sanitize parameters
    - Check required parameters
    """

    @staticmethod
    def validate_request(data: Dict[str, Any]) -> CommandRequest:
        """
        Validate command request.

        Args:
            data: Request data

        Returns:
            Validated CommandRequest

        Raises:
            ValueError: If validation fails
        """
        try:
            return CommandRequest(**data)
        except Exception as e:
            logger.error(f"Command validation failed: {e}")
            raise ValueError(f"Invalid command request: {str(e)}")

    @staticmethod
    def validate_app_launch_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate app launch parameters.

        Args:
            params: Command parameters

        Returns:
            Validated parameters

        Raises:
            ValueError: If validation fails
        """
        app_name = params.get('app_name')
        if not app_name:
            raise ValueError("Missing required parameter: app_name")

        return {
            'app_name': str(app_name),
            'args': params.get('args', []),
        }

    @staticmethod
    def validate_terminal_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate terminal command parameters.

        Args:
            params: Command parameters

        Returns:
            Validated parameters

        Raises:
            ValueError: If validation fails
        """
        command = params.get('terminal_command') or params.get('command')
        if not command:
            raise ValueError("Missing required parameter: terminal_command or command")

        return {
            'terminal_command': str(command),
            'shell': params.get('shell', 'cmd'),
            'timeout': params.get('timeout', 30),
        }

    @staticmethod
    def validate_file_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate file operation parameters.

        Args:
            params: Command parameters

        Returns:
            Validated parameters

        Raises:
            ValueError: If validation fails
        """
        file_path = params.get('file_path') or params.get('path')
        if not file_path:
            raise ValueError("Missing required parameter: file_path or path")

        return {
            'file_path': str(file_path),
            'content': params.get('content', ''),
            'overwrite': params.get('overwrite', False),
        }

    @staticmethod
    def validate_dir_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate directory operation parameters.

        Args:
            params: Command parameters

        Returns:
            Validated parameters

        Raises:
            ValueError: If validation fails
        """
        dir_path = params.get('dir_path') or params.get('path')
        if not dir_path:
            raise ValueError("Missing required parameter: dir_path or path")

        return {
            'dir_path': str(dir_path),
            'recursive': params.get('recursive', False),
        }

    @staticmethod
    def validate_music_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate music control parameters.

        Args:
            params: Command parameters

        Returns:
            Validated parameters
        """
        return {
            'action': params.get('action', 'play'),
            'step': params.get('step', 5),
            'level': params.get('level', 50),
        }

    @staticmethod
    def sanitize_path(path: str) -> str:
        """
        Sanitize file path.

        Args:
            path: File path

        Returns:
            Sanitized path
        """
        # Remove dangerous characters
        dangerous_chars = ['..', '~', '$', '`', '|', '&', ';']
        sanitized = path

        for char in dangerous_chars:
            if char in sanitized:
                logger.warning(f"Removed dangerous character '{char}' from path")
                sanitized = sanitized.replace(char, '')

        return sanitized

    @staticmethod
    def validate_and_sanitize(
        command_type: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and sanitize command parameters based on type.

        Args:
            command_type: Command type
            params: Parameters to validate

        Returns:
            Validated and sanitized parameters

        Raises:
            ValueError: If validation fails
        """
        if command_type in ['app_launch', 'app_close']:
            return CommandValidator.validate_app_launch_params(params)

        elif command_type in ['terminal', 'terminal_command']:
            return CommandValidator.validate_terminal_params(params)

        elif command_type in ['file_create', 'file_delete', 'file_read', 'file_copy', 'file_move']:
            validated = CommandValidator.validate_file_params(params)
            # Sanitize path
            validated['file_path'] = CommandValidator.sanitize_path(validated['file_path'])
            return validated

        elif command_type in ['dir_create', 'dir_delete', 'dir_list', 'dir_navigate']:
            validated = CommandValidator.validate_dir_params(params)
            # Sanitize path
            validated['dir_path'] = CommandValidator.sanitize_path(validated['dir_path'])
            return validated

        elif command_type.startswith('music_') or command_type.startswith('volume_'):
            return CommandValidator.validate_music_params(params)

        else:
            # For other types, just return params as-is
            return params

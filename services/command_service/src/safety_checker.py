"""Safety checker for command execution."""

import re
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety levels for commands."""
    SAFE = 1              # Execute immediately
    NEEDS_CONFIRMATION = 2 # Ask user first
    FORBIDDEN = 3         # Never execute


class SafetyChecker:
    """
    Check command safety before execution.

    This class implements a three-level safety system:
    1. SAFE: Execute immediately
    2. NEEDS_CONFIRMATION: Ask user first
    3. FORBIDDEN: Never execute
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize safety checker.

        Args:
            config_path: Path to safety_rules.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "safety_rules.yaml"

        self.config_path = config_path
        self.rules = self._load_rules()
        logger.info(f"Safety checker initialized with rules from {config_path}")

    def _load_rules(self) -> Dict[str, Any]:
        """Load safety rules from YAML config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load safety rules: {e}")
            # Return default minimal rules
            return {
                'safe_commands': ['app_launch', 'app_close', 'dir_list'],
                'confirmation_required': ['file_delete', 'terminal_command'],
                'forbidden_patterns': ['format *', 'del /s /q C:\\'],
                'protected_paths': ['C:\\Windows', 'C:\\Program Files'],
                'protected_processes': ['csrss.exe', 'explorer.exe'],
                'whitelisted_terminal_commands': ['dir', 'ls', 'cd', 'echo'],
                'dangerous_keywords': ['format', 'deltree']
            }

    def check_command_safety(
        self,
        command_type: str,
        params: Dict[str, Any]
    ) -> Tuple[SafetyLevel, str]:
        """
        Check if a command is safe to execute.

        Args:
            command_type: Type of command (e.g., 'app_launch', 'file_delete')
            params: Command parameters

        Returns:
            Tuple of (SafetyLevel, reason/message)
        """
        # Check if command type is in safe list
        if command_type in self.rules.get('safe_commands', []):
            # Additional checks for specific command types
            if command_type == 'app_close':
                return self._check_app_close_safety(params)
            return (SafetyLevel.SAFE, "Command is safe")

        # Check if command needs confirmation
        if command_type in self.rules.get('confirmation_required', []):
            return self._check_confirmation_required(command_type, params)

        # Check specific command types
        if command_type == 'terminal':
            return self._check_terminal_command_safety(params)
        elif command_type == 'file_delete':
            return self._check_file_delete_safety(params)
        elif command_type == 'dir_delete':
            return self._check_dir_delete_safety(params)
        elif command_type == 'process_kill':
            return self._check_process_kill_safety(params)
        elif command_type == 'registry_modify':
            return self._check_registry_safety(params)

        # Unknown command - require confirmation by default
        return (
            SafetyLevel.NEEDS_CONFIRMATION,
            f"Unknown command type '{command_type}' requires confirmation"
        )

    def _check_app_close_safety(self, params: Dict[str, Any]) -> Tuple[SafetyLevel, str]:
        """Check if closing an app is safe."""
        app_name = params.get('app_name', '')
        process_name = params.get('process_name', app_name)

        # Check if it's a protected process
        protected = self.rules.get('protected_processes', [])
        for protected_proc in protected:
            if protected_proc.lower() in process_name.lower():
                return (
                    SafetyLevel.FORBIDDEN,
                    f"Cannot close protected system process: {process_name}"
                )

        return (SafetyLevel.SAFE, "App can be safely closed")

    def _check_terminal_command_safety(
        self,
        params: Dict[str, Any]
    ) -> Tuple[SafetyLevel, str]:
        """Check if a terminal command is safe."""
        command = params.get('terminal_command', '').strip()
        if not command:
            return (SafetyLevel.FORBIDDEN, "Empty command")

        # Check forbidden patterns
        for pattern in self.rules.get('forbidden_patterns', []):
            if re.search(pattern, command, re.IGNORECASE):
                return (
                    SafetyLevel.FORBIDDEN,
                    f"Command matches forbidden pattern: {pattern}"
                )

        # Check dangerous keywords
        for keyword in self.rules.get('dangerous_keywords', []):
            if keyword.lower() in command.lower():
                return (
                    SafetyLevel.FORBIDDEN,
                    f"Command contains dangerous keyword: {keyword}"
                )

        # Check if it's a whitelisted command
        command_name = command.split()[0].lower()
        whitelisted = self.rules.get('whitelisted_terminal_commands', [])
        if command_name in [cmd.lower() for cmd in whitelisted]:
            return (SafetyLevel.SAFE, "Command is whitelisted")

        # Require confirmation for non-whitelisted commands
        return (
            SafetyLevel.NEEDS_CONFIRMATION,
            f"Terminal command '{command}' requires confirmation"
        )

    def _check_file_delete_safety(
        self,
        params: Dict[str, Any]
    ) -> Tuple[SafetyLevel, str]:
        """Check if deleting a file is safe."""
        file_path = params.get('file_path', '')
        if not file_path:
            return (SafetyLevel.FORBIDDEN, "No file path specified")

        path = Path(file_path)

        # Check if it's in a protected path
        for protected_path in self.rules.get('protected_paths', []):
            protected = Path(protected_path)
            try:
                if path.is_relative_to(protected):
                    return (
                        SafetyLevel.FORBIDDEN,
                        f"Cannot delete file in protected directory: {protected_path}"
                    )
            except (ValueError, AttributeError):
                # is_relative_to not available in Python < 3.9
                if str(path).startswith(str(protected)):
                    return (
                        SafetyLevel.FORBIDDEN,
                        f"Cannot delete file in protected directory: {protected_path}"
                    )

        # Require confirmation for all file deletions
        return (
            SafetyLevel.NEEDS_CONFIRMATION,
            f"Confirm deletion of: {file_path}"
        )

    def _check_dir_delete_safety(
        self,
        params: Dict[str, Any]
    ) -> Tuple[SafetyLevel, str]:
        """Check if deleting a directory is safe."""
        dir_path = params.get('dir_path', '')
        if not dir_path:
            return (SafetyLevel.FORBIDDEN, "No directory path specified")

        path = Path(dir_path)

        # Check if it's a protected path or subdirectory
        for protected_path in self.rules.get('protected_paths', []):
            protected = Path(protected_path)
            try:
                # Check if we're trying to delete a protected directory
                if path.is_relative_to(protected) or protected.is_relative_to(path):
                    return (
                        SafetyLevel.FORBIDDEN,
                        f"Cannot delete protected directory: {protected_path}"
                    )
            except (ValueError, AttributeError):
                if (str(path).startswith(str(protected)) or
                    str(protected).startswith(str(path))):
                    return (
                        SafetyLevel.FORBIDDEN,
                        f"Cannot delete protected directory: {protected_path}"
                    )

        # Require confirmation for all directory deletions
        return (
            SafetyLevel.NEEDS_CONFIRMATION,
            f"Confirm deletion of directory: {dir_path}"
        )

    def _check_process_kill_safety(
        self,
        params: Dict[str, Any]
    ) -> Tuple[SafetyLevel, str]:
        """Check if killing a process is safe."""
        process_name = params.get('process_name', '')
        if not process_name:
            return (SafetyLevel.FORBIDDEN, "No process name specified")

        # Check if it's a protected process
        protected = self.rules.get('protected_processes', [])
        for protected_proc in protected:
            if protected_proc.lower() in process_name.lower():
                return (
                    SafetyLevel.FORBIDDEN,
                    f"Cannot kill protected system process: {process_name}"
                )

        # Require confirmation for killing processes
        return (
            SafetyLevel.NEEDS_CONFIRMATION,
            f"Confirm killing process: {process_name}"
        )

    def _check_registry_safety(
        self,
        params: Dict[str, Any]
    ) -> Tuple[SafetyLevel, str]:
        """Check if modifying registry is safe."""
        key_path = params.get('key_path', '')
        if not key_path:
            return (SafetyLevel.FORBIDDEN, "No registry key specified")

        # Forbid modifications to HKLM (system-wide settings)
        if key_path.startswith('HKEY_LOCAL_MACHINE') or key_path.startswith('HKLM'):
            return (
                SafetyLevel.FORBIDDEN,
                "Cannot modify system-wide registry keys (HKLM)"
            )

        # Require confirmation for all registry modifications
        return (
            SafetyLevel.NEEDS_CONFIRMATION,
            f"Confirm registry modification: {key_path}"
        )

    def _check_confirmation_required(
        self,
        command_type: str,
        params: Dict[str, Any]
    ) -> Tuple[SafetyLevel, str]:
        """Generate confirmation message for commands that require it."""
        if command_type == 'file_delete':
            return self._check_file_delete_safety(params)
        elif command_type == 'dir_delete':
            return self._check_dir_delete_safety(params)
        elif command_type == 'terminal_command':
            return self._check_terminal_command_safety(params)
        elif command_type == 'process_kill':
            return self._check_process_kill_safety(params)
        elif command_type == 'registry_modify':
            return self._check_registry_safety(params)
        else:
            return (
                SafetyLevel.NEEDS_CONFIRMATION,
                f"Command '{command_type}' requires user confirmation"
            )

    def is_safe(self, command_type: str, params: Dict[str, Any]) -> bool:
        """
        Quick check if command is safe (doesn't need confirmation).

        Args:
            command_type: Type of command
            params: Command parameters

        Returns:
            True if command is safe to execute immediately
        """
        level, _ = self.check_command_safety(command_type, params)
        return level == SafetyLevel.SAFE

    def is_forbidden(self, command_type: str, params: Dict[str, Any]) -> bool:
        """
        Quick check if command is forbidden.

        Args:
            command_type: Type of command
            params: Command parameters

        Returns:
            True if command should never be executed
        """
        level, _ = self.check_command_safety(command_type, params)
        return level == SafetyLevel.FORBIDDEN

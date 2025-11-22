"""Command whitelist for terminal execution."""

import logging
import yaml
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class CommandWhitelist:
    """
    Manage whitelist of safe terminal commands.

    Whitelisted commands can be executed without user confirmation.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize command whitelist.

        Args:
            config_path: Path to safety_rules.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "safety_rules.yaml"

        self.config_path = config_path
        self.whitelist = self._load_whitelist()
        logger.info(f"Command whitelist initialized with {len(self.whitelist)} commands")

    def _load_whitelist(self) -> List[str]:
        """Load whitelisted commands from config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                return rules.get('whitelisted_terminal_commands', [])
        except Exception as e:
            logger.error(f"Failed to load command whitelist: {e}")
            # Return minimal default whitelist
            return ['dir', 'ls', 'cd', 'pwd', 'echo', 'type']

    def is_whitelisted(self, command: str) -> bool:
        """
        Check if a command is whitelisted.

        Args:
            command: Full command string

        Returns:
            True if command is whitelisted
        """
        if not command:
            return False

        # Extract command name (first word)
        command_name = command.strip().split()[0].lower()

        # Remove common shell prefixes
        for prefix in ['cmd', 'cmd.exe', 'powershell', 'powershell.exe', 'pwsh', 'pwsh.exe']:
            if command_name == prefix:
                # Get actual command after shell
                parts = command.strip().split()
                if len(parts) > 2 and parts[1] in ['/c', '/C', '-c', '-Command']:
                    command_name = parts[2].lower()
                    break

        return command_name in [cmd.lower() for cmd in self.whitelist]

    def add_command(self, command: str):
        """
        Add a command to whitelist.

        Args:
            command: Command to add
        """
        if command and command not in self.whitelist:
            self.whitelist.append(command)
            logger.info(f"Added '{command}' to whitelist")

    def remove_command(self, command: str):
        """
        Remove a command from whitelist.

        Args:
            command: Command to remove
        """
        if command in self.whitelist:
            self.whitelist.remove(command)
            logger.info(f"Removed '{command}' from whitelist")

    def get_whitelist(self) -> List[str]:
        """
        Get current whitelist.

        Returns:
            List of whitelisted commands
        """
        return self.whitelist.copy()

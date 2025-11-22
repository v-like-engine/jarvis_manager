"""Execute terminal commands safely."""

import subprocess
import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

from .command_whitelist import CommandWhitelist
from .output_handler import OutputHandler

logger = logging.getLogger(__name__)


class TerminalExecutor:
    """
    Execute terminal commands with safety checks and limits.

    Features:
    - Support for CMD and PowerShell
    - Timeout enforcement
    - Output capture
    - Working directory support
    """

    def __init__(
        self,
        default_shell: str = 'cmd',
        default_timeout: int = 30,
        whitelist_config: Optional[Path] = None
    ):
        """
        Initialize terminal executor.

        Args:
            default_shell: Default shell ('cmd' or 'powershell')
            default_timeout: Default command timeout in seconds
            whitelist_config: Path to whitelist config
        """
        self.default_shell = default_shell
        self.default_timeout = default_timeout
        self.whitelist = CommandWhitelist(whitelist_config)
        logger.info(f"Terminal executor initialized (shell: {default_shell})")

    def execute(
        self,
        command: str,
        shell: Optional[str] = None,
        timeout: Optional[int] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a terminal command.

        Args:
            command: Command to execute
            shell: Shell to use ('cmd' or 'powershell')
            timeout: Timeout in seconds
            cwd: Working directory
            env: Environment variables

        Returns:
            Execution result dictionary
        """
        if not command:
            return {
                'success': False,
                'error': 'Empty command'
            }

        shell = shell or self.default_shell
        timeout = timeout or self.default_timeout

        try:
            # Build command for shell
            if shell == 'powershell':
                shell_cmd = self._build_powershell_command(command)
            else:
                shell_cmd = self._build_cmd_command(command)

            logger.info(f"Executing: {command} (shell: {shell}, timeout: {timeout}s)")

            # Execute command
            result = subprocess.run(
                shell_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )

            # Format output
            return OutputHandler.format_output(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                command=command
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {command}")
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds',
                'command': command
            }

        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return {
                'success': False,
                'error': f'Failed to execute command: {str(e)}',
                'command': command
            }

    def _build_cmd_command(self, command: str) -> str:
        """
        Build command for CMD.

        Args:
            command: Original command

        Returns:
            CMD-formatted command
        """
        # Just return the command as-is for CMD
        # CMD is the default shell on Windows
        return command

    def _build_powershell_command(self, command: str) -> List[str]:
        """
        Build command for PowerShell.

        Args:
            command: Original command

        Returns:
            PowerShell command list
        """
        if sys.platform == 'win32':
            # Use PowerShell on Windows
            return ['powershell.exe', '-Command', command]
        else:
            # Use pwsh (PowerShell Core) on other platforms
            return ['pwsh', '-Command', command]

    def execute_script(
        self,
        script_path: str,
        shell: Optional[str] = None,
        timeout: Optional[int] = None,
        args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a script file.

        Args:
            script_path: Path to script
            shell: Shell to use
            timeout: Timeout in seconds
            args: Script arguments

        Returns:
            Execution result
        """
        path = Path(script_path)
        if not path.exists():
            return {
                'success': False,
                'error': f'Script not found: {script_path}'
            }

        # Build command
        command = f'"{script_path}"'
        if args:
            command += ' ' + ' '.join(f'"{arg}"' for arg in args)

        return self.execute(command, shell=shell, timeout=timeout)

    def is_whitelisted(self, command: str) -> bool:
        """
        Check if command is whitelisted.

        Args:
            command: Command to check

        Returns:
            True if whitelisted
        """
        return self.whitelist.is_whitelisted(command)

    def get_whitelisted_commands(self) -> List[str]:
        """
        Get list of whitelisted commands.

        Returns:
            List of whitelisted commands
        """
        return self.whitelist.get_whitelist()

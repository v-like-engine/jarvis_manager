"""Handle terminal command output."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class OutputHandler:
    """
    Handle and format terminal command output.

    Features:
    - Parse output into structured format
    - Limit output size
    - Detect errors
    """

    MAX_OUTPUT_LENGTH = 10000  # Maximum characters in output

    @staticmethod
    def format_output(
        stdout: str,
        stderr: str,
        returncode: int,
        command: str
    ) -> Dict[str, Any]:
        """
        Format command output into structured result.

        Args:
            stdout: Standard output
            stderr: Standard error
            returncode: Process return code
            command: Original command

        Returns:
            Formatted result dictionary
        """
        # Truncate output if too long
        if stdout and len(stdout) > OutputHandler.MAX_OUTPUT_LENGTH:
            stdout = stdout[:OutputHandler.MAX_OUTPUT_LENGTH] + "\n... (output truncated)"

        if stderr and len(stderr) > OutputHandler.MAX_OUTPUT_LENGTH:
            stderr = stderr[:OutputHandler.MAX_OUTPUT_LENGTH] + "\n... (output truncated)"

        # Determine success
        success = returncode == 0

        result = {
            'success': success,
            'returncode': returncode,
            'stdout': stdout.strip() if stdout else '',
            'stderr': stderr.strip() if stderr else '',
            'command': command,
        }

        # Add error message if failed
        if not success:
            result['error'] = OutputHandler._extract_error_message(stderr, returncode)

        # Add message
        if success:
            result['message'] = 'Command executed successfully'
        else:
            result['message'] = f'Command failed with exit code {returncode}'

        return result

    @staticmethod
    def _extract_error_message(stderr: str, returncode: int) -> str:
        """
        Extract concise error message from stderr.

        Args:
            stderr: Standard error output
            returncode: Return code

        Returns:
            Error message string
        """
        if stderr:
            # Get first non-empty line
            lines = [line.strip() for line in stderr.split('\n') if line.strip()]
            if lines:
                return lines[0]

        return f"Command failed with exit code {returncode}"

    @staticmethod
    def parse_lines(output: str) -> List[str]:
        """
        Parse output into lines.

        Args:
            output: Output string

        Returns:
            List of lines
        """
        if not output:
            return []

        return [line.rstrip() for line in output.split('\n')]

    @staticmethod
    def detect_errors(output: str) -> List[str]:
        """
        Detect error patterns in output.

        Args:
            output: Output to check

        Returns:
            List of detected errors
        """
        errors = []
        error_keywords = [
            'error',
            'exception',
            'failed',
            'fatal',
            'cannot',
            'unable to',
            'not found',
            'access denied',
            'permission denied',
        ]

        lines = OutputHandler.parse_lines(output)
        for line in lines:
            line_lower = line.lower()
            for keyword in error_keywords:
                if keyword in line_lower:
                    errors.append(line)
                    break

        return errors

    @staticmethod
    def format_table(lines: List[str]) -> List[Dict[str, str]]:
        """
        Try to parse output as a table (for commands like dir, ls, tasklist).

        Args:
            lines: Output lines

        Returns:
            List of row dictionaries (if parseable as table)
        """
        # This is a simple implementation
        # Could be enhanced to detect column positions automatically
        if not lines:
            return []

        # For now, just return lines as-is
        # A full implementation would parse column-aligned output
        return [{'line': line} for line in lines]

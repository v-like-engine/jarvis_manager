"""Manage command execution with safety checks and confirmation handling."""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from .safety_checker import SafetyChecker, SafetyLevel
from .command_validator import CommandValidator, CommandRequest, CommandResponse
from .command_router import CommandRouter

logger = logging.getLogger(__name__)


class ExecutionManager:
    """
    Manage command execution lifecycle.

    Features:
    - Safety checking before execution
    - Confirmation management for dangerous commands
    - Command history
    - Error handling
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize execution manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.safety_checker = SafetyChecker()
        self.command_router = CommandRouter(config)

        # Command history
        self.history: Dict[str, Dict[str, Any]] = {}

        # Pending confirmations
        self.pending_confirmations: Dict[str, CommandRequest] = {}

        logger.info("Execution manager initialized")

    def execute_command(self, request: CommandRequest) -> CommandResponse:
        """
        Execute a command with safety checks.

        Args:
            request: Command request

        Returns:
            Command response
        """
        try:
            # Validate and sanitize parameters
            try:
                params = CommandValidator.validate_and_sanitize(
                    request.command_type,
                    request.params
                )
            except ValueError as e:
                logger.error(f"Command validation failed: {e}")
                return CommandResponse(
                    success=False,
                    error=str(e)
                )

            # Check safety
            safety_level, safety_message = self.safety_checker.check_command_safety(
                request.command_type,
                params
            )

            # Handle based on safety level
            if safety_level == SafetyLevel.FORBIDDEN:
                logger.warning(f"Forbidden command blocked: {request.command_type}")
                return CommandResponse(
                    success=False,
                    error=f"Command forbidden: {safety_message}"
                )

            elif safety_level == SafetyLevel.NEEDS_CONFIRMATION:
                # Check if already confirmed
                if request.confirmed:
                    logger.info(f"Confirmed command executing: {request.command_type}")
                    # Execute the command
                    result = self._execute(request.command_type, params)
                    self._add_to_history(request, result, confirmed=True)
                    return CommandResponse(
                        success=result.get('success', False),
                        result=result,
                        error=result.get('error')
                    )
                else:
                    # Request confirmation
                    logger.info(f"Requesting confirmation for: {request.command_type}")

                    # Store pending confirmation
                    self.pending_confirmations[request.command_id] = request

                    return CommandResponse(
                        success=False,
                        requires_confirmation=True,
                        confirmation_message=safety_message
                    )

            else:  # SAFE
                # Execute immediately
                logger.info(f"Safe command executing: {request.command_type}")
                result = self._execute(request.command_type, params)
                self._add_to_history(request, result, confirmed=False)
                return CommandResponse(
                    success=result.get('success', False),
                    result=result,
                    error=result.get('error')
                )

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return CommandResponse(
                success=False,
                error=f"Execution error: {str(e)}"
            )

    def _execute(self, command_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute command via router.

        Args:
            command_type: Command type
            params: Command parameters

        Returns:
            Execution result
        """
        try:
            return self.command_router.route(command_type, params)
        except Exception as e:
            logger.error(f"Router execution error: {e}")
            return {
                'success': False,
                'error': f'Execution failed: {str(e)}'
            }

    def confirm_command(self, command_id: str) -> CommandResponse:
        """
        Confirm a pending command.

        Args:
            command_id: Command ID

        Returns:
            Command response after execution
        """
        # Check if command is pending
        if command_id not in self.pending_confirmations:
            return CommandResponse(
                success=False,
                error=f"No pending command with ID: {command_id}"
            )

        # Get pending command
        request = self.pending_confirmations[command_id]

        # Mark as confirmed and execute
        request.confirmed = True

        # Remove from pending
        del self.pending_confirmations[command_id]

        # Execute
        return self.execute_command(request)

    def cancel_command(self, command_id: str) -> Dict[str, Any]:
        """
        Cancel a pending command.

        Args:
            command_id: Command ID

        Returns:
            Result dictionary
        """
        if command_id in self.pending_confirmations:
            del self.pending_confirmations[command_id]
            return {
                'success': True,
                'message': 'Command cancelled'
            }
        else:
            return {
                'success': False,
                'error': f'No pending command with ID: {command_id}'
            }

    def _add_to_history(
        self,
        request: CommandRequest,
        result: Dict[str, Any],
        confirmed: bool
    ):
        """
        Add command to history.

        Args:
            request: Command request
            result: Execution result
            confirmed: Whether command required confirmation
        """
        self.history[request.command_id] = {
            'command_id': request.command_id,
            'command_type': request.command_type,
            'params': request.params,
            'language': request.language,
            'confirmed': confirmed,
            'result': result,
            'timestamp': datetime.now().isoformat(),
        }

        # Keep only last 100 commands
        if len(self.history) > 100:
            oldest_key = min(self.history.keys())
            del self.history[oldest_key]

    def get_history(self, limit: int = 10) -> list:
        """
        Get command history.

        Args:
            limit: Maximum number of history items

        Returns:
            List of history items
        """
        items = list(self.history.values())
        # Sort by timestamp, most recent first
        items.sort(key=lambda x: x['timestamp'], reverse=True)
        return items[:limit]

    def get_pending_confirmations(self) -> list:
        """
        Get list of pending confirmations.

        Returns:
            List of pending commands
        """
        return [
            {
                'command_id': cmd.command_id,
                'command_type': cmd.command_type,
                'params': cmd.params,
                'language': cmd.language,
            }
            for cmd in self.pending_confirmations.values()
        ]

    def validate_command(self, request: CommandRequest) -> Dict[str, Any]:
        """
        Validate command without executing.

        Args:
            request: Command request

        Returns:
            Validation result
        """
        try:
            # Validate parameters
            params = CommandValidator.validate_and_sanitize(
                request.command_type,
                request.params
            )

            # Check safety
            safety_level, safety_message = self.safety_checker.check_command_safety(
                request.command_type,
                params
            )

            return {
                'valid': True,
                'safety_level': safety_level.name,
                'requires_confirmation': safety_level == SafetyLevel.NEEDS_CONFIRMATION,
                'forbidden': safety_level == SafetyLevel.FORBIDDEN,
                'message': safety_message,
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

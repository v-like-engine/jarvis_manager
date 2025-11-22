"""Command Service - Main FastAPI application."""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import uuid

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from shared.utils import setup_logger
from .command_validator import CommandRequest, CommandResponse, CommandValidator
from .execution_manager import ExecutionManager

# Setup logging
log_file = Path(__file__).parent.parent / "logs" / "command_service.log"
logger = setup_logger("command_service", log_file=log_file, level=logging.INFO)

# Load configuration
config_file = Path(__file__).parent.parent / "config" / "command_config.yaml"
try:
    with open(config_file, 'r', encoding='utf-8') as f:
        CONFIG = yaml.safe_load(f)
except Exception as e:
    logger.warning(f"Failed to load config: {e}, using defaults")
    CONFIG = {
        'service': {
            'host': '0.0.0.0',
            'port': 8002
        }
    }

# Create FastAPI app
app = FastAPI(
    title="Gerald Command Service",
    description="Execute system commands safely with validation and confirmation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize execution manager
execution_manager = ExecutionManager(CONFIG)


# Request/Response Models
class ExecuteCommandRequest(BaseModel):
    """Request to execute a command."""
    command_type: str = Field(..., description="Type of command to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    language: str = Field(default="en", description="Response language (en/ru)")
    confirmed: bool = Field(default=False, description="User confirmed dangerous operation")


class ConfirmCommandRequest(BaseModel):
    """Request to confirm a pending command."""
    command_id: str = Field(..., description="ID of command to confirm")


class ValidateCommandRequest(BaseModel):
    """Request to validate a command."""
    command_type: str = Field(..., description="Type of command")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Gerald Command Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "command_service"
    }


@app.post("/commands/execute", response_model=CommandResponse)
async def execute_command(request: ExecuteCommandRequest):
    """
    Execute a command.

    This endpoint:
    1. Validates the command
    2. Checks safety level
    3. Executes if safe OR returns confirmation request
    4. Returns execution result
    """
    try:
        # Create command request with unique ID
        command_request = CommandRequest(
            command_id=str(uuid.uuid4()),
            command_type=request.command_type,
            language=request.language,
            params=request.params,
            confirmed=request.confirmed
        )

        # Execute via execution manager
        response = execution_manager.execute_command(command_request)

        logger.info(
            f"Command executed: {request.command_type} "
            f"(success={response.success}, "
            f"requires_confirmation={response.requires_confirmation})"
        )

        return response

    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Command execution failed: {str(e)}"
        )


@app.post("/commands/validate")
async def validate_command(request: ValidateCommandRequest):
    """
    Validate a command without executing it.

    Returns safety level and whether confirmation is required.
    """
    try:
        command_request = CommandRequest(
            command_id=str(uuid.uuid4()),
            command_type=request.command_type,
            params=request.params
        )

        validation_result = execution_manager.validate_command(command_request)

        return {
            "success": True,
            "validation": validation_result
        }

    except Exception as e:
        logger.error(f"Error validating command: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}"
        )


@app.post("/commands/confirm")
async def confirm_command(request: ConfirmCommandRequest):
    """
    Confirm and execute a pending dangerous command.

    The command must have been previously submitted and returned
    requires_confirmation=True.
    """
    try:
        response = execution_manager.confirm_command(request.command_id)

        logger.info(f"Command confirmed and executed: {request.command_id}")

        return response

    except Exception as e:
        logger.error(f"Error confirming command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confirmation failed: {str(e)}"
        )


@app.delete("/commands/{command_id}")
async def cancel_command(command_id: str):
    """
    Cancel a pending command.
    """
    try:
        result = execution_manager.cancel_command(command_id)

        if result['success']:
            logger.info(f"Command cancelled: {command_id}")
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result['error']
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cancellation failed: {str(e)}"
        )


@app.get("/commands/pending")
async def get_pending_confirmations():
    """
    Get list of commands pending confirmation.
    """
    try:
        pending = execution_manager.get_pending_confirmations()
        return {
            "success": True,
            "count": len(pending),
            "commands": pending
        }

    except Exception as e:
        logger.error(f"Error getting pending confirmations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending confirmations: {str(e)}"
        )


@app.get("/commands/history")
async def get_command_history(limit: int = 10):
    """
    Get command execution history.
    """
    try:
        history = execution_manager.get_history(limit=limit)
        return {
            "success": True,
            "count": len(history),
            "history": history
        }

    except Exception as e:
        logger.error(f"Error getting command history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get history: {str(e)}"
        )


@app.get("/commands/apps/list")
async def list_installed_apps():
    """
    Get list of all installed applications.
    """
    try:
        apps = execution_manager.command_router.app_database.get_all_apps()
        return {
            "success": True,
            "count": len(apps),
            "apps": apps
        }

    except Exception as e:
        logger.error(f"Error listing apps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list apps: {str(e)}"
        )


@app.get("/commands/apps/running")
async def list_running_apps():
    """
    Get list of currently running applications.
    """
    try:
        apps = execution_manager.command_router.app_closer.get_running_apps()
        return {
            "success": True,
            "count": len(apps),
            "apps": apps
        }

    except Exception as e:
        logger.error(f"Error listing running apps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list running apps: {str(e)}"
        )


@app.get("/commands/apps/search")
async def search_apps(query: str, limit: int = 10):
    """
    Search for applications by name.
    """
    try:
        apps = execution_manager.command_router.app_database.search(query, limit=limit)
        return {
            "success": True,
            "query": query,
            "count": len(apps),
            "apps": apps
        }

    except Exception as e:
        logger.error(f"Error searching apps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search apps: {str(e)}"
        )


@app.post("/commands/apps/refresh")
async def refresh_app_database():
    """
    Refresh the application database by re-scanning the system.
    """
    try:
        execution_manager.command_router._refresh_app_database()

        stats = execution_manager.command_router.app_database.stats()

        return {
            "success": True,
            "message": "App database refreshed",
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Error refreshing app database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh app database: {str(e)}"
        )


@app.get("/commands/status")
async def get_service_status():
    """
    Get service status and statistics.
    """
    try:
        app_stats = execution_manager.command_router.app_database.stats()
        history_count = len(execution_manager.history)
        pending_count = len(execution_manager.pending_confirmations)

        return {
            "success": True,
            "status": "running",
            "app_database": app_stats,
            "command_history_count": history_count,
            "pending_confirmations_count": pending_count
        }

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on service startup."""
    logger.info("=" * 60)
    logger.info("Gerald Command Service starting...")
    logger.info(f"Version: 1.0.0")
    logger.info(f"Config: {config_file}")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on service shutdown."""
    logger.info("Gerald Command Service shutting down...")


# Main entry point
if __name__ == "__main__":
    import uvicorn

    host = CONFIG.get('service', {}).get('host', '0.0.0.0')
    port = CONFIG.get('service', {}).get('port', 8002)

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

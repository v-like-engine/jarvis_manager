"""
LLM Service Main Entry Point
FastAPI REST API for LLM-based response generation

Endpoints:
- POST /llm/generate - Generate response
- POST /llm/set_character - Switch character
- GET /llm/characters - List available characters
- POST /llm/clear_context - Clear conversation history
- GET /llm/status - Health check
- GET /llm/model_info - Model information
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from model_manager import ModelManager
from llm_engine import LLMEngine
from character_manager import CharacterManager
from context_manager import ContextManager
from prompt_builder import PromptBuilder
from response_generator import ResponseGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_PATH = "/home/user/jarvis_manager/services/llm_service/config/llm_config.yaml"
MODEL_SETTINGS_PATH = "/home/user/jarvis_manager/services/llm_service/config/model_settings.yaml"
CHARACTERS_DIR = "/home/user/jarvis_manager/services/llm_service/characters"
PROMPTS_DIR = "/home/user/jarvis_manager/services/llm_service/prompts"


# Request/Response Models
class GenerateRequest(BaseModel):
    """Request model for text generation"""
    text: str = Field(..., description="User input text")
    language: Optional[str] = Field("en", description="Language code (en, ru)")
    character: Optional[str] = Field(None, description="Character name (overrides current)")
    scenario: Optional[str] = Field("chat", description="Scenario type")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    use_template: Optional[bool] = Field(True, description="Try to use template response")


class GenerateResponse(BaseModel):
    """Response model for text generation"""
    response_text: str
    language: str
    should_speak: bool
    emotion: str
    scenario: str
    metadata: Dict[str, Any]


class SetCharacterRequest(BaseModel):
    """Request model for setting character"""
    character: str = Field(..., description="Character name")
    language: Optional[str] = Field(None, description="Language code")
    emotion: Optional[str] = Field("neutral", description="Emotional state")


class ClearContextRequest(BaseModel):
    """Request model for clearing context"""
    session_id: Optional[str] = Field(None, description="Session ID (None = all)")


class StatusResponse(BaseModel):
    """Response model for status check"""
    status: str
    service: str
    version: str
    model_loaded: bool
    character_loaded: bool
    current_character: Optional[str]
    available_characters: List[str]


# Global service components
app = FastAPI(
    title="Jarvis LLM Service",
    description="Local LLM service with character personalities",
    version="1.0.0",
)

# Service state
service_state = {
    "model_manager": None,
    "llm_engine": None,
    "character_manager": None,
    "context_manager": None,
    "prompt_builder": None,
    "response_generator": None,
    "config": None,
}


def load_config() -> Dict[str, Any]:
    """Load service configuration"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def initialize_service():
    """Initialize all service components"""
    logger.info("Initializing LLM service...")

    try:
        # Load configuration
        config = load_config()
        service_state["config"] = config

        # Initialize model manager
        logger.info("Initializing model manager...")
        model_manager = ModelManager(CONFIG_PATH)
        service_state["model_manager"] = model_manager

        # Ensure model is downloaded and ready
        logger.info("Ensuring model is ready...")
        model_path = model_manager.ensure_model_ready()
        logger.info(f"Model ready: {model_path}")

        # Initialize LLM engine
        logger.info("Loading LLM engine...")
        llm_engine = LLMEngine(
            model_path=str(model_path),
            model_settings_path=MODEL_SETTINGS_PATH,
        )
        service_state["llm_engine"] = llm_engine

        # Initialize character manager
        logger.info("Loading characters...")
        character_manager = CharacterManager(CHARACTERS_DIR)
        service_state["character_manager"] = character_manager

        # Load default character
        default_character = config["service"].get("default_character", "gerald")
        character_manager.load_character(default_character)
        logger.info(f"Loaded default character: {default_character}")

        # Initialize context manager
        context_config = config["service"]["context"]
        context_manager = ContextManager(
            max_exchanges=context_config["max_exchanges"],
            max_tokens_per_exchange=context_config["max_tokens_per_exchange"],
        )
        service_state["context_manager"] = context_manager

        # Initialize prompt builder
        prompt_builder = PromptBuilder(PROMPTS_DIR)
        service_state["prompt_builder"] = prompt_builder

        # Initialize response generator
        response_generator = ResponseGenerator(
            llm_engine=llm_engine,
            character_manager=character_manager,
            context_manager=context_manager,
            prompt_builder=prompt_builder,
            use_cache=config["service"]["performance"]["cache_enabled"],
        )
        service_state["response_generator"] = response_generator

        logger.info("LLM service initialized successfully!")

    except Exception as e:
        logger.error(f"Failed to initialize service: {e}", exc_info=True)
        raise


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    initialize_service()


# API Endpoints

@app.post("/llm/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """
    Generate a response to user input

    This endpoint generates character-appropriate responses using the LLM.
    """
    try:
        generator = service_state["response_generator"]
        char_manager = service_state["character_manager"]

        if not generator:
            raise HTTPException(status_code=503, detail="Service not initialized")

        # Switch character if requested
        if request.character:
            try:
                char_manager.load_character(request.character)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Generate response
        kwargs = {}
        if request.context:
            kwargs.update(request.context)

        response = generator.generate(
            user_input=request.text,
            scenario=request.scenario,
            language=request.language,
            session_id=request.session_id,
            use_template=request.use_template,
            **kwargs
        )

        return GenerateResponse(**response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/llm/set_character")
async def set_character(request: SetCharacterRequest):
    """
    Switch to a different character

    Changes the current character and optionally sets language and emotion.
    """
    try:
        char_manager = service_state["character_manager"]

        if not char_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")

        # Load character
        try:
            char_manager.load_character(request.character)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Set language if provided
        if request.language:
            char_manager.set_language(request.language)

        # Set emotion if provided
        if request.emotion:
            char_manager.set_emotion(request.emotion)

        return {
            "status": "success",
            "character": request.character,
            "language": char_manager.current_language,
            "emotion": char_manager.current_emotion,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting character: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to set character: {str(e)}")


@app.get("/llm/characters")
async def list_characters():
    """
    List all available characters

    Returns a list of character names and their basic information.
    """
    try:
        char_manager = service_state["character_manager"]

        if not char_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")

        characters = char_manager.list_characters()

        # Get detailed info for each character
        characters_info = []
        for char_name in characters:
            try:
                char = char_manager.get_character(char_name)
                characters_info.append({
                    "name": char.name,
                    "description": char.description,
                    "archetype": char.personality.archetype,
                    "languages": char.language_support,
                })
            except Exception as e:
                logger.warning(f"Failed to get info for character {char_name}: {e}")

        return {
            "characters": characters_info,
            "current_character": char_manager.current_character.name if char_manager.current_character else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing characters: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/llm/clear_context")
async def clear_context(request: ClearContextRequest):
    """
    Clear conversation context/history

    Clears the conversation history for a specific session or all sessions.
    """
    try:
        context_manager = service_state["context_manager"]

        if not context_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")

        if request.session_id:
            context_manager.clear_history(request.session_id)
            message = f"Cleared history for session {request.session_id}"
        else:
            # Clear all sessions
            for session_id in context_manager.list_sessions():
                context_manager.clear_history(session_id)
            message = "Cleared all conversation history"

        return {
            "status": "success",
            "message": message,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing context: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm/status", response_model=StatusResponse)
async def get_status():
    """
    Get service status and health check

    Returns the current status of the LLM service and its components.
    """
    try:
        char_manager = service_state["character_manager"]
        llm_engine = service_state["llm_engine"]

        model_loaded = llm_engine is not None
        character_loaded = char_manager is not None and char_manager.current_character is not None

        current_character = None
        available_characters = []

        if char_manager:
            available_characters = char_manager.list_characters()
            if char_manager.current_character:
                current_character = char_manager.current_character.name

        return StatusResponse(
            status="operational" if model_loaded and character_loaded else "degraded",
            service="llm_service",
            version="1.0.0",
            model_loaded=model_loaded,
            character_loaded=character_loaded,
            current_character=current_character,
            available_characters=available_characters,
        )

    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        return StatusResponse(
            status="error",
            service="llm_service",
            version="1.0.0",
            model_loaded=False,
            character_loaded=False,
            current_character=None,
            available_characters=[],
        )


@app.get("/llm/model_info")
async def get_model_info():
    """
    Get information about the loaded model

    Returns details about the LLM model and its configuration.
    """
    try:
        model_manager = service_state["model_manager"]
        llm_engine = service_state["llm_engine"]

        if not model_manager or not llm_engine:
            raise HTTPException(status_code=503, detail="Service not initialized")

        model_info = model_manager.get_model_info()
        engine_info = llm_engine.get_model_info()

        return {
            "model": model_info,
            "engine": engine_info,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Jarvis LLM Service",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/llm/generate",
            "/llm/set_character",
            "/llm/characters",
            "/llm/clear_context",
            "/llm/status",
            "/llm/model_info",
        ],
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


def main():
    """Run the service"""
    config = load_config()
    service_config = config["service"]

    host = service_config["host"]
    port = service_config["port"]

    logger.info(f"Starting LLM service on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()

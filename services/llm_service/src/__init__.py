"""
LLM Service for Jarvis Voice Assistant
Agent 2 - Local Language Model and Character Management

This service provides:
- Local LLM inference using llama.cpp
- Character personality management (starting with Gerald)
- Prompt building and context management
- Natural language response generation
- Bilingual support (English and Russian)
"""

__version__ = "1.0.0"
__author__ = "Agent 2 - LLM Service"

from .model_manager import ModelManager
from .llm_engine import LLMEngine
from .character_manager import CharacterManager
from .prompt_builder import PromptBuilder
from .context_manager import ContextManager
from .response_generator import ResponseGenerator

__all__ = [
    "ModelManager",
    "LLMEngine",
    "CharacterManager",
    "PromptBuilder",
    "ContextManager",
    "ResponseGenerator",
]

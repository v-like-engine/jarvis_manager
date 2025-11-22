"""
Response Generator - Generate character-based responses

Handles:
- Integrating character, context, and prompts
- Generating responses with LLM
- Applying character traits to responses
- Managing different response scenarios
- Caching common responses
"""

import logging
import time
from typing import Dict, Any, Optional
from enum import Enum

from .character_manager import CharacterManager
from .context_manager import ContextManager
from .prompt_builder import PromptBuilder
from .llm_engine import LLMEngine

logger = logging.getLogger(__name__)


class ResponseScenario(str, Enum):
    """Response scenario types"""
    CHAT = "chat"
    CONFIRMATION = "confirmation"
    SAFETY_WARNING = "safety_warning"
    GREETING = "greeting"
    CLARIFICATION = "clarification"
    ERROR = "error"
    REFUSAL = "refusal"
    SELF_DESCRIPTION = "self_description"


class ResponseGenerator:
    """Generates character-appropriate responses using LLM"""

    def __init__(
        self,
        llm_engine: LLMEngine,
        character_manager: CharacterManager,
        context_manager: ContextManager,
        prompt_builder: PromptBuilder,
        use_cache: bool = True,
    ):
        """
        Initialize ResponseGenerator

        Args:
            llm_engine: LLM inference engine
            character_manager: Character personality manager
            context_manager: Conversation context manager
            prompt_builder: Prompt construction utility
            use_cache: Enable response caching
        """
        self.llm = llm_engine
        self.character_manager = character_manager
        self.context_manager = context_manager
        self.prompt_builder = prompt_builder
        self.use_cache = use_cache

        # Simple response cache (for templates and common responses)
        self.cache: Dict[str, str] = {}

        logger.info("ResponseGenerator initialized")

    def generate(
        self,
        user_input: str,
        scenario: str = "chat",
        language: Optional[str] = None,
        session_id: Optional[str] = None,
        use_template: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response to user input

        Args:
            user_input: User's message/input
            scenario: Response scenario type
            language: Language code (None = use character's current language)
            session_id: Optional session ID for context
            use_template: Try to use template response if applicable
            **kwargs: Additional parameters (e.g., command, description, error)

        Returns:
            Response dictionary with text, metadata, etc.
        """
        start_time = time.time()

        # Set language if provided
        if language:
            self.character_manager.set_language(language)

        current_language = self.character_manager.current_language

        # Try to use template response first (for simple scenarios)
        if use_template and scenario in ["greeting", "confirmation", "refusal"]:
            template_response = self._try_template_response(scenario, current_language, **kwargs)
            if template_response:
                logger.info(f"Using template response for '{scenario}'")
                return self._build_response_dict(
                    template_response,
                    current_language,
                    scenario,
                    time.time() - start_time,
                    tokens_used=0,
                    from_template=True,
                )

        # Generate response using LLM
        response_text = self._generate_llm_response(
            user_input,
            scenario,
            current_language,
            session_id,
            **kwargs
        )

        # Add messages to context (if not a template scenario)
        if scenario == "chat":
            self.context_manager.add_user_message(user_input, session_id)
            self.context_manager.add_assistant_message(response_text, session_id)

        # Build response dictionary
        generation_time = time.time() - start_time
        tokens_used = self.llm.count_tokens(response_text)

        return self._build_response_dict(
            response_text,
            current_language,
            scenario,
            generation_time,
            tokens_used,
            from_template=False,
        )

    def _try_template_response(
        self,
        scenario: str,
        language: str,
        **kwargs
    ) -> Optional[str]:
        """
        Try to get a template response

        Args:
            scenario: Response scenario
            language: Language code
            **kwargs: Template variables

        Returns:
            Template response text or None
        """
        try:
            # Map scenario to template type
            template_map = {
                "greeting": "greeting",
                "confirmation": "confirmation",
                "refusal": "refusal",
                "clarification": "clarification",
                "error": "error",
            }

            template_type = template_map.get(scenario)
            if not template_type:
                return None

            return self.character_manager.get_template(
                template_type,
                language,
                **kwargs
            )

        except Exception as e:
            logger.warning(f"Failed to get template response: {e}")
            return None

    def _generate_llm_response(
        self,
        user_input: str,
        scenario: str,
        language: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response using LLM

        Args:
            user_input: User input
            scenario: Response scenario
            language: Language code
            session_id: Optional session ID
            **kwargs: Scenario-specific parameters

        Returns:
            Generated response text
        """
        # Get character system prompt
        system_prompt = self.character_manager.get_system_prompt(language)

        # Get conversation context
        context = None
        if scenario == "chat":
            rules = self.character_manager.get_response_rules()
            if rules.require_context:
                context = self.context_manager.get_context_for_prompt(
                    session_id,
                    rules.context_window
                )

        # Build prompt based on scenario
        prompt = self._build_scenario_prompt(
            user_input,
            system_prompt,
            context,
            scenario,
            language,
            **kwargs
        )

        # Get character-specific generation parameters
        rules = self.character_manager.get_response_rules()

        # Generate with LLM
        logger.debug(f"Generating response for scenario '{scenario}'")

        response_text = self.llm.generate_with_character(
            prompt=prompt,
            character_name=self.character_manager.current_character.name,
            scenario=scenario,
        )

        # Post-process response
        response_text = self._post_process_response(response_text, rules)

        return response_text

    def _build_scenario_prompt(
        self,
        user_input: str,
        system_prompt: str,
        context: Optional[str],
        scenario: str,
        language: str,
        **kwargs
    ) -> str:
        """Build prompt for specific scenario"""

        if scenario == "chat":
            return self.prompt_builder.build_chat_prompt(
                user_input,
                system_prompt,
                context,
                language,
            )

        elif scenario == "confirmation":
            command = kwargs.get("command", user_input)
            return self.prompt_builder.build_confirmation_prompt(
                command,
                system_prompt,
                language,
            )

        elif scenario == "safety_warning":
            command = kwargs.get("command", user_input)
            description = kwargs.get("description", "perform this operation")
            return self.prompt_builder.build_safety_prompt(
                command,
                description,
                system_prompt,
                language,
            )

        elif scenario == "clarification":
            return self.prompt_builder.build_clarification_prompt(
                user_input,
                system_prompt,
                context,
                language,
            )

        elif scenario == "error":
            error = kwargs.get("error", "Unknown error")
            return self.prompt_builder.build_error_prompt(
                error,
                system_prompt,
                language,
            )

        else:
            # Default to chat
            return self.prompt_builder.build_chat_prompt(
                user_input,
                system_prompt,
                context,
                language,
            )

    def _post_process_response(self, response: str, rules) -> str:
        """
        Post-process generated response

        Args:
            response: Raw generated text
            rules: Character response rules

        Returns:
            Processed response
        """
        # Strip whitespace
        response = response.strip()

        # Remove any partial sentences at the end if too long
        if rules.prefer_short_responses:
            # Split into sentences
            sentences = response.split('. ')
            if len(sentences) > 2:
                # Keep first 1-2 sentences
                response = '. '.join(sentences[:2])
                if not response.endswith('.'):
                    response += '.'

        return response

    def _build_response_dict(
        self,
        response_text: str,
        language: str,
        scenario: str,
        generation_time: float,
        tokens_used: int,
        from_template: bool = False,
    ) -> Dict[str, Any]:
        """
        Build response dictionary

        Args:
            response_text: The generated response
            language: Language code
            scenario: Scenario type
            generation_time: Time taken to generate
            tokens_used: Tokens in response
            from_template: Whether response came from template

        Returns:
            Response dictionary
        """
        # Determine if response should be spoken
        should_speak = scenario in ["chat", "greeting", "confirmation", "error", "safety_warning"]

        # Determine emotion/tone
        emotion = "neutral"
        if scenario == "safety_warning":
            emotion = "stern"
        elif scenario in ["greeting", "confirmation"]:
            emotion = "helpful"
        elif scenario == "error":
            emotion = "stern"

        return {
            "response_text": response_text,
            "language": language,
            "should_speak": should_speak,
            "emotion": emotion,
            "scenario": scenario,
            "metadata": {
                "tokens_used": tokens_used,
                "inference_time_ms": int(generation_time * 1000),
                "from_template": from_template,
                "character": self.character_manager.current_character.name if self.character_manager.current_character else None,
            },
        }

    def generate_greeting(
        self,
        language: Optional[str] = None,
        time_of_day: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a greeting

        Args:
            language: Language code
            time_of_day: Optional time of day (morning, afternoon, evening, night)

        Returns:
            Response dictionary
        """
        return self.generate(
            user_input="",
            scenario="greeting",
            language=language,
            use_template=True,
            time_of_day=time_of_day,
        )

    def generate_self_description(
        self,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate self-description (when user asks "who are you?")

        Args:
            language: Language code

        Returns:
            Response dictionary
        """
        if language:
            self.character_manager.set_language(language)

        lang = self.character_manager.current_language

        # Get self-description template from character
        description = self.character_manager.get_template("self_description", lang)

        return self._build_response_dict(
            description,
            lang,
            "self_description",
            generation_time=0.0,
            tokens_used=0,
            from_template=True,
        )


if __name__ == "__main__":
    # Test response generator
    logging.basicConfig(level=logging.INFO)

    # This requires all components to be set up
    # See main.py for full integration test
    print("ResponseGenerator module loaded successfully")
    print("Run main.py for full integration test")

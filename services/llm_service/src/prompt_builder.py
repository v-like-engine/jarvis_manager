"""
Prompt Builder - Construct prompts for LLM generation

Handles:
- Building prompts with system instructions
- Injecting character personality
- Adding conversation context
- Scenario-specific prompt templates
- Multi-language support
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from jinja2 import Template

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds prompts for LLM generation with character and context"""

    def __init__(self, prompts_dir: str):
        """
        Initialize PromptBuilder

        Args:
            prompts_dir: Directory containing prompt template YAML files
        """
        self.prompts_dir = Path(prompts_dir)

        # Load prompt templates
        self.system_prompts = self._load_yaml("system_prompts.yaml")
        self.safety_prompts = self._load_yaml("safety_prompts.yaml")
        self.greeting_templates = self._load_yaml("greeting_templates.yaml")

        logger.info("PromptBuilder initialized")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file from the prompts directory"""
        file_path = self.prompts_dir / filename

        if not file_path.exists():
            logger.warning(f"Prompt file not found: {file_path}")
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def build_prompt(
        self,
        user_input: str,
        system_prompt: str,
        context: Optional[str] = None,
        scenario: str = "chat",
        language: str = "en",
        **kwargs
    ) -> str:
        """
        Build a complete prompt for LLM generation

        Args:
            user_input: The user's message/input
            system_prompt: System prompt defining character behavior
            context: Optional conversation context
            scenario: Scenario type (chat, confirmation, safety_warning, etc.)
            language: Language code
            **kwargs: Additional template variables

        Returns:
            Complete prompt text
        """
        # Get scenario template if available
        scenario_template = self._get_scenario_template(scenario, language, **kwargs)

        # Build the prompt parts
        parts = []

        # 1. System prompt (character instructions)
        if system_prompt:
            parts.append(f"### System Instructions ###\n{system_prompt}")

        # 2. Scenario-specific instructions (if any)
        if scenario_template and scenario != "chat":
            parts.append(f"\n### Task ###\n{scenario_template}")

        # 3. Conversation context (if available)
        if context:
            parts.append(f"\n### Previous Conversation ###\n{context}")

        # 4. Current user input
        parts.append(f"\n### User ###\n{user_input}")

        # 5. Assistant response prefix
        parts.append("\n### Assistant ###\n")

        prompt = "\n".join(parts)

        logger.debug(f"Built prompt for scenario '{scenario}' ({len(prompt)} chars)")

        return prompt

    def build_chat_prompt(
        self,
        user_input: str,
        system_prompt: str,
        context: Optional[str] = None,
        language: str = "en",
    ) -> str:
        """
        Build a prompt for general chat/conversation

        Args:
            user_input: User's message
            system_prompt: Character system prompt
            context: Optional conversation history
            language: Language code

        Returns:
            Chat prompt
        """
        return self.build_prompt(
            user_input=user_input,
            system_prompt=system_prompt,
            context=context,
            scenario="chat",
            language=language,
        )

    def build_confirmation_prompt(
        self,
        command: str,
        system_prompt: str,
        language: str = "en",
    ) -> str:
        """
        Build a prompt for command confirmation

        Args:
            command: The command to confirm
            system_prompt: Character system prompt
            language: Language code

        Returns:
            Confirmation prompt
        """
        return self.build_prompt(
            user_input=command,
            system_prompt=system_prompt,
            context=None,
            scenario="command_confirmation",
            language=language,
            command=command,
        )

    def build_safety_prompt(
        self,
        command: str,
        description: str,
        system_prompt: str,
        language: str = "en",
    ) -> str:
        """
        Build a prompt for safety warning

        Args:
            command: The dangerous command
            description: Description of what the command will do
            system_prompt: Character system prompt
            language: Language code

        Returns:
            Safety warning prompt
        """
        return self.build_prompt(
            user_input=command,
            system_prompt=system_prompt,
            context=None,
            scenario="safety_check",
            language=language,
            command=command,
            description=description,
        )

    def build_clarification_prompt(
        self,
        user_input: str,
        system_prompt: str,
        context: Optional[str] = None,
        language: str = "en",
    ) -> str:
        """
        Build a prompt for asking clarification

        Args:
            user_input: Unclear user input
            system_prompt: Character system prompt
            context: Optional conversation context
            language: Language code

        Returns:
            Clarification prompt
        """
        return self.build_prompt(
            user_input=user_input,
            system_prompt=system_prompt,
            context=context,
            scenario="clarification_needed",
            language=language,
            user_input=user_input,
        )

    def build_error_prompt(
        self,
        error: str,
        system_prompt: str,
        language: str = "en",
    ) -> str:
        """
        Build a prompt for error response

        Args:
            error: Error description
            system_prompt: Character system prompt
            language: Language code

        Returns:
            Error response prompt
        """
        return self.build_prompt(
            user_input=f"Error occurred: {error}",
            system_prompt=system_prompt,
            context=None,
            scenario="error_response",
            language=language,
            error=error,
        )

    def _get_scenario_template(
        self,
        scenario: str,
        language: str,
        **kwargs
    ) -> Optional[str]:
        """
        Get the template for a specific scenario

        Args:
            scenario: Scenario name
            language: Language code
            **kwargs: Template variables

        Returns:
            Formatted template text or None
        """
        # Get scenario-specific template from system_prompts
        scenario_templates = self.system_prompts.get(scenario, {})

        if not scenario_templates:
            return None

        template_text = scenario_templates.get(language)

        if not template_text:
            logger.warning(f"No template for scenario '{scenario}' in language '{language}'")
            # Fallback to English
            template_text = scenario_templates.get("en")

        if not template_text:
            return None

        # Format template with provided variables
        try:
            template = Template(template_text)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            return template_text

    def get_safety_warning(
        self,
        operation_type: str,
        language: str = "en",
        **kwargs
    ) -> Optional[str]:
        """
        Get a safety warning for a specific operation type

        Args:
            operation_type: Type of operation (file_deletion, system_power, etc.)
            language: Language code
            **kwargs: Template variables (e.g., target, action)

        Returns:
            Formatted safety warning or None
        """
        operations = self.safety_prompts.get("dangerous_operations", {})
        operation = operations.get(operation_type)

        if not operation:
            logger.warning(f"No safety warning for operation: {operation_type}")
            return None

        lang_config = operation.get(language, operation.get("en"))

        if not lang_config:
            return None

        warning = lang_config.get("warning", "")
        prompt = lang_config.get("prompt", "")

        # Format with variables
        try:
            warning = warning.format(**kwargs)
            prompt = prompt.format(**kwargs)
            return f"{warning}\n{prompt}"
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return f"{warning}\n{prompt}"

    def format_context(self, context: str, max_length: int = 500) -> str:
        """
        Format and truncate context if needed

        Args:
            context: Raw context text
            max_length: Maximum character length

        Returns:
            Formatted context
        """
        if not context:
            return ""

        if len(context) > max_length:
            logger.debug(f"Truncating context from {len(context)} to {max_length} chars")
            context = "..." + context[-(max_length - 3):]

        return context

    def build_simple_prompt(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        """
        Build a simple prompt without scenario or context

        Args:
            system_prompt: System instructions
            user_message: User's message

        Returns:
            Simple prompt
        """
        return f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"


if __name__ == "__main__":
    # Test the prompt builder
    logging.basicConfig(level=logging.INFO)

    prompts_dir = "/home/user/jarvis_manager/services/llm_service/prompts"
    builder = PromptBuilder(prompts_dir)

    # Test chat prompt
    system_prompt = "You are Gerald, a helpful assistant."
    user_input = "Hello, who are you?"
    context = "User: Hi\nAssistant: Gerald at your service."

    prompt = builder.build_chat_prompt(user_input, system_prompt, context)
    print("Chat Prompt:")
    print(prompt)
    print("\n" + "="*50 + "\n")

    # Test safety warning
    warning = builder.get_safety_warning(
        "file_deletion",
        language="en",
        target="/important/file.txt"
    )
    print("Safety Warning:")
    print(warning)

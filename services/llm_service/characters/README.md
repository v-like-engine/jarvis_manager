# Character System

This directory contains character personality configurations for the Jarvis LLM service.

## Overview

Characters define the personality, communication style, and behavioral patterns for the virtual assistant. Each character is defined in a YAML file with specific prompts, traits, and settings.

## Current Characters

- **Gerald** (`gerald.yaml`) - The default character. A loyal, strict knight who protects the system. Direct, authoritative, and helpful but not overly polite.

## Creating a New Character

To add a new character:

1. **Copy the template**: Start with `character_base.yaml` as your template
2. **Create new file**: Name it `your_character_name.yaml`
3. **Define personality**: Fill in all personality traits and communication style
4. **Write prompts**: Create system prompts for each supported language
5. **Add templates**: Define greeting, confirmation, refusal, and other templates
6. **Set voice settings**: Configure TTS parameters for the character's voice
7. **Test**: Use the character manager to load and test your character

## Character Structure

### Required Fields

- `name`: Character name (string)
- `version`: Semantic version (e.g., "1.0.0")
- `description`: Brief character description
- `language_support`: List of supported language codes
- `personality`: Complete personality definition
- `prompts`: System prompts and templates for all supported languages
- `response_rules`: Generation parameters and constraints

### Optional Fields

- `voice_settings`: TTS configuration per language
- `emotions`: Emotional state variations
- `metadata`: Author, creation date, tags

## Personality Traits

Choose traits that define your character's behavior:
- **Communication**: friendly, formal, casual, direct, verbose, concise
- **Attitude**: helpful, strict, playful, serious, patient, impatient
- **Expertise**: technical, simple, professional, educational
- **Emotion**: warm, cold, enthusiastic, calm, stern

## Response Rules

Configure how the character generates responses:

```yaml
response_rules:
  max_length: 150                    # Maximum words in response
  max_tokens: 150                    # Maximum tokens to generate
  require_context: true              # Use conversation history
  context_window: 5                  # Last N exchanges to remember
  temperature: 0.7                   # Creativity (0.0-1.0)
  top_p: 0.9                        # Diversity
  repetition_penalty: 1.1            # Avoid repetition
  prefer_short_responses: false      # Favor brevity
  use_templates_when_possible: true  # Use predefined templates
```

## Multi-Language Support

For each language you support, provide:
- System prompt (`system_<lang>`)
- Greeting templates (`greeting_<lang>`)
- Confirmation templates (`confirmation_<lang>`)
- Safety warnings (`safety_warning_<lang>`)
- Refusal phrases (`refusal_<lang>`)
- Clarification requests (`clarification_<lang>`)
- Error messages (`error_<lang>`)
- Self-description (`self_description_<lang>`)

## Example: Creating a "Friendly Helper" Character

```yaml
name: "Buddy"
version: "1.0.0"
description: "A friendly and enthusiastic helper"

personality:
  archetype: "Friendly Assistant"
  traits:
    - friendly
    - enthusiastic
    - patient
    - encouraging
  communication_style:
    verbosity: medium
    formality: low
    humor: playful
    patience: high
    politeness: high

prompts:
  system_en: |
    You are Buddy, a friendly and enthusiastic virtual assistant.
    You love helping people and always stay positive.
    You explain things clearly and encourage users.
    Use a warm, conversational tone.

  greeting_en:
    - "Hey there! I'm Buddy, ready to help!"
    - "Hi! What can I do for you today?"
    - "Hello! Buddy here, at your service!"
```

## Testing Characters

After creating a character:

1. Load it using the character manager
2. Test various scenarios (greetings, commands, errors)
3. Verify responses match the intended personality
4. Test in all supported languages
5. Check response length and timing

## Best Practices

1. **Be Consistent**: Maintain personality across all prompts and templates
2. **Be Brief**: Keep system prompts concise and clear
3. **Provide Variety**: Offer multiple template options for natural variation
4. **Consider Context**: Design prompts that work with conversation history
5. **Test Thoroughly**: Verify character behavior in different scenarios
6. **Document Well**: Add clear descriptions and metadata

## Integration

Characters are automatically loaded by the `CharacterManager` from this directory. To use a character:

```python
# Via API
POST /llm/set_character
{
    "character": "gerald"
}

# Via Python
character_manager.load_character("gerald")
```

## Voice Settings

Voice settings are used by the ASR service (Agent 1) for text-to-speech:

```yaml
voice_settings:
  en:
    rate: 180      # Words per minute (140-200 typical)
    volume: 0.9    # 0.0 to 1.0
    pitch: 0.8     # 0.5 (low) to 1.5 (high)
    voice_id: "male_1"  # TTS engine voice ID
    emphasis: medium    # Emphasis on important words
```

## Emotional States

Define emotional variations for different contexts:

```yaml
emotions:
  neutral:
    description: "Standard tone"
    temperature: 0.7

  excited:
    description: "Enthusiastic tone"
    temperature: 0.85
    prompt_suffix: "Be enthusiastic and energetic!"

  serious:
    description: "Serious, focused tone"
    temperature: 0.5
    prompt_suffix: "Be serious and professional."
```

## Character Versioning

When updating a character:
1. Increment the version number
2. Document changes in git commit
3. Test backward compatibility
4. Consider migration path for existing conversations

---

For questions or issues, contact Agent 2 (LLM Service) maintainer.

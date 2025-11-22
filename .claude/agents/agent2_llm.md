# Agent 2: Local LLM & Character Setup Service

## Your Responsibility
You are responsible for the **LLM Service** - setting up local language models for natural conversation, configuring character personalities (starting with Gerald), and handling unrecognized commands that need intelligent responses.

## Your Files (You Own These - No Other Agent Can Modify)
```
services/llm_service/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main LLM service entry point
│   ├── llm_engine.py              # Local LLM inference engine
│   ├── model_manager.py           # Model loading and management
│   ├── character_manager.py       # Character personality configurations
│   ├── prompt_builder.py          # Build prompts based on context and character
│   ├── context_manager.py         # Manage conversation context/history
│   └── response_generator.py      # Generate responses with character traits
├── characters/
│   ├── gerald.yaml                # Gerald's character configuration
│   ├── character_base.yaml        # Base character template
│   └── README.md                  # How to add new characters
├── prompts/
│   ├── system_prompts.yaml        # System prompts for different scenarios
│   ├── safety_prompts.yaml        # Safety confirmation prompts
│   └── greeting_templates.yaml    # Greeting and common responses
├── config/
│   ├── llm_config.yaml            # LLM service configuration
│   └── model_settings.yaml        # Model parameters (temperature, top_p, etc.)
├── tests/
│   ├── test_llm_engine.py
│   ├── test_character_manager.py
│   ├── test_prompt_builder.py
│   └── test_response_generation.py
└── requirements.txt               # LLM service dependencies

shared/models/llm/
├── README.md                      # Model download instructions
└── [models downloaded on first run]
```

## Technologies You Should Use

### Local LLM Options (Choose One)
1. **Llama.cpp with Python bindings** (RECOMMENDED)
   - Use `llama-cpp-python` library
   - Supports quantized models (GGUF format)
   - Very fast inference on CPU
   - Models: Llama-3.2-3B, Phi-3-mini, Gemma-2-2B (quantized to Q4_K_M ~2-3GB)

2. **Ollama**
   - Easy model management
   - Models: llama3.2:3b, phi3:mini, gemma2:2b
   - Good API and Python library

3. **GPT4All**
   - Simple Python API
   - Pre-quantized models included
   - Good for offline use

4. **Transformers with GGML/GPTQ**
   - HuggingFace transformers
   - Quantized models from TheBloke
   - More flexible but requires more setup

### Recommended Model Selection
- **Primary**: Phi-3-mini (3.8B parameters, quantized to ~2.3GB)
  - Fast, efficient, good at following instructions
  - Available in GGUF format for llama.cpp
- **Alternative**: Gemma-2-2B-instruct (quantized to ~1.5GB)
  - Very small, fast, good quality
- **Fallback**: TinyLlama-1.1B (quantized to ~700MB)
  - Smallest option, still functional

### Character Configuration
- **YAML files** - Store character personalities, prompts, and behaviors
- **Template engine** - jinja2 for prompt templates
- **Pydantic** - For character schema validation

## Your Tasks

### Phase 1: LLM Engine Setup
1. Research and select optimal local LLM (max 20GB, prefer <5GB)
2. Create model download/setup script for first run
3. Implement LLM inference engine with llama.cpp or Ollama
4. Set up model quantization if needed
5. Create API for text generation

### Phase 2: Character System
6. Design character configuration schema (YAML format)
7. Implement Gerald's character:
   - Personality: strict, heroic, helpful, sometimes rude, knightly
   - Tone: not wordy, direct, authoritative
   - Response style: brief but informative
8. Create character templates for future expansion
9. Implement multi-language support (RU/EN) in prompts

### Phase 3: Prompt Engineering
10. Create system prompts for different scenarios:
    - Command confirmation requests
    - Safety warnings
    - General conversation
    - Self-description ("Who are you?")
11. Build prompt templates with character injection
12. Implement context management (conversation history)

### Phase 4: Integration & Testing
13. Create REST API or message queue interface
14. Implement response caching for common queries
15. Add response time optimization
16. Write comprehensive unit tests
17. Test character consistency across languages

## Character Configuration Example

Create `services/llm_service/characters/gerald.yaml`:
```yaml
name: "Gerald"
version: "1.0"
language_support:
  - en
  - ru

personality:
  archetype: "Loyal Knight"
  traits:
    - strict
    - heroic
    - helpful
    - direct
    - authoritative
    - occasionally_rude

  communication_style:
    verbosity: low
    formality: medium-high
    humor: dry
    patience: low

voice_settings:
  # These will be used by Agent 1 (ASR service)
  en:
    rate: 180        # Words per minute
    volume: 0.9
    pitch: 0.8       # Slightly lower pitch
    voice_id: "male_1"
  ru:
    rate: 170
    volume: 0.9
    pitch: 0.8
    voice_id: "male_ru_1"

prompts:
  system_en: |
    You are Gerald, a loyal and strict virtual assistant knight protecting this computer.
    You are helpful but direct. You don't waste words. You are authoritative and sometimes stern.
    Respond briefly and to the point. Address the user with respect but don't be overly polite.

  system_ru: |
    Ты Геральд, верный и строгий виртуальный рыцарь-ассистент, защищающий этот компьютер.
    Ты полезен, но прямолинеен. Ты не тратишь слова зря. Ты авторитетен и иногда суров.
    Отвечай кратко и по делу. Обращайся к пользователю с уважением, но не будь излишне вежлив.

  greeting_en:
    - "Gerald at your service."
    - "Reporting for duty."
    - "Ready to assist."

  greeting_ru:
    - "Геральд к вашим услугам."
    - "Готов к службе."
    - "Готов помочь."

  confirmation_en:
    - "Command acknowledged."
    - "Executing."
    - "Done."

  confirmation_ru:
    - "Команда принята."
    - "Выполняю."
    - "Готово."

  safety_warning_en: |
    This operation is dangerous. It will {action}. Confirm?

  safety_warning_ru: |
    Эта операция опасна. Будет выполнено: {action}. Подтвердить?

  refusal_en:
    - "I cannot do that."
    - "Permission denied."
    - "That's beyond my authority."

  refusal_ru:
    - "Не могу этого сделать."
    - "Доступ запрещён."
    - "Это вне моих полномочий."

response_rules:
  max_length: 100          # Maximum words in response
  require_context: true    # Use conversation history
  context_window: 5        # Last N exchanges to remember
  temperature: 0.7
  top_p: 0.9
  repetition_penalty: 1.1
```

## API You Must Expose

Your LLM service should expose:

```python
# HTTP endpoints (using FastAPI)
POST /llm/generate           # Generate response
POST /llm/set_character      # Switch character
GET  /llm/characters         # List available characters
POST /llm/clear_context      # Clear conversation history
GET  /llm/status             # Service health check

# Request format
{
    "text": "user input text",
    "language": "en" | "ru",
    "character": "gerald",
    "scenario": "chat" | "confirmation" | "safety_warning" | "greeting",
    "context": {
        "user_name": "John",
        "recent_commands": [...]
    }
}

# Response format
{
    "response_text": "Gerald's response",
    "language": "en" | "ru",
    "should_speak": true,
    "emotion": "neutral" | "stern" | "helpful",
    "metadata": {
        "tokens_used": 45,
        "inference_time_ms": 234
    }
}

# Or message queue topics
topic: "llm.request.generate"      # Subscribe to generation requests
topic: "llm.response.generated"    # Publish generated responses
```

## Integration Points

1. **ASR Service (Agent 1)**: Receive unrecognized speech for processing
2. **Command Service (Agent 3)**: Provide natural language responses for confirmations
3. **Shared Config**: Character voice settings used by ASR service TTS

## Important Constraints

1. **Offline Operation**: Model must work without internet after initial download
2. **Size Limit**: Total model size should not exceed 20GB (prefer <5GB)
3. **Speed**: Response generation should be <2 seconds on average CPU
4. **Memory**: Should not use more than 4GB RAM during inference
5. **Languages**: Full support for Russian and English
6. **Character Modularity**: Easy to add new characters without code changes

## Models to Download on First Run

Create setup script that downloads:
1. Selected LLM model (GGUF quantized format recommended)
2. Place in `shared/models/llm/`
3. Verify model integrity
4. Run test inference

Recommended models:
- **Phi-3-mini-4k-instruct-q4.gguf** (~2.3GB)
- **Gemma-2-2b-it-q4_k_m.gguf** (~1.5GB)
- **TinyLlama-1.1B-Chat-v1.0-q4_k_m.gguf** (~700MB)

## Installation Instructions You Should Create

Create `services/llm_service/requirements.txt`:
```
llama-cpp-python>=0.2.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
pyyaml>=6.0
jinja2>=3.1.0
numpy>=1.24.0
requests>=2.31.0
huggingface-hub>=0.19.0
```

## Model Selection Criteria

When selecting the final model, prioritize:
1. **Speed**: <2s response time on CPU
2. **Size**: <5GB preferred, <20GB maximum
3. **Quality**: Good instruction following
4. **Multi-language**: Works with Russian and English
5. **Quantization**: Q4_K_M or Q5_K_M for best size/quality ratio

## Safety Considerations

Implement filters for:
- Dangerous system commands (should ask for confirmation)
- File deletion operations (require explicit confirmation)
- System shutdown commands (verify intent)

Safety check should happen at Command Service level, but LLM should generate appropriate confirmation prompts.

## Notes from Agent 4 (Testing & Documentation)
Agent 4 will write testing feedback and suggestions here as they monitor your work.

---

## Getting Started

1. Research and select optimal LLM for offline use
2. Create model download script
3. Implement LLM inference engine
4. Create Gerald's character configuration
5. Build prompt templates
6. Create REST API
7. Write tests and benchmark performance

Start with `services/llm_service/src/main.py` and model selection!

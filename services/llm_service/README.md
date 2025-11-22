# Jarvis LLM Service

**Agent 2 - Local Language Model and Character Personality Management**

A production-ready LLM service for natural conversation with character personalities, starting with Gerald the loyal knight assistant.

## Overview

The LLM Service provides:
- **Local LLM inference** using llama.cpp (offline capable)
- **Character personality system** with Gerald as the default character
- **Bilingual support** (English and Russian)
- **Conversation context management** (last 5 exchanges)
- **Prompt engineering** with scenario-specific templates
- **REST API** for integration with other services
- **Safety features** for dangerous commands

## Quick Start

### 1. Install Dependencies

```bash
cd /home/user/jarvis_manager/services/llm_service
pip install -r requirements.txt
```

**Note**: `llama-cpp-python` compilation may take several minutes on first install.

### 2. Download the Model

The model will auto-download on first run, or you can download manually:

```bash
cd /home/user/jarvis_manager/shared/models/llm
python download_model.py
```

This downloads **Phi-3-mini-4k-instruct** (~2.3GB) from HuggingFace.

### 3. Start the Service

```bash
cd /home/user/jarvis_manager/services/llm_service/src
python main.py
```

The service will start on `http://0.0.0.0:8002`

## Model Selection

**Selected Model: Phi-3-mini-4k-instruct (Q4_K_M)**

### Why Phi-3-mini?

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Size | ⭐⭐⭐⭐⭐ | 2.3GB (well under 5GB limit) |
| Speed | ⭐⭐⭐⭐ | 10-25 tok/s on CPU |
| Quality | ⭐⭐⭐⭐⭐ | Excellent instruction following |
| Multi-language | ⭐⭐⭐⭐⭐ | Strong EN/RU support |
| Memory | ⭐⭐⭐⭐ | 3-4GB during inference |

### Performance Benchmarks

**Hardware**: Average CPU (Intel i5/AMD Ryzen 5)

- **Response time**: 1-3 seconds (typical response)
- **Throughput**: 10-25 tokens/second
- **Memory usage**: 3-4GB RAM
- **Startup time**: 2-5 seconds
- **Context window**: 4096 tokens

## Architecture

### Components

```
services/llm_service/
├── src/
│   ├── main.py                    # FastAPI REST API entry point
│   ├── model_manager.py           # Model download and loading
│   ├── llm_engine.py              # llama.cpp inference engine
│   ├── character_manager.py       # Character personality management
│   ├── prompt_builder.py          # Prompt construction
│   ├── context_manager.py         # Conversation history
│   └── response_generator.py      # Response generation coordinator
├── characters/
│   ├── gerald.yaml                # Gerald's character config
│   ├── character_base.yaml        # Template for new characters
│   └── README.md                  # Character system guide
├── prompts/
│   ├── system_prompts.yaml        # Scenario templates
│   ├── safety_prompts.yaml        # Safety warnings
│   └── greeting_templates.yaml    # Common responses
├── config/
│   ├── llm_config.yaml            # Service configuration
│   └── model_settings.yaml        # LLM parameters
└── tests/
    ├── test_character_manager.py
    ├── test_context_manager.py
    ├── test_prompt_builder.py
    └── test_llm_engine.py
```

### Data Flow

```
User Input → REST API → Character Manager → Prompt Builder → LLM Engine → Response
                ↓                                                              ↓
          Context Manager ←──────────────────────────────────────────────────┘
```

## Gerald - The Default Character

### Personality

**Archetype**: Loyal Knight

**Traits**:
- Strict and direct
- Heroic and protective
- Helpful but authoritative
- Occasionally stern
- Low verbosity (brief responses)

### Example Interactions

**English**:
```
User: "Hello, who are you?"
Gerald: "Gerald at your service. I protect this system and help you with commands."

User: "Delete all files"
Gerald: "Warning: This operation is dangerous. It will permanently delete data.
This action cannot be undone. Confirm to proceed, or cancel."
```

**Russian**:
```
User: "Привет, кто ты?"
Gerald: "Геральд к вашим услугам. Я защищаю эту систему и помогаю с командами."

User: "Удали все файлы"
Gerald: "Внимание: Эта операция опасна. Будет удалена информация навсегда.
Это действие невозможно отменить. Подтвердите для продолжения или отмените."
```

## REST API

### Endpoints

#### POST /llm/generate
Generate a response to user input

**Request**:
```json
{
    "text": "Hello, who are you?",
    "language": "en",
    "character": "gerald",
    "scenario": "chat",
    "session_id": "optional-session-id",
    "use_template": true
}
```

**Response**:
```json
{
    "response_text": "Gerald at your service.",
    "language": "en",
    "should_speak": true,
    "emotion": "neutral",
    "scenario": "chat",
    "metadata": {
        "tokens_used": 8,
        "inference_time_ms": 234,
        "from_template": true,
        "character": "Gerald"
    }
}
```

#### POST /llm/set_character
Switch to a different character

**Request**:
```json
{
    "character": "gerald",
    "language": "en",
    "emotion": "neutral"
}
```

#### GET /llm/characters
List all available characters

**Response**:
```json
{
    "characters": [
        {
            "name": "Gerald",
            "description": "A loyal and strict virtual assistant knight",
            "archetype": "Loyal Knight",
            "languages": ["en", "ru"]
        }
    ],
    "current_character": "Gerald"
}
```

#### POST /llm/clear_context
Clear conversation history

**Request**:
```json
{
    "session_id": "optional-session-id"
}
```

#### GET /llm/status
Service health check

**Response**:
```json
{
    "status": "operational",
    "service": "llm_service",
    "version": "1.0.0",
    "model_loaded": true,
    "character_loaded": true,
    "current_character": "Gerald",
    "available_characters": ["gerald"]
}
```

#### GET /llm/model_info
Get model information

### Response Scenarios

The service supports different response scenarios:

- **chat**: General conversation
- **confirmation**: Command confirmations
- **safety_warning**: Warnings for dangerous operations
- **greeting**: Initial greetings
- **clarification**: Requests for clarification
- **error**: Error messages
- **refusal**: Refusing unauthorized operations

## Configuration

### Service Configuration (`config/llm_config.yaml`)

```yaml
service:
  name: "jarvis_llm_service"
  port: 8002

  model:
    name: "phi-3-mini-4k-instruct"
    variant: "q4_k_m"
    repo_id: "microsoft/Phi-3-mini-4k-instruct-gguf"
    filename: "Phi-3-mini-4k-instruct-q4.gguf"
    auto_download: true

  default_character: "gerald"

  context:
    max_exchanges: 5
    max_tokens_per_exchange: 200
```

### Model Settings (`config/model_settings.yaml`)

```yaml
generation:
  temperature: 0.7        # Creativity (0.0-1.0)
  top_p: 0.9             # Nucleus sampling
  top_k: 40              # Top-k sampling
  repetition_penalty: 1.1 # Avoid repetition
  max_tokens: 150        # Max response length
```

## Character System

### Creating a New Character

1. Copy `characters/character_base.yaml`
2. Customize personality traits and prompts
3. Add to both English and Russian languages
4. Test with CharacterManager

### Character Structure

```yaml
name: "CharacterName"
personality:
  archetype: "Role"
  traits: [trait1, trait2]
  communication_style:
    verbosity: low|medium|high
    formality: low|medium|high
prompts:
  system_en: "System prompt in English..."
  system_ru: "System prompt in Russian..."
  greeting_en: ["Hello!", "Hi!"]
```

See `characters/README.md` for complete guide.

## Testing

### Run Unit Tests

```bash
cd /home/user/jarvis_manager/services/llm_service

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_character_manager.py

# Run with verbose output
pytest tests/ -v

# Skip slow tests (require model)
pytest tests/ -m "not slow"
```

### Test Coverage

- ✅ Character loading and management
- ✅ Context/history management
- ✅ Prompt building with templates
- ✅ LLM inference (requires model)
- ✅ Multi-language support
- ✅ Template responses

## Integration with Other Services

### Agent 1 (ASR Service)
- Receives unrecognized speech for processing
- Uses voice settings from character config for TTS

### Agent 3 (Command Service)
- Requests natural language confirmations
- Gets safety warnings for dangerous commands

## Safety Features

The service includes built-in safety checks:

1. **Dangerous Command Detection**: Pattern matching for risky operations
2. **Confirmation Requirements**: Explicit confirmation for destructive actions
3. **Safety Warnings**: Clear warnings with consequences
4. **Multi-level Safety**: Low, medium, high, critical levels

Example dangerous patterns:
- `rm -rf`: File deletion (high safety)
- `format`: Disk formatting (critical safety)
- `shutdown`: System power (medium safety)

## Troubleshooting

### Model Download Fails

```bash
# Check internet
ping huggingface.co

# Manual download
cd /home/user/jarvis_manager/shared/models/llm
python download_model.py
```

### Service Won't Start

1. Check model is downloaded: `ls shared/models/llm/*.gguf`
2. Check dependencies: `pip install -r requirements.txt`
3. Check logs: `logs/llm_service.log`
4. Verify configuration: `config/llm_config.yaml`

### Slow Response Times

1. Reduce `n_ctx` to 1024 in config
2. Increase `n_threads` to match CPU cores
3. Use smaller model (Gemma-2-2b or TinyLlama)
4. Check CPU usage during generation

### Out of Memory

1. Close other applications
2. Use smaller model
3. Reduce `n_ctx` (context window)
4. Check system has >8GB RAM

## Performance Optimization

### CPU Optimization

- Enable AVX2 instructions (2x speedup)
- Set `n_threads` to number of physical cores
- Use `use_mmap: true` for faster loading
- Increase `n_batch` for better throughput

### Memory Optimization

- Reduce `n_ctx` if not using long context
- Use Q4 quantization (current) or Q3 for smaller
- Disable `use_mlock` if low on RAM

### Response Quality

- Increase `temperature` for more creative responses
- Decrease `temperature` for more consistent responses
- Adjust `repetition_penalty` to avoid repetition
- Use `top_p` and `top_k` for response diversity

## Monitoring

### Logs

Service logs are written to:
- `/home/user/jarvis_manager/logs/llm_service.log`

### Metrics

Each response includes metadata:
- `tokens_used`: Number of tokens generated
- `inference_time_ms`: Generation time in milliseconds
- `from_template`: Whether response used a template

### Health Check

```bash
curl http://localhost:8002/llm/status
```

## Future Enhancements

Potential improvements:
1. Additional characters (technical expert, friendly companion)
2. Streaming responses for long generations
3. Response caching for common queries
4. GPU acceleration support
5. Model hot-swapping
6. Custom fine-tuned models
7. Emotion detection from user input
8. Personality adaptation over time

## Technical Details

### Technology Stack

- **LLM Framework**: llama.cpp (via llama-cpp-python)
- **Web Framework**: FastAPI
- **Model Format**: GGUF (quantized)
- **Quantization**: Q4_K_M (4-bit mixed precision)
- **Template Engine**: Jinja2
- **Configuration**: YAML
- **Validation**: Pydantic

### Model Format: GGUF

GGUF (GPT-Generated Unified Format) benefits:
- Efficient memory mapping
- Fast loading times
- Multiple quantization levels
- Cross-platform compatibility
- Optimized for llama.cpp

### Quantization: Q4_K_M

Q4_K_M quantization:
- 4-bit weights with K-quant (mixed precision)
- ~75% size reduction from FP16
- <3% quality degradation
- 2-3x faster inference
- Optimal quality/size balance

## License

Part of the Jarvis voice assistant system.
See main project LICENSE file.

## Credits

- **Model**: Phi-3-mini by Microsoft
- **Inference**: llama.cpp by Georgi Gerganov
- **Python Bindings**: llama-cpp-python by Andrei Betlen
- **Character Design**: Agent 2 (LLM Service)

## Support

For issues or questions:
1. Check this README
2. Review logs in `/home/user/jarvis_manager/logs/`
3. Run tests: `pytest tests/ -v`
4. Check model documentation
5. Contact Agent 2 maintainer

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
**Agent**: 2 - LLM Service
**Status**: Production Ready ✅

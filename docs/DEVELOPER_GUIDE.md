# Gerald Desktop Manager - Developer Guide

Guide for developers who want to contribute to or extend Gerald v1.0.0

## Table of Contents
1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Adding New Features](#adding-new-features)
5. [Testing Guidelines](#testing-guidelines)
6. [Code Style](#code-style)
7. [Documentation](#documentation)
8. [Agent-Based Development](#agent-based-development)
9. [Debugging](#debugging)
10. [Performance Optimization](#performance-optimization)

---

## Development Setup

### Prerequisites

- **Python**: 3.10+ (3.11 recommended)
- **Git**: For version control
- **IDE**: VS Code, PyCharm, or similar
- **Windows 10/11**: For testing (primary platform)

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/gerald-desktop-manager.git
cd gerald-desktop-manager

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux (future)

# Install all dependencies
pip install -r services/asr_service/requirements.txt
pip install -r services/llm_service/requirements.txt
pip install -r services/command_service/requirements.txt
pip install -r tests/requirements.txt

# Install development tools
pip install black flake8 mypy pylint pytest-cov
```

### Download Models

```bash
python setup_models.py
```

### Run in Development Mode

```bash
# Start all services with hot reload
python run_gerald.py --dev

# Or start services individually
python -m services.asr_service.src.main --reload
python -m services.llm_service.src.main --reload
python -m services.command_service.src.main --reload
```

---

## Project Structure

```
gerald-desktop-manager/
├── .claude/
│   └── agents/              # Agent-specific development docs
│       ├── agent1_asr.md
│       ├── agent2_llm.md
│       ├── agent3_commands.md
│       └── agent4_testing.md
│
├── services/
│   ├── asr_service/         # Agent 1: Speech, TTS, Recognition
│   │   ├── src/
│   │   │   ├── main.py                  # FastAPI service
│   │   │   ├── audio_capture.py         # Microphone input
│   │   │   ├── vad.py                   # Voice Activity Detection
│   │   │   ├── speech_recognition.py    # Vosk ASR
│   │   │   ├── command_parser.py        # Parse commands
│   │   │   ├── tts_engine.py            # Text-to-Speech
│   │   │   ├── face_recognition.py      # Face ID
│   │   │   └── voice_biometrics.py      # Voice ID
│   │   ├── config/
│   │   │   └── asr_config.yaml
│   │   ├── tests/
│   │   │   └── test_*.py
│   │   └── requirements.txt
│   │
│   ├── llm_service/         # Agent 2: Language Model
│   │   ├── src/
│   │   │   ├── main.py                  # FastAPI service
│   │   │   ├── llm_engine.py            # LLM inference
│   │   │   ├── prompt_builder.py        # Prompt templates
│   │   │   ├── character_loader.py      # Load characters
│   │   │   └── safety_validator.py      # Safety checks
│   │   ├── characters/
│   │   │   ├── gerald.yaml
│   │   │   └── ...
│   │   ├── prompts/
│   │   │   ├── system_prompts.yaml
│   │   │   └── safety_prompts.yaml
│   │   ├── config/
│   │   ├── tests/
│   │   └── requirements.txt
│   │
│   └── command_service/     # Agent 3: Command Execution
│       ├── src/
│       │   ├── main.py
│       │   ├── command_router.py
│       │   └── safety_checker.py
│       ├── modules/
│       │   ├── app_launcher/
│       │   ├── file_ops/
│       │   ├── terminal/
│       │   ├── music_control/
│       │   └── settings/
│       ├── config/
│       ├── tests/
│       └── requirements.txt
│
├── shared/
│   ├── models/              # Downloaded AI models
│   │   ├── asr/
│   │   ├── llm/
│   │   ├── face/
│   │   └── voice/
│   ├── utils/               # Shared utilities
│   │   ├── logger.py
│   │   ├── config_loader.py
│   │   └── validators.py
│   └── user_data.db         # User enrollment database
│
├── tests/                   # Agent 4: Integration Tests
│   ├── integration/
│   ├── performance/
│   ├── safety/
│   ├── fixtures/
│   └── requirements.txt
│
├── docs/                    # Agent 4: Documentation
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── COMMANDS.md
│   ├── API_REFERENCE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── CONTRIBUTING.md
│
├── config/
│   ├── main_config.yaml     # Main configuration
│   ├── services.yaml        # Service orchestration
│   └── logging_config.yaml  # Logging setup
│
├── logs/                    # Runtime logs
├── run_gerald.py            # Main launcher
├── setup_models.py          # Model downloader
├── README.md
└── requirements.txt         # Global dependencies
```

---

## Development Workflow

### Branching Strategy

```bash
# Main branches
main            # Stable releases
develop         # Development branch

# Feature branches
feature/new-command-type
feature/gpu-acceleration
fix/memory-leak
docs/api-updates
```

### Making Changes

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes
# ... edit files ...

# Test changes
pytest tests/
pytest services/asr_service/tests/
pytest services/llm_service/tests/
pytest services/command_service/tests/

# Format code
black .
flake8 .

# Commit
git add .
git commit -m "Add new feature: XYZ"

# Push and create PR
git push origin feature/my-new-feature
```

### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Run full test suite
4. Update documentation
5. Create PR with description
6. Request review
7. Address feedback
8. Merge to develop

---

## Adding New Features

### Adding a New Voice Command

**Example**: Add "Open Incognito Browser" command

#### 1. Update Command Parser (ASR Service)

Edit `services/asr_service/src/command_parser.py`:

```python
COMMAND_PATTERNS = {
    # Existing patterns...

    "app_launch_incognito": {
        "en": [
            r"open incognito",
            r"launch private (?:browsing|mode)",
            r"start incognito (?:mode|window)"
        ],
        "ru": [
            r"открой инкогнито",
            r"запусти приватный режим"
        ]
    }
}

def parse_command(text: str, language: str) -> Dict:
    # ... existing code ...

    # Add new intent handling
    if match_pattern(text, "app_launch_incognito", language):
        return {
            "intent": "app_launch_incognito",
            "params": {
                "mode": "incognito"
            },
            "confidence": 0.95
        }
```

#### 2. Add Safety Check (LLM Service)

Edit `services/llm_service/prompts/safety_prompts.yaml`:

```yaml
app_launch_incognito:
  is_safe: true
  requires_confirmation: false
  explanation: "Launching browser in incognito mode is safe"
```

#### 3. Implement Command Executor (Command Service)

Edit `services/command_service/modules/app_launcher/launcher.py`:

```python
def launch_app_incognito(app_name: str = "chrome") -> Dict:
    """Launch browser in incognito mode"""

    # Chrome
    if "chrome" in app_name.lower():
        path = find_app_path("chrome.exe")
        process = subprocess.Popen([path, "--incognito"])
        return {
            "success": True,
            "app": "Chrome Incognito",
            "process_id": process.pid
        }

    # Firefox
    elif "firefox" in app_name.lower():
        path = find_app_path("firefox.exe")
        process = subprocess.Popen([path, "-private-window"])
        return {
            "success": True,
            "app": "Firefox Private",
            "process_id": process.pid
        }

    else:
        return {"success": False, "error": "Incognito not supported for this browser"}
```

#### 4. Add to Command Router

Edit `services/command_service/src/command_router.py`:

```python
from modules.app_launcher import launcher

async def route_command(intent: str, params: Dict) -> Dict:
    # ... existing routing ...

    if intent == "app_launch_incognito":
        return launcher.launch_app_incognito(
            app_name=params.get("app", "chrome")
        )
```

#### 5. Write Tests

Create `tests/integration/test_incognito_launch.py`:

```python
import pytest
from services.command_service.modules.app_launcher import launcher

def test_launch_chrome_incognito():
    """Test launching Chrome in incognito mode"""
    result = launcher.launch_app_incognito("chrome")

    assert result["success"] == True
    assert "Chrome Incognito" in result["app"]
    assert result["process_id"] > 0

def test_launch_firefox_private():
    """Test launching Firefox in private mode"""
    result = launcher.launch_app_incognito("firefox")

    assert result["success"] == True
    assert "Firefox Private" in result["app"]
```

#### 6. Update Documentation

Add to `docs/COMMANDS.md`:

```markdown
### Incognito Mode

| English Command | Russian Command | Action |
|----------------|-----------------|--------|
| Open incognito | Открой инкогнито | Launch browser in incognito mode |
| Launch private mode | Запусти приватный режим | Launch browser in private mode |
```

#### 7. Run Tests

```bash
pytest tests/integration/test_incognito_launch.py
pytest services/command_service/tests/
```

---

### Adding a New Character

**Example**: Add "Jarvis" character

#### 1. Create Character Configuration

Create `services/llm_service/characters/jarvis.yaml`:

```yaml
name: "Jarvis"
archetype: "Witty Butler"
personality:
  traits:
    - witty
    - polite
    - sophisticated
    - helpful
  communication_style: "Polished and articulate with subtle humor"

voice_settings:
  pitch: 0.6       # Higher pitch than Gerald
  rate: 200        # Slightly faster
  volume: 0.9

system_prompt: |
  You are Jarvis, a sophisticated AI butler in the style of Tony Stark's Jarvis.
  You are polite, witty, and always professional. You address the user as "Sir" or "Madam".
  Your responses are articulate and often include subtle humor.

  Examples:
  - "Certainly, sir. Chrome is now at your disposal."
  - "As you wish. Shutting down the calculator."
  - "I'm afraid I can't do that, sir. That command would be quite destructive."

response_templates:
  confirmation:
    en: "Certainly, {action_description}"
    ru: "Конечно, {action_description}"

  error:
    en: "My apologies, sir. {error_reason}"
    ru: "Прошу прощения, {error_reason}"
```

#### 2. Test Character

```bash
curl -X POST http://localhost:8002/set_character \
  -H "Content-Type: application/json" \
  -d '{"character_name":"jarvis"}'
```

#### 3. Document

Update `docs/USER_GUIDE.md` and `docs/API_REFERENCE.md`

---

### Adding a New LLM Model

**Example**: Support Llama-3-8B

#### 1. Add Model Download

Edit `setup_models.py`:

```python
LLM_MODELS = {
    "phi-3-mini": {...},
    "gemma-2-2b": {...},
    "llama-3-8b": {  # New
        "url": "https://huggingface.co/...",
        "size_gb": 5.0,
        "quantization": "Q4_K_M"
    }
}
```

#### 2. Update LLM Engine

Edit `services/llm_service/src/llm_engine.py`:

```python
SUPPORTED_MODELS = ["phi-3-mini", "gemma-2-2b", "llama-3-8b"]

def load_model(model_name: str):
    if model_name == "llama-3-8b":
        return Llama(
            model_path="shared/models/llm/llama-3-8b-q4.gguf",
            n_ctx=4096,  # Larger context
            n_threads=8
        )
```

#### 3. Add Configuration

Edit `config/main_config.yaml`:

```yaml
llm:
  model: "llama-3-8b"  # New option
```

#### 4. Document

Update `docs/ARCHITECTURE.md` and `docs/INSTALLATION.md`

---

## Testing Guidelines

### Unit Tests

Each service should have unit tests for all modules.

**Example**: Test command parser

```python
# services/asr_service/tests/test_command_parser.py
import pytest
from src.command_parser import parse_command

def test_parse_app_launch_english():
    result = parse_command("open chrome", "en")
    assert result["intent"] == "app_launch"
    assert "chrome" in result["params"]["app_name"].lower()

def test_parse_app_launch_russian():
    result = parse_command("открой chrome", "ru")
    assert result["intent"] == "app_launch"

def test_parse_invalid_command():
    result = parse_command("xyz nonsense", "en")
    assert result["intent"] == "unknown"
```

Run tests:
```bash
pytest services/asr_service/tests/
```

### Integration Tests

Test communication between services.

**Example**: Test full pipeline

```python
# tests/integration/test_full_pipeline.py
import pytest
from tests.fixtures import start_all_services, stop_all_services

@pytest.fixture(scope="module")
def services():
    start_all_services()
    yield
    stop_all_services()

def test_full_command_flow(services):
    """Test: Voice command → App launch → Confirmation"""

    # 1. ASR recognizes
    asr_result = asr_client.recognize(audio_sample("open_chrome.wav"))
    assert asr_result["text"] == "open chrome"

    # 2. LLM validates
    llm_result = llm_client.safety_check("app_launch", {"app": "chrome"})
    assert llm_result["is_safe"] == True

    # 3. Command executes
    cmd_result = command_client.execute("app_launch", {"app": "chrome"})
    assert cmd_result["success"] == True
```

### Performance Tests

Ensure Gerald meets performance targets.

```python
# tests/performance/test_cpu_usage.py
import pytest
import psutil
import time

def test_cpu_usage_idle():
    """Test: CPU usage <5% when idle"""

    # Let system stabilize
    time.sleep(5)

    # Measure CPU for 30 seconds
    cpu_samples = []
    for _ in range(30):
        cpu_samples.append(psutil.cpu_percent(interval=1))

    avg_cpu = sum(cpu_samples) / len(cpu_samples)
    assert avg_cpu < 5.0, f"CPU usage too high: {avg_cpu}%"
```

### Safety Tests

Verify dangerous operations are blocked.

```python
# tests/safety/test_safety_checker.py
import pytest

def test_forbidden_command_blocked():
    """Test: Format command is blocked"""

    result = safety_checker.check_command("format C:")
    assert result["blocked"] == True
    assert "damage" in result["reason"].lower()

def test_confirmation_required():
    """Test: File deletion requires confirmation"""

    result = safety_checker.check_command("delete file important.txt")
    assert result["requires_confirmation"] == True
```

---

## Code Style

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

```python
# Formatting
- Line length: 100 characters (not 79)
- Indentation: 4 spaces
- Imports: alphabetical, grouped (stdlib, third-party, local)

# Naming
- Functions: snake_case
- Classes: PascalCase
- Constants: UPPER_CASE
- Private: _leading_underscore
```

### Code Formatting

Use **Black** for automatic formatting:

```bash
black .
black services/asr_service/
```

### Linting

Use **flake8** and **pylint**:

```bash
flake8 .
pylint services/*/src/
```

### Type Hints

Use type hints for all functions:

```python
from typing import Dict, List, Optional

def parse_command(text: str, language: str) -> Dict[str, any]:
    """Parse voice command into intent and parameters"""
    ...

async def execute_command(intent: str, params: Dict) -> Optional[Dict]:
    """Execute parsed command"""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def launch_app(app_name: str, fuzzy_match: bool = True) -> Dict:
    """Launch an application by name.

    Args:
        app_name: Name of the application to launch
        fuzzy_match: Enable fuzzy string matching (default: True)

    Returns:
        Dictionary containing:
            - success: bool
            - app_name: str (full app name)
            - process_id: int

    Raises:
        AppNotFoundError: If application cannot be found

    Example:
        >>> launch_app("chrome")
        {"success": True, "app_name": "Google Chrome", "process_id": 12345}
    """
    ...
```

---

## Documentation

### Keeping Docs Updated

When adding features, update:

1. **Code docstrings** - Inline documentation
2. **API_REFERENCE.md** - If adding/changing APIs
3. **COMMANDS.md** - If adding voice commands
4. **USER_GUIDE.md** - User-facing features
5. **ARCHITECTURE.md** - Architectural changes
6. **CHANGELOG.md** - All changes

### Writing Good Documentation

- **Clear**: Avoid jargon, explain technical terms
- **Complete**: Include examples, edge cases
- **Concise**: Remove unnecessary words
- **Current**: Update with each change
- **Tested**: Verify code examples work

---

## Agent-Based Development

Gerald was built using 4 specialized agents:

### Agent 1: ASR Service
- **Files**: `services/asr_service/**`
- **Responsibilities**: Speech recognition, TTS, face/voice ID
- **Contact**: See `.claude/agents/agent1_asr.md`

### Agent 2: LLM Service
- **Files**: `services/llm_service/**`
- **Responsibilities**: LLM inference, character system
- **Contact**: See `.claude/agents/agent2_llm.md`

### Agent 3: Command Service
- **Files**: `services/command_service/**`
- **Responsibilities**: Command execution, app control
- **Contact**: See `.claude/agents/agent3_commands.md`

### Agent 4: Testing & Documentation
- **Files**: `tests/**`, `docs/**`
- **Responsibilities**: QA, integration tests, docs
- **Contact**: See `.claude/agents/agent4_testing.md`

### Cross-Agent Communication

If your change affects multiple services:

1. Read relevant agent docs in `.claude/agents/`
2. Coordinate changes across services
3. Update all affected tests
4. Document inter-service impacts

---

## Debugging

### Enable Debug Logging

Edit `config/main_config.yaml`:

```yaml
app:
  log_level: "DEBUG"  # Instead of INFO
```

Restart Gerald.

### View Real-Time Logs

```bash
# Windows
powershell Get-Content logs/asr_service.log -Wait
powershell Get-Content logs/llm_service.log -Wait
powershell Get-Content logs/command_service.log -Wait
```

### Debug Individual Services

Start service in debug mode with breakpoints:

```python
# services/asr_service/src/main.py
import pdb; pdb.set_trace()  # Breakpoint

# Or use IDE debugger
# VS Code: F5 with launch.json configured
```

### Common Issues

1. **Import errors**: Check `PYTHONPATH` includes project root
2. **Port conflicts**: Kill process on port 8001-8003
3. **Model not found**: Run `python setup_models.py`
4. **Permission denied**: Run as administrator

---

## Performance Optimization

### Profiling CPU

```bash
python -m cProfile -o profile.stats run_gerald.py
python -m pstats profile.stats
```

### Profiling Memory

```bash
python -m memory_profiler services/llm_service/src/main.py
```

### Optimization Checklist

- [ ] Use async/await for I/O operations
- [ ] Cache expensive computations
- [ ] Lazy load models
- [ ] Minimize LLM token count
- [ ] Optimize VAD processing interval
- [ ] Use memory-mapped file I/O for models
- [ ] Profile before and after changes

---

## Release Process

### Version Bump

1. Update version in:
   - `config/main_config.yaml`
   - `README.md`
   - All `docs/*.md` files

2. Create `CHANGELOG.md` entry

3. Tag release:
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

### Build Artifacts

```bash
# Package for distribution
python setup.py sdist bdist_wheel

# Create installer (Windows)
pyinstaller run_gerald.spec
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## Need Help?

- **GitHub Issues**: Report bugs, request features
- **Discord**: Join developer community (link TBD)
- **Docs**: Read all documentation in `docs/`

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
**Maintained by**: Agent 4 (Testing & Documentation)

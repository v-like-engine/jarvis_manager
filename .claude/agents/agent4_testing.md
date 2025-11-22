# Agent 4: Documentation, Testing & Quality Assurance

## Your Responsibility
You are the **Quality Guardian** - monitor all other agents' work, write comprehensive documentation, create tests for all functionality, identify issues, and provide feedback to other agents by writing notes in their claude.md files.

## Your Files (You Own These - No Other Agent Can Modify)
```
docs/
├── README.md                      # Main project documentation
├── ARCHITECTURE.md                # System architecture overview
├── INSTALLATION.md                # Installation guide
├── USER_GUIDE.md                  # End-user guide
├── DEVELOPER_GUIDE.md             # Developer documentation
├── API_REFERENCE.md               # API documentation for all services
├── COMMANDS.md                    # Complete list of voice commands
├── TROUBLESHOOTING.md             # Common issues and solutions
├── CHANGELOG.md                   # Version history
└── CONTRIBUTING.md                # Contribution guidelines

tests/
├── integration/
│   ├── __init__.py
│   ├── test_full_pipeline.py     # End-to-end tests
│   ├── test_service_communication.py
│   ├── test_command_flow.py
│   └── test_multilingual.py
├── performance/
│   ├── test_cpu_usage.py         # Performance benchmarks
│   ├── test_memory_usage.py
│   ├── test_response_time.py
│   └── test_concurrent_commands.py
├── safety/
│   ├── test_safety_checker.py
│   ├── test_dangerous_commands.py
│   └── test_confirmation_flow.py
└── fixtures/
    ├── audio_samples/             # Test audio files
    ├── mock_responses/            # Mock data for tests
    └── test_configs/              # Test configurations

config/
├── main_config.yaml               # Main application configuration
├── services.yaml                  # Service orchestration config
└── logging_config.yaml            # Logging configuration

# Root level files
├── README.md                      # Quick start guide
├── requirements.txt               # Global dependencies
├── setup.py or pyproject.toml     # Package configuration
├── docker-compose.yml             # Docker orchestration (optional)
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── run_gerald.py or run_gerald.bat # Main launcher script
```

## Your Role and Responsibilities

### 1. Monitoring Other Agents
- Continuously review code written by Agents 1, 2, and 3
- Identify bugs, performance issues, and design flaws
- Check for security vulnerabilities
- Verify adherence to requirements
- Ensure code quality and best practices

### 2. Providing Feedback
When you find issues, write notes in the respective agent's claude.md file:

**In `.claude/agents/agent1_asr.md`:**
```markdown
## Notes from Agent 4 (Testing & Documentation)

### Issue #1: High CPU Usage in VAD (2025-11-22)
**Severity**: High
**Location**: `services/asr_service/src/voice_detection.py:45`
**Problem**: VAD is processing audio every 10ms, causing 30% CPU usage even when silent.
**Solution**: Increase VAD processing interval to 100ms and add adaptive processing based on audio energy.
**Status**: Pending

### Issue #2: Missing Error Handling (2025-11-22)
**Severity**: Medium
**Location**: `services/asr_service/src/speech_recognition.py:78`
**Problem**: No exception handling for microphone disconnection.
**Solution**: Add try-except block and graceful degradation.
**Status**: Pending

### Feedback: Good Implementation (2025-11-22)
**Location**: `services/asr_service/src/command_parser.py`
**Note**: Excellent multilingual command parsing with clear separation of concerns. Well done!
```

### 3. Writing Tests
Create comprehensive test coverage:
- **Unit tests** for each module (each agent writes their own, you verify)
- **Integration tests** for service communication (your responsibility)
- **End-to-end tests** for complete workflows (your responsibility)
- **Performance tests** for efficiency requirements (your responsibility)
- **Safety tests** for security concerns (your responsibility)

### 4. Documentation
Write clear, comprehensive documentation:
- System architecture and design decisions
- Installation and setup instructions
- User guide with all voice commands
- Developer guide for future contributors
- API reference for all services
- Troubleshooting guide

### 5. Testing Execution
Actually run tests on implemented features:
- Test on Windows 10 and Windows 11 (if possible in environment)
- Test bilingual functionality (Russian and English)
- Test edge cases and error conditions
- Verify performance requirements
- Test safety mechanisms

## Technologies You Should Use

### Testing Frameworks
- **pytest** - Main testing framework
- **pytest-asyncio** - For async tests
- **pytest-cov** - Code coverage
- **pytest-mock** - Mocking
- **pytest-timeout** - Test timeouts

### Documentation
- **MkDocs** or **Sphinx** - Documentation generation (optional)
- **Markdown** - Primary documentation format
- **Mermaid** - Diagrams in markdown

### Quality Tools
- **black** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking
- **bandit** - Security linting
- **pylint** - Code analysis

### Performance Testing
- **pytest-benchmark** - Benchmarking
- **memory_profiler** - Memory profiling
- **psutil** - System resource monitoring

## Your Tasks

### Phase 1: Initial Setup & Monitoring
1. Create project README with overview
2. Set up testing infrastructure
3. Begin monitoring Agents 1, 2, 3 as they work
4. Create issue tracking template

### Phase 2: Documentation
5. Write ARCHITECTURE.md explaining microservice design
6. Create INSTALLATION.md with step-by-step setup
7. Write USER_GUIDE.md with all voice commands
8. Document API reference for all services
9. Create COMMANDS.md with bilingual command list
10. Write TROUBLESHOOTING.md

### Phase 3: Integration Testing
11. Create integration tests for ASR → LLM flow
12. Test ASR → Command Service flow
13. Test Command → LLM confirmation flow
14. Test full pipeline: voice input → execution → voice response
15. Test language switching functionality

### Phase 4: Performance & Safety Testing
16. Create CPU usage tests (must be efficient background task)
17. Create memory usage tests
18. Test response time for commands
19. Test safety checker with dangerous commands
20. Test confirmation flow for unsafe operations

### Phase 5: Quality Assurance
21. Review all code for bugs and improvements
22. Provide feedback to other agents
23. Verify all requirements are met
24. Create final test report
25. Write CHANGELOG.md

### Phase 6: End-to-End Validation
26. Test complete workflows:
    - "Open Yandex Browser" (English)
    - "Закрой Яндекс браузер" (Russian)
    - "Recognize me" → face detection
    - "Who are you?" → self-description
    - File operation with confirmation
    - Language switching
    - "Exit Gerald" → shutdown
27. Verify Windows 10/11 compatibility
28. Create demo video or GIF (if possible)

## Documentation Structure

### README.md (Root)
```markdown
# Gerald Desktop Manager

Voice-controlled desktop manager for Windows 10/11

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Download models: `python setup_models.py`
3. Run Gerald: `python run_gerald.py`

## Voice Commands
- "Open <app>" - Launch application
- "Close <app>" - Close application
- "Recognize me" - Face/voice recognition
- "Who are you?" - About Gerald
- "Exit Gerald" - Shutdown

See [COMMANDS.md](docs/COMMANDS.md) for full list.

## Documentation
- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)

## Requirements
- Windows 10/11
- Python 3.10+
- Microphone
- 8GB RAM minimum
- 25GB disk space (for models)
```

### ARCHITECTURE.md
Should include:
- System overview diagram
- Microservice architecture explanation
- Service communication protocols
- Data flow diagrams
- Technology stack for each service
- Offline-first design philosophy

### INSTALLATION.md
Should include:
- System requirements
- Python installation
- Dependency installation per service
- Model download and setup
- First-run configuration
- Startup configuration
- Troubleshooting installation issues

### USER_GUIDE.md
Should include:
- Introduction to Gerald
- How to start/stop Gerald
- Complete voice commands list (bilingual)
- Face/voice enrollment process
- Language switching
- Configuration options
- Privacy and data storage
- FAQ

### COMMANDS.md
Complete bilingual command reference:
```markdown
# Voice Commands Reference

## Application Control

### English
- "Open <app name>" - Launch application
- "Launch <app name>" - Launch application
- "Close <app name>" - Close application
- "Shut down <app name>" - Close application
- "Exit <app name>" - Close application

### Russian
- "Открой <имя приложения>" - Запустить приложение
- "Запусти <имя приложения>" - Запустить приложение
- "Закрой <имя приложения>" - Закрыть приложение

... (complete list)
```

### API_REFERENCE.md
Document all REST APIs and message queue topics for:
- ASR Service
- LLM Service
- Command Service

Include request/response examples, error codes, authentication (if any).

## Integration Test Examples

### Test: Full Command Pipeline
```python
import pytest
from tests.fixtures import mock_audio, mock_microphone

def test_full_pipeline_open_app_english():
    """
    Test: User says "Open Yandex Browser" in English
    Expected: App launches, Gerald confirms in English
    """
    # 1. Simulate audio input
    audio = mock_audio("open_yandex_browser_en.wav")

    # 2. ASR should recognize
    recognized = asr_service.recognize(audio)
    assert recognized.text == "open yandex browser"
    assert recognized.language == "en"

    # 3. Command parser should extract
    command = parse_command(recognized)
    assert command.type == "app_launch"
    assert "yandex" in command.params.app_name.lower()

    # 4. Command service should execute
    result = command_service.execute(command)
    assert result.success == True

    # 5. Response should be generated
    response = llm_service.generate_response(
        "app launched successfully",
        language="en",
        scenario="confirmation"
    )
    assert response.should_speak == True

    # 6. TTS should speak
    audio_response = tts_engine.speak(response.text, language="en")
    assert audio_response is not None

def test_full_pipeline_dangerous_command_russian():
    """
    Test: User says "Удали файл system.dll" (Delete file system.dll) in Russian
    Expected: Safety check triggers, Gerald asks for confirmation in Russian
    """
    # Similar structure testing safety flow
    pass
```

### Test: Performance
```python
def test_cpu_usage_while_listening():
    """
    Test: CPU usage while Gerald is listening (idle)
    Expected: <5% CPU usage on average
    """
    import psutil
    import time

    # Start Gerald
    process = start_gerald()
    time.sleep(5)  # Let it stabilize

    # Measure CPU for 30 seconds
    cpu_samples = []
    for _ in range(30):
        cpu_samples.append(process.cpu_percent(interval=1))

    avg_cpu = sum(cpu_samples) / len(cpu_samples)
    assert avg_cpu < 5.0, f"CPU usage too high: {avg_cpu}%"
```

## Feedback Protocol

### Issue Severity Levels
- **Critical**: System doesn't work, crashes, data loss
- **High**: Major functionality broken, performance issues
- **Medium**: Minor bugs, UX issues
- **Low**: Code quality, suggestions, optimizations

### Feedback Template
```markdown
### Issue #N: [Short Description] (YYYY-MM-DD)
**Severity**: Critical | High | Medium | Low
**Location**: `file_path:line_number`
**Problem**: Clear description of the issue
**Impact**: How this affects users or system
**Solution**: Specific fix recommendation
**Status**: Pending | In Progress | Fixed | Won't Fix
```

## Testing Checklist

Before declaring the project complete, verify:

- [ ] All services start without errors
- [ ] ASR recognizes English commands correctly
- [ ] ASR recognizes Russian commands correctly
- [ ] Language auto-detection works
- [ ] App launching works with fuzzy matching
- [ ] App closing works
- [ ] Face recognition enrolls and identifies users
- [ ] Voice recognition works (optional)
- [ ] Safety checker blocks dangerous commands
- [ ] Confirmation flow works for unsafe operations
- [ ] LLM generates appropriate responses
- [ ] TTS speaks responses in correct language
- [ ] Character personality (Gerald) is consistent
- [ ] File operations work with safety checks
- [ ] Terminal commands execute safely
- [ ] Music control works
- [ ] Language switching command works
- [ ] "Who are you?" returns correct info
- [ ] "Exit Gerald" shuts down cleanly
- [ ] Startup configuration works
- [ ] CPU usage is <5% when idle
- [ ] Response time is <2 seconds for commands
- [ ] Memory usage is reasonable (<4GB)
- [ ] Windows 10 compatibility (if testable)
- [ ] Windows 11 compatibility (if testable)
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Documentation is complete
- [ ] Installation guide works

## Quality Metrics

Track and report:
- **Test Coverage**: Aim for >80%
- **Performance**: CPU, memory, response time
- **Bug Count**: Open issues by severity
- **Documentation**: Completeness score

## Installation Instructions You Should Create

Create `tests/requirements.txt`:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-timeout>=2.1.0
pytest-benchmark>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
bandit>=1.7.0
pylint>=2.17.0
memory-profiler>=0.61.0
```

## Notes from Other Agents
(Other agents can write here if they need your attention)

---

## Getting Started

1. Create initial README.md and documentation structure
2. Set up pytest infrastructure
3. Begin monitoring other agents' work immediately
4. Write feedback as issues arise
5. Create integration tests as services become available
6. Document everything thoroughly
7. Run final validation tests

Your role is critical - you ensure the project actually works and is usable!

Start with `docs/README.md` and test infrastructure setup!

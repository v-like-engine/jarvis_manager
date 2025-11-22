# Contributing to Gerald Desktop Manager

Thank you for your interest in contributing to Gerald! This document provides guidelines for contributing to the project.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Development Setup](#development-setup)
4. [Pull Request Process](#pull-request-process)
5. [Style Guidelines](#style-guidelines)
6. [Testing Requirements](#testing-requirements)
7. [Documentation Requirements](#documentation-requirements)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

**Positive behavior includes**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes**:
- Harassment, trolling, or insulting comments
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report**:
1. Check [existing issues](https://github.com/yourusername/gerald/issues)
2. Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Generate diagnostic report: `python -m gerald_diagnostics`

**When reporting a bug, include**:
- Gerald version
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs
- Diagnostic report

**Example bug report**:
```markdown
**Bug**: Gerald doesn't recognize "Open Chrome" command

**Environment**:
- Gerald v1.0.0
- Windows 11 22H2
- Python 3.11.4

**Steps to Reproduce**:
1. Say "Hey Gerald"
2. Say "Open Chrome"

**Expected**: Chrome launches
**Actual**: Gerald says "I don't understand"

**Logs**:
[ASR Service] Recognized: "open crone" (confidence: 0.6)

**Diagnostic report**: attached
```

### Suggesting Features

**Before suggesting a feature**:
1. Check [existing feature requests](https://github.com/yourusername/gerald/labels/feature)
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand design

**When suggesting a feature, include**:
- Clear description of the feature
- Use cases and benefits
- Implementation ideas (optional)
- Mockups or examples (if applicable)

**Example feature request**:
```markdown
**Feature**: Add support for window management commands

**Description**:
Allow Gerald to minimize, maximize, and move windows.

**Use Cases**:
- "Minimize Chrome"
- "Maximize Visual Studio Code"
- "Move window to left screen"

**Implementation Ideas**:
- Use pywin32 for window manipulation
- Add new command category: window_control
- Safety: No minimizing system windows

**Mockups**: attached
```

### Contributing Code

We welcome code contributions! See [Development Setup](#development-setup) below.

---

## Development Setup

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#development-setup) for complete setup instructions.

**Quick Start**:
```bash
# Clone repo
git clone https://github.com/yourusername/gerald-desktop-manager.git
cd gerald-desktop-manager

# Setup virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r services/asr_service/requirements.txt
pip install -r services/llm_service/requirements.txt
pip install -r services/command_service/requirements.txt
pip install -r tests/requirements.txt

# Install dev tools
pip install black flake8 mypy pytest-cov

# Download models
python setup_models.py

# Run tests
pytest tests/
```

---

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

**Branch naming**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `perf/` - Performance improvements
- `test/` - Test improvements

### 2. Make Changes

- Write clean, documented code
- Follow style guidelines
- Add tests for new features
- Update documentation

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/

# Run service-specific tests
pytest services/asr_service/tests/
pytest services/llm_service/tests/
pytest services/command_service/tests/

# Check code coverage
pytest --cov=services tests/

# Format code
black .

# Lint code
flake8 .
pylint services/*/src/
```

### 4. Update Documentation

Update relevant documentation:
- Code docstrings
- `docs/API_REFERENCE.md` (if API changed)
- `docs/COMMANDS.md` (if commands changed)
- `docs/USER_GUIDE.md` (if user-facing feature)
- `docs/CHANGELOG.md` (describe your changes)

### 5. Commit Changes

**Commit message format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example**:
```
feat(asr): Add support for custom wake words

Allow users to configure custom wake words in config.yaml.
Adds new configuration option: asr.wake_words.custom

Closes #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Build process, dependencies

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- **Title**: Clear, descriptive
- **Description**: What, why, and how
- **Testing**: How you tested
- **Screenshots**: If UI changes
- **Checklist**: See below

**PR Template**:
```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes Made
- Added XYZ feature
- Fixed ABC bug
- Updated documentation

## Testing
- [ ] All existing tests pass
- [ ] Added new tests
- [ ] Manually tested on Windows 10
- [ ] Manually tested on Windows 11

## Documentation
- [ ] Updated docstrings
- [ ] Updated API_REFERENCE.md (if applicable)
- [ ] Updated USER_GUIDE.md (if applicable)
- [ ] Updated CHANGELOG.md

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] No breaking changes (or documented)
- [ ] All tests pass
```

### 7. Code Review

- Respond to reviewer feedback
- Make requested changes
- Update PR description if needed
- Be patient and respectful

### 8. Merge

Once approved:
- Squash commits (if requested)
- Merge to `develop` branch
- Delete feature branch

---

## Style Guidelines

### Python Code Style

**Follow PEP 8** with these specifics:

```python
# Line length: 100 characters
# Indentation: 4 spaces
# Use type hints
# Use descriptive variable names

def parse_command(text: str, language: str) -> Dict[str, any]:
    """Parse voice command into intent and parameters.

    Args:
        text: Recognized voice command text
        language: Language code ("en" or "ru")

    Returns:
        Dictionary with intent and parameters

    Raises:
        ValueError: If language not supported
    """
    ...
```

### Formatting

Use **Black** for automatic formatting:
```bash
black .
```

Configuration in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311']
```

### Linting

Use **flake8**:
```bash
flake8 .
```

Configuration in `.flake8`:
```ini
[flake8]
max-line-length = 100
ignore = E203, W503
exclude = venv, __pycache__
```

### Imports

Order imports:
1. Standard library
2. Third-party
3. Local

```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party
import numpy as np
from fastapi import FastAPI

# Local
from src.utils import logger
from modules.app_launcher import launch_app
```

---

## Testing Requirements

### Test Coverage

- **New features**: Must have tests
- **Bug fixes**: Add regression test
- **Target coverage**: >80%

### Types of Tests

1. **Unit Tests**: Test individual functions/classes
   ```python
   def test_parse_app_launch():
       result = parse_command("open chrome", "en")
       assert result["intent"] == "app_launch"
   ```

2. **Integration Tests**: Test service communication
   ```python
   def test_full_pipeline():
       # ASR → LLM → Command flow
       ...
   ```

3. **Performance Tests**: Verify efficiency
   ```python
   def test_cpu_usage_idle():
       cpu = measure_cpu_usage(duration=30)
       assert cpu < 5.0
   ```

4. **Safety Tests**: Verify security
   ```python
   def test_dangerous_command_blocked():
       result = check_command("format C:")
       assert result["blocked"] == True
   ```

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/integration/test_full_pipeline.py

# Specific test function
pytest tests/integration/test_full_pipeline.py::test_app_launch

# With coverage
pytest --cov=services --cov-report=html tests/

# Verbose output
pytest -v tests/
```

---

## Documentation Requirements

### Code Documentation

**All functions must have docstrings**:

```python
def my_function(param1: str, param2: int = 0) -> Dict:
    """One-line summary.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid

    Example:
        >>> my_function("test", 5)
        {"result": "success"}
    """
    ...
```

### User Documentation

Update user-facing docs for new features:
- `docs/USER_GUIDE.md`
- `docs/COMMANDS.md`
- `docs/TROUBLESHOOTING.md`

### Developer Documentation

Update developer docs for API/architecture changes:
- `docs/ARCHITECTURE.md`
- `docs/API_REFERENCE.md`
- `docs/DEVELOPER_GUIDE.md`

### CHANGELOG

Add entry to `docs/CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- New feature XYZ (#123)

### Fixed
- Bug ABC (#456)

### Changed
- Improved performance of DEF
```

---

## Agent-Specific Guidelines

### Agent 1 (ASR Service)

**Files**: `services/asr_service/**`

When contributing to ASR:
- Maintain <2s response time
- Support both English and Russian
- Document voice command patterns
- Test with various accents/microphones

### Agent 2 (LLM Service)

**Files**: `services/llm_service/**`

When contributing to LLM:
- Keep responses under 100 tokens
- Maintain character personality
- Document prompt templates
- Test multilingual responses

### Agent 3 (Command Service)

**Files**: `services/command_service/**`

When contributing to Commands:
- Always implement safety checks
- Test on Windows 10 and 11
- Document new command types
- Handle errors gracefully

### Agent 4 (Testing & Documentation)

**Files**: `tests/**`, `docs/**`

When contributing tests/docs:
- Maintain >80% test coverage
- Keep documentation current
- Add integration tests for new features
- Document all changes

---

## Getting Help

### Questions?

- **GitHub Discussions**: Ask questions
- **Discord**: Join community (link TBD)
- **Documentation**: Read `docs/`

### Found a Security Issue?

**DO NOT** open a public issue. Instead:
- Email: security@gerald-project.com (TBD)
- Include detailed description
- We'll respond within 48 hours

---

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md`
- Release notes
- Project README

Top contributors may become:
- Core maintainers
- Agent leads
- Community moderators

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (TBD).

---

**Thank you for contributing to Gerald!** 🎙️⚔️

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0

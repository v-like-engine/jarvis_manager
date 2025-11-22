"""
Pytest configuration and shared fixtures for Gerald tests
"""

import os
import sys
import pytest
import time
import psutil
from typing import Generator
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# Service Management Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return project root directory"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def config_path(project_root) -> Path:
    """Return path to main config file"""
    return project_root / "config" / "main_config.yaml"


@pytest.fixture(scope="module")
def asr_service_url() -> str:
    """ASR Service base URL"""
    return "http://localhost:8001"


@pytest.fixture(scope="module")
def llm_service_url() -> str:
    """LLM Service base URL"""
    return "http://localhost:8002"


@pytest.fixture(scope="module")
def command_service_url() -> str:
    """Command Service base URL"""
    return "http://localhost:8003"


# ============================================================================
# HTTP Client Fixtures
# ============================================================================

@pytest.fixture
def http_client():
    """HTTP client for testing APIs"""
    import httpx
    with httpx.Client(timeout=30.0) as client:
        yield client


@pytest.fixture
async def async_http_client():
    """Async HTTP client for testing APIs"""
    import httpx
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


# ============================================================================
# Service Health Check Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def ensure_asr_service_running(asr_service_url, http_client):
    """Ensure ASR service is running before tests"""
    import httpx
    try:
        response = http_client.get(f"{asr_service_url}/health")
        if response.status_code == 200:
            yield True
        else:
            pytest.skip("ASR service not running")
    except httpx.ConnectError:
        pytest.skip("ASR service not accessible")


@pytest.fixture(scope="module")
def ensure_llm_service_running(llm_service_url, http_client):
    """Ensure LLM service is running before tests"""
    import httpx
    try:
        response = http_client.get(f"{llm_service_url}/health")
        if response.status_code == 200:
            yield True
        else:
            pytest.skip("LLM service not running")
    except httpx.ConnectError:
        pytest.skip("LLM service not accessible")


@pytest.fixture(scope="module")
def ensure_command_service_running(command_service_url, http_client):
    """Ensure Command service is running before tests"""
    import httpx
    try:
        response = http_client.get(f"{command_service_url}/health")
        if response.status_code == 200:
            yield True
        else:
            pytest.skip("Command service not running")
    except httpx.ConnectError:
        pytest.skip("Command service not accessible")


@pytest.fixture(scope="module")
def ensure_all_services_running(
    ensure_asr_service_running,
    ensure_llm_service_running,
    ensure_command_service_running
):
    """Ensure all services are running before tests"""
    yield True


# ============================================================================
# Performance Monitoring Fixtures
# ============================================================================

@pytest.fixture
def cpu_monitor():
    """Monitor CPU usage during test"""
    class CPUMonitor:
        def __init__(self):
            self.samples = []
            self.monitoring = False

        def start(self):
            """Start monitoring"""
            self.monitoring = True
            self.samples = []
            psutil.cpu_percent(interval=None)  # Initialize

        def sample(self):
            """Take a CPU usage sample"""
            if self.monitoring:
                self.samples.append(psutil.cpu_percent(interval=0.1))

        def stop(self):
            """Stop monitoring and return average"""
            self.monitoring = False
            if not self.samples:
                return 0.0
            return sum(self.samples) / len(self.samples)

    return CPUMonitor()


@pytest.fixture
def memory_monitor():
    """Monitor memory usage during test"""
    class MemoryMonitor:
        def __init__(self):
            self.start_memory = 0
            self.end_memory = 0

        def start(self):
            """Record starting memory"""
            self.start_memory = psutil.virtual_memory().used

        def stop(self):
            """Record ending memory and return delta in MB"""
            self.end_memory = psutil.virtual_memory().used
            delta_bytes = self.end_memory - self.start_memory
            return delta_bytes / (1024 * 1024)  # Convert to MB

    return MemoryMonitor()


@pytest.fixture
def timer():
    """Time test execution"""
    class Timer:
        def __init__(self):
            self.start_time = 0
            self.end_time = 0

        def start(self):
            """Start timer"""
            self.start_time = time.time()

        def stop(self):
            """Stop timer and return elapsed time in seconds"""
            self.end_time = time.time()
            return self.end_time - self.start_time

    return Timer()


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_audio_data():
    """Mock audio data (base64)"""
    # This would be actual base64-encoded audio in real implementation
    return "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQAAAAA="


@pytest.fixture
def mock_recognized_text():
    """Mock recognized text samples"""
    return {
        "en": {
            "app_launch": "open chrome",
            "app_close": "close chrome",
            "file_create": "create file notes.txt",
            "info_query": "what time is it"
        },
        "ru": {
            "app_launch": "открой chrome",
            "app_close": "закрой chrome",
            "file_create": "создай файл заметки.txt",
            "info_query": "сколько времени"
        }
    }


@pytest.fixture
def mock_command_intents():
    """Mock parsed command intents"""
    return {
        "app_launch": {
            "intent": "app_launch",
            "params": {"app_name": "chrome"},
            "confidence": 0.95
        },
        "app_close": {
            "intent": "app_close",
            "params": {"app_name": "chrome"},
            "confidence": 0.93
        },
        "file_delete": {
            "intent": "file_delete",
            "params": {"file_path": "C:\\Users\\test\\test.txt"},
            "confidence": 0.88
        }
    }


# ============================================================================
# Test Data Cleanup
# ============================================================================

@pytest.fixture
def temp_test_file(tmp_path):
    """Create temporary test file"""
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("Test content")
    yield test_file
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def temp_test_folder(tmp_path):
    """Create temporary test folder"""
    test_folder = tmp_path / "test_folder"
    test_folder.mkdir()
    yield test_folder
    # Cleanup happens automatically with tmp_path


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def test_database(tmp_path):
    """Create temporary test database"""
    import sqlite3
    db_path = tmp_path / "test_user_data.db"

    # Create database with schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            face_encoding BLOB,
            voice_embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """Test configuration dictionary"""
    return {
        "app": {
            "name": "Gerald Desktop Manager",
            "version": "1.0.0",
            "character": "gerald",
            "default_language": "en"
        },
        "asr": {
            "vad": {
                "threshold": 0.5
            }
        },
        "llm": {
            "model": "phi-3-mini",
            "inference": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        },
        "commands": {
            "safety": {
                "confirmation_required": ["file_delete", "terminal_command"],
                "forbidden_patterns": ["format *", "del /s /q C:\\"]
            }
        }
    }


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "safety: marks tests as safety tests"
    )
    config.addinivalue_line(
        "markers", "requires_services: marks tests that require running services"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    skip_slow = pytest.mark.skip(reason="Slow test (use --runslow to run)")

    for item in items:
        if "slow" in item.keywords and not config.getoption("--runslow", default=False):
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )
    parser.addoption(
        "--runservices",
        action="store_true",
        default=False,
        help="Run tests that require services to be running"
    )

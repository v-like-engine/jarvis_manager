"""
Performance Test: Memory Usage

Verify Gerald meets memory usage requirements:
- <4GB total memory usage
- No memory leaks over time
"""

import pytest
import time
import psutil
import httpx
from typing import List


@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage metrics"""

    def test_total_memory_usage(self, ensure_all_services_running):
        """
        Test: Total memory usage for all Gerald services
        Target: <2GB
        Acceptable: <4GB
        """
        time.sleep(3)  # Stabilize

        # Get Python processes (Gerald services)
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Calculate total memory
        total_memory_mb = 0
        for proc in python_processes:
            try:
                mem_info = proc.memory_info()
                mem_mb = mem_info.rss / (1024 * 1024)  # Convert to MB
                print(f"Process {proc.pid}: {mem_mb:.1f} MB")
                total_memory_mb += mem_mb
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        total_memory_gb = total_memory_mb / 1024

        print(f"\nTotal Memory Usage:")
        print(f"  {total_memory_mb:.1f} MB ({total_memory_gb:.2f} GB)")

        # Target: <2GB, Acceptable: <4GB
        assert total_memory_gb < 4.0, f"Memory usage too high: {total_memory_gb:.2f}GB (target: <2GB)"

        if total_memory_gb > 2.0:
            pytest.warn(f"Memory usage above target: {total_memory_gb:.2f}GB (target: <2GB)")

    @pytest.mark.slow
    def test_memory_leak_detection(self, ensure_all_services_running, asr_service_url):
        """
        Test: Check for memory leaks over time
        Method: Process many commands and monitor memory growth
        """
        import httpx

        # Measure initial memory
        initial_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB

        memory_samples: List[float] = []

        # Process 100 commands
        with httpx.Client(timeout=30.0) as client:
            for i in range(100):
                client.post(
                    f"{asr_service_url}/parse_command",
                    json={"text": f"open app{i % 10}", "language": "en"}
                )

                # Sample memory every 10 iterations
                if i % 10 == 0:
                    current_memory = psutil.virtual_memory().used / (1024 * 1024)
                    memory_samples.append(current_memory)

        # Measure final memory
        final_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB

        memory_growth_mb = final_memory - initial_memory
        memory_growth_percent = (memory_growth_mb / initial_memory) * 100

        print(f"\nMemory Leak Test:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Growth: {memory_growth_mb:.1f} MB ({memory_growth_percent:.2f}%)")

        # Should not grow more than 10%
        assert memory_growth_percent < 10.0, f"Possible memory leak: {memory_growth_percent:.2f}% growth"

    def test_model_loading_memory(self, ensure_all_services_running):
        """
        Test: Memory usage with models loaded
        Verify models fit in memory budget
        """
        time.sleep(5)  # Ensure models loaded

        # Check system memory
        mem = psutil.virtual_memory()

        print(f"\nSystem Memory:")
        print(f"  Total: {mem.total / (1024**3):.2f} GB")
        print(f"  Available: {mem.available / (1024**3):.2f} GB")
        print(f"  Used: {mem.used / (1024**3):.2f} GB")
        print(f"  Percent: {mem.percent}%")

        # System should have at least 2GB available
        assert mem.available > 2 * (1024**3), "Insufficient available memory"

    @pytest.mark.slow
    def test_memory_usage_under_load(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url
    ):
        """
        Test: Memory usage under heavy load
        Process commands rapidly and monitor memory
        """
        import httpx
        import concurrent.futures

        initial_memory = psutil.virtual_memory().used / (1024 * 1024)

        def process_command(text):
            with httpx.Client(timeout=30.0) as client:
                client.post(
                    f"{asr_service_url}/parse_command",
                    json={"text": text, "language": "en"}
                )

        # Process 50 commands concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(process_command, f"command {i}")
                for i in range(50)
            ]
            concurrent.futures.wait(futures)

        final_memory = psutil.virtual_memory().used / (1024 * 1024)
        memory_delta = final_memory - initial_memory

        print(f"\nMemory Under Load:")
        print(f"  Delta: {memory_delta:.1f} MB")

        # Should not increase more than 500MB under load
        assert memory_delta < 500, f"Memory increased too much: {memory_delta:.1f}MB"

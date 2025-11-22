"""
Performance Test: CPU Usage

Verify Gerald meets CPU usage requirements:
- <5% CPU when idle (listening)
- <50% CPU when processing commands
"""

import pytest
import time
import psutil
import httpx
from typing import List


@pytest.mark.performance
class TestCPUUsage:
    """Test CPU usage metrics"""

    @pytest.mark.slow
    def test_cpu_usage_while_idle(self, ensure_all_services_running):
        """
        Test: CPU usage while Gerald is listening (idle)
        Target: <5% CPU usage on average
        Acceptable: <7% CPU usage
        """
        # Let system stabilize
        time.sleep(5)

        # Measure CPU for 30 seconds
        cpu_samples: List[float] = []
        for _ in range(30):
            cpu_samples.append(psutil.cpu_percent(interval=1))

        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)

        print(f"\nCPU Usage (Idle):")
        print(f"  Average: {avg_cpu:.2f}%")
        print(f"  Maximum: {max_cpu:.2f}%")
        print(f"  Minimum: {min(cpu_samples):.2f}%")

        # Target: <5%, Acceptable: <7%
        assert avg_cpu < 7.0, f"CPU usage too high: {avg_cpu:.2f}% (target: <5%)"

        # Warn if above target but below acceptable
        if avg_cpu > 5.0:
            pytest.warn(f"CPU usage above target: {avg_cpu:.2f}% (target: <5%)")

    @pytest.mark.slow
    def test_cpu_usage_during_command_processing(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url
    ):
        """
        Test: CPU usage while processing voice commands
        Target: <30% CPU average
        Acceptable: <50% CPU average
        """
        import httpx

        # Warm up services
        with httpx.Client(timeout=30.0) as client:
            client.post(f"{asr_service_url}/parse_command",
                       json={"text": "test", "language": "en"})

        # Start CPU monitoring
        cpu_samples: List[float] = []

        # Process multiple commands while monitoring
        with httpx.Client(timeout=30.0) as client:
            for i in range(10):
                # Sample CPU before command
                cpu_samples.append(psutil.cpu_percent(interval=0.1))

                # Execute command
                client.post(
                    f"{asr_service_url}/parse_command",
                    json={"text": "open chrome", "language": "en"}
                )

                # Sample CPU after command
                cpu_samples.append(psutil.cpu_percent(interval=0.1))

        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)

        print(f"\nCPU Usage (Active):")
        print(f"  Average: {avg_cpu:.2f}%")
        print(f"  Maximum: {max_cpu:.2f}%")

        # Target: <30%, Acceptable: <50%
        assert avg_cpu < 50.0, f"CPU usage too high: {avg_cpu:.2f}% (target: <30%)"

        if avg_cpu > 30.0:
            pytest.warn(f"CPU usage above target: {avg_cpu:.2f}% (target: <30%)")

    def test_cpu_usage_per_service(self, ensure_all_services_running):
        """
        Test: Individual service CPU usage
        Target: Each service <3% when idle
        """
        time.sleep(3)  # Stabilize

        # Get Python processes (Gerald services)
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Measure each process
        for proc in python_processes:
            cpu = proc.cpu_percent(interval=1.0)
            print(f"Process {proc.pid}: {cpu:.2f}% CPU")

        # Total CPU for all Gerald processes
        total_cpu = sum(proc.cpu_percent(interval=0.5) for proc in python_processes)

        print(f"\nTotal Gerald CPU: {total_cpu:.2f}%")
        assert total_cpu < 10.0, f"Total Gerald CPU too high: {total_cpu:.2f}%"

    @pytest.mark.benchmark
    def test_cpu_efficiency_benchmark(self, ensure_all_services_running, benchmark):
        """
        Benchmark: CPU efficiency for command parsing
        """
        import httpx

        def parse_command():
            with httpx.Client() as client:
                client.post(
                    "http://localhost:8001/parse_command",
                    json={"text": "open chrome", "language": "en"}
                )

        # Run benchmark
        result = benchmark(parse_command)

        print(f"\nBenchmark Results:")
        print(f"  Mean: {result.stats.mean:.4f}s")
        print(f"  Median: {result.stats.median:.4f}s")
        print(f"  Min: {result.stats.min:.4f}s")
        print(f"  Max: {result.stats.max:.4f}s")

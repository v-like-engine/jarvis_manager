"""
Performance Test: Response Time

Verify Gerald meets response time requirements:
- <2 seconds from voice input to execution
- <500ms for command parsing
- <1.5s for LLM inference
"""

import pytest
import time
import httpx
from typing import List


@pytest.mark.performance
class TestResponseTime:
    """Test response time metrics"""

    def test_command_parsing_speed(self, ensure_asr_service_running, asr_service_url):
        """
        Test: Command parsing response time
        Target: <500ms
        Acceptable: <1000ms
        """
        import httpx

        response_times: List[float] = []

        with httpx.Client(timeout=30.0) as client:
            # Test multiple commands
            test_commands = [
                "open chrome",
                "close calculator",
                "who are you",
                "what time is it",
                "create file test.txt"
            ]

            for cmd in test_commands:
                start_time = time.time()

                response = client.post(
                    f"{asr_service_url}/parse_command",
                    json={"text": cmd, "language": "en"}
                )

                end_time = time.time()
                elapsed_ms = (end_time - start_time) * 1000

                response_times.append(elapsed_ms)
                print(f"'{cmd}': {elapsed_ms:.1f}ms")

        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        print(f"\nCommand Parsing Performance:")
        print(f"  Average: {avg_response_time:.1f}ms")
        print(f"  Maximum: {max_response_time:.1f}ms")
        print(f"  Minimum: {min(response_times):.1f}ms")

        # Target: <500ms, Acceptable: <1000ms
        assert avg_response_time < 1000, f"Parsing too slow: {avg_response_time:.1f}ms"

        if avg_response_time > 500:
            pytest.warn(f"Parsing above target: {avg_response_time:.1f}ms (target: <500ms)")

    def test_llm_inference_speed(self, ensure_llm_service_running, llm_service_url):
        """
        Test: LLM response generation speed
        Target: <1.5s
        Acceptable: <2.5s
        """
        import httpx

        response_times: List[float] = []

        with httpx.Client(timeout=30.0) as client:
            test_inputs = [
                ("who are you", "self_description"),
                ("command executed", "command_confirmation"),
                ("error occurred", "error_explanation"),
            ]

            for user_input, scenario in test_inputs:
                start_time = time.time()

                response = client.post(
                    f"{llm_service_url}/generate",
                    json={
                        "user_input": user_input,
                        "context": {"language": "en"},
                        "scenario": scenario
                    }
                )

                end_time = time.time()
                elapsed_ms = (end_time - start_time) * 1000

                response_times.append(elapsed_ms)
                print(f"'{user_input}' ({scenario}): {elapsed_ms:.1f}ms")

        avg_response_time = sum(response_times) / len(response_times)

        print(f"\nLLM Inference Performance:")
        print(f"  Average: {avg_response_time:.1f}ms")
        print(f"  Maximum: {max(response_times):.1f}ms")

        # Target: <1500ms, Acceptable: <2500ms
        assert avg_response_time < 2500, f"LLM too slow: {avg_response_time:.1f}ms"

        if avg_response_time > 1500:
            pytest.warn(f"LLM above target: {avg_response_time:.1f}ms (target: <1500ms)")

    def test_end_to_end_response_time(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url
    ):
        """
        Test: End-to-end response time (full pipeline)
        Target: <2 seconds
        Acceptable: <3 seconds
        """
        import httpx

        total_times: List[float] = []

        with httpx.Client(timeout=30.0) as client:
            for _ in range(5):  # Run 5 full pipelines
                start_time = time.time()

                # Step 1: Parse command
                asr_response = client.post(
                    f"{asr_service_url}/parse_command",
                    json={"text": "open chrome", "language": "en"}
                )
                asr_data = asr_response.json()["data"]

                # Step 2: Safety check
                llm_response = client.post(
                    f"{llm_service_url}/safety_check",
                    json={
                        "command_intent": asr_data["intent"],
                        "command_params": asr_data["params"],
                        "language": "en"
                    }
                )

                # Step 3: Execute (or simulate)
                # Note: Skip actual execution to avoid side effects

                # Step 4: Generate response
                response = client.post(
                    f"{llm_service_url}/generate",
                    json={
                        "user_input": "open chrome",
                        "context": {"language": "en"},
                        "scenario": "command_confirmation"
                    }
                )

                end_time = time.time()
                elapsed_s = end_time - start_time

                total_times.append(elapsed_s)

        avg_time = sum(total_times) / len(total_times)

        print(f"\nEnd-to-End Performance:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Maximum: {max(total_times):.2f}s")
        print(f"  Minimum: {min(total_times):.2f}s")

        # Target: <2s, Acceptable: <3s
        assert avg_time < 3.0, f"Pipeline too slow: {avg_time:.2f}s (target: <2s)"

        if avg_time > 2.0:
            pytest.warn(f"Pipeline above target: {avg_time:.2f}s (target: <2s)")

    @pytest.mark.benchmark
    def test_throughput_benchmark(self, ensure_asr_service_running, benchmark, asr_service_url):
        """
        Benchmark: Commands processed per second
        """
        import httpx

        def parse_command():
            with httpx.Client() as client:
                client.post(
                    f"{asr_service_url}/parse_command",
                    json={"text": "open chrome", "language": "en"}
                )

        result = benchmark(parse_command)

        commands_per_second = 1.0 / result.stats.mean

        print(f"\nThroughput:")
        print(f"  {commands_per_second:.1f} commands/second")
        print(f"  Mean latency: {result.stats.mean * 1000:.1f}ms")

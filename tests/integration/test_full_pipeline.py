"""
Integration Test: Full End-to-End Pipeline

Tests the complete flow from voice input to command execution to voice output.
"""

import pytest
import httpx
from typing import Dict


@pytest.mark.integration
@pytest.mark.requires_services
class TestFullPipeline:
    """Test complete command pipeline across all services"""

    def test_app_launch_english(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url,
        http_client
    ):
        """
        Test: User says "Open Chrome" in English
        Expected: Chrome launches, Gerald confirms in English
        """
        # Step 1: ASR recognizes speech
        asr_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={
                "text": "open chrome",
                "language": "en"
            }
        )
        assert asr_response.status_code == 200
        asr_data = asr_response.json()

        assert asr_data["status"] == "success"
        assert asr_data["data"]["intent"] == "app_launch"
        assert "chrome" in asr_data["data"]["params"]["app_name"].lower()

        # Step 2: LLM validates safety
        llm_response = http_client.post(
            f"{llm_service_url}/safety_check",
            json={
                "command_intent": "app_launch",
                "command_params": asr_data["data"]["params"],
                "language": "en"
            }
        )
        assert llm_response.status_code == 200
        llm_data = llm_response.json()

        assert llm_data["status"] == "success"
        assert llm_data["data"]["is_safe"] == True

        # Step 3: Command service executes
        cmd_response = http_client.post(
            f"{command_service_url}/execute",
            json={
                "intent": "app_launch",
                "params": asr_data["data"]["params"],
                "confirmed": False
            }
        )
        assert cmd_response.status_code in [200, 202]  # 202 if async
        cmd_data = cmd_response.json()

        # Verify execution (may vary based on implementation)
        assert "status" in cmd_data
        # Note: Actual Chrome launch verification depends on implementation

        # Step 4: LLM generates confirmation response
        response_gen = http_client.post(
            f"{llm_service_url}/generate",
            json={
                "user_input": "open chrome",
                "context": {
                    "language": "en",
                    "execution_result": "success"
                },
                "scenario": "command_confirmation"
            }
        )
        assert response_gen.status_code == 200
        response_data = response_gen.json()

        assert response_data["status"] == "success"
        assert response_data["data"]["language"] == "en"
        assert len(response_data["data"]["response_text"]) > 0

    def test_app_launch_russian(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url,
        http_client
    ):
        """
        Test: User says "Открой Chrome" in Russian
        Expected: Chrome launches, Gerald confirms in Russian
        """
        # Step 1: ASR recognizes Russian speech
        asr_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={
                "text": "открой chrome",
                "language": "ru"
            }
        )
        assert asr_response.status_code == 200
        asr_data = asr_response.json()

        assert asr_data["status"] == "success"
        assert asr_data["data"]["intent"] == "app_launch"

        # Step 2: LLM validates and generates response in Russian
        response_gen = http_client.post(
            f"{llm_service_url}/generate",
            json={
                "user_input": "открой chrome",
                "context": {"language": "ru"},
                "scenario": "command_confirmation"
            }
        )
        assert response_gen.status_code == 200
        response_data = response_gen.json()

        assert response_data["data"]["language"] == "ru"

    def test_dangerous_command_with_confirmation(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url,
        http_client
    ):
        """
        Test: User says "Delete file important.txt"
        Expected: Safety check triggers, confirmation requested
        """
        # Step 1: Parse command
        asr_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={
                "text": "delete file test.txt",
                "language": "en"
            }
        )
        assert asr_response.status_code == 200
        asr_data = asr_response.json()
        assert asr_data["data"]["intent"] == "file_delete"

        # Step 2: Safety check should flag as needing confirmation
        llm_response = http_client.post(
            f"{llm_service_url}/safety_check",
            json={
                "command_intent": "file_delete",
                "command_params": {"file_path": "test.txt"},
                "language": "en"
            }
        )
        assert llm_response.status_code == 200
        llm_data = llm_response.json()

        # Should be safe but require confirmation
        assert llm_data["data"]["is_safe"] == True
        assert llm_data["data"]["requires_confirmation"] == True

        # Step 3: Attempt execution without confirmation
        cmd_response = http_client.post(
            f"{command_service_url}/execute",
            json={
                "intent": "file_delete",
                "params": {"file_path": "test.txt"},
                "confirmed": False
            }
        )

        # Should return status indicating confirmation needed
        cmd_data = cmd_response.json()
        assert cmd_data.get("status") in ["needs_confirmation", "error"]

    def test_forbidden_command_blocked(
        self,
        ensure_all_services_running,
        llm_service_url,
        command_service_url,
        http_client
    ):
        """
        Test: User says "Format C:"
        Expected: Command absolutely blocked, never executed
        """
        # Step 1: Safety check should block
        llm_response = http_client.post(
            f"{llm_service_url}/safety_check",
            json={
                "command_intent": "terminal_command",
                "command_params": {"command": "format C:"},
                "language": "en"
            }
        )
        assert llm_response.status_code == 200
        llm_data = llm_response.json()

        # Should be flagged as dangerous/blocked
        assert llm_data["data"]["is_safe"] == False or llm_data["data"]["blocked"] == True

        # Step 2: Command service should also block
        cmd_response = http_client.post(
            f"{command_service_url}/execute",
            json={
                "intent": "terminal_command",
                "params": {"command": "format C:"},
                "confirmed": True  # Even with confirmation!
            }
        )

        # Should return error status
        cmd_data = cmd_response.json()
        assert cmd_data.get("status") in ["error", "blocked"]

    def test_information_query(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        http_client
    ):
        """
        Test: User asks "Who are you?"
        Expected: Gerald introduces himself
        """
        # Step 1: Parse query
        asr_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={
                "text": "who are you",
                "language": "en"
            }
        )
        assert asr_response.status_code == 200
        asr_data = asr_response.json()

        # Step 2: LLM generates self-description
        llm_response = http_client.post(
            f"{llm_service_url}/generate",
            json={
                "user_input": "who are you",
                "context": {"language": "en"},
                "scenario": "self_description"
            }
        )
        assert llm_response.status_code == 200
        llm_data = llm_response.json()

        response_text = llm_data["data"]["response_text"]
        # Should mention Gerald
        assert "gerald" in response_text.lower() or "i am" in response_text.lower()

    @pytest.mark.slow
    def test_multiple_commands_sequence(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url,
        http_client
    ):
        """
        Test: Execute multiple commands in sequence
        Expected: All commands execute correctly, context maintained
        """
        commands = [
            ("open calculator", "app_launch"),
            ("who are you", "information_query"),
            ("close calculator", "app_close"),
        ]

        for text, expected_intent in commands:
            # Parse each command
            response = http_client.post(
                f"{asr_service_url}/parse_command",
                json={"text": text, "language": "en"}
            )
            assert response.status_code == 200
            data = response.json()

            # Verify intent recognition
            if expected_intent:
                assert data["data"]["intent"] == expected_intent


@pytest.mark.integration
class TestServiceCommunication:
    """Test inter-service communication patterns"""

    def test_asr_to_llm_communication(
        self,
        ensure_asr_service_running,
        ensure_llm_service_running,
        asr_service_url,
        llm_service_url,
        http_client
    ):
        """Test ASR → LLM data flow"""
        # ASR parses command
        asr_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={"text": "open chrome", "language": "en"}
        )
        asr_data = asr_response.json()["data"]

        # LLM processes ASR output
        llm_response = http_client.post(
            f"{llm_service_url}/safety_check",
            json={
                "command_intent": asr_data["intent"],
                "command_params": asr_data["params"],
                "language": "en"
            }
        )
        assert llm_response.status_code == 200

    def test_llm_to_command_communication(
        self,
        ensure_llm_service_running,
        ensure_command_service_running,
        llm_service_url,
        command_service_url,
        http_client
    ):
        """Test LLM → Command Service data flow"""
        # LLM validates command (simulated)
        intent = "app_launch"
        params = {"app_name": "calculator"}

        # Command service receives LLM-validated command
        cmd_response = http_client.post(
            f"{command_service_url}/execute",
            json={
                "intent": intent,
                "params": params,
                "confirmed": False
            }
        )
        assert cmd_response.status_code in [200, 202]


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across services"""

    def test_invalid_command(
        self,
        ensure_asr_service_running,
        asr_service_url,
        http_client
    ):
        """Test handling of unrecognized commands"""
        response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={"text": "xyz nonsense command", "language": "en"}
        )
        assert response.status_code in [200, 400]

    def test_missing_parameters(
        self,
        ensure_command_service_running,
        command_service_url,
        http_client
    ):
        """Test handling of missing required parameters"""
        response = http_client.post(
            f"{command_service_url}/execute",
            json={
                "intent": "app_launch",
                # Missing params
            }
        )
        assert response.status_code in [400, 422]  # Bad request

    def test_service_timeout(
        self,
        ensure_llm_service_running,
        llm_service_url
    ):
        """Test timeout handling"""
        import httpx

        with httpx.Client(timeout=0.001) as client:  # Very short timeout
            with pytest.raises(httpx.TimeoutException):
                client.post(
                    f"{llm_service_url}/generate",
                    json={
                        "user_input": "test",
                        "scenario": "command_confirmation"
                    }
                )

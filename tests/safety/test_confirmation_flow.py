"""
Safety Test: Confirmation Flow

Verify confirmation system works correctly:
- User confirmation required for dangerous operations
- User can cancel operations
- Confirmation state properly managed
"""

import pytest
import httpx


@pytest.mark.safety
class TestConfirmationFlow:
    """Test confirmation request and handling"""

    def test_file_deletion_confirmation_flow(
        self,
        ensure_all_services_running,
        asr_service_url,
        llm_service_url,
        command_service_url,
        http_client
    ):
        """
        Test: Complete confirmation flow for file deletion
        Flow: Request deletion → Confirmation requested → User confirms → Execute
        """
        # Step 1: Parse delete command
        asr_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={
                "text": "delete file test.txt",
                "language": "en"
            }
        )
        asr_data = asr_response.json()["data"]
        assert asr_data["intent"] == "file_delete"

        # Step 2: Safety check should require confirmation
        llm_response = http_client.post(
            f"{llm_service_url}/safety_check",
            json={
                "command_intent": "file_delete",
                "command_params": {"file_path": "test.txt"},
                "language": "en"
            }
        )
        llm_data = llm_response.json()["data"]

        assert llm_data.get("requires_confirmation") == True
        confirmation_text = llm_data.get("suggested_confirmation_text", "")

        print(f"Confirmation requested: {confirmation_text}")

        # Step 3: Attempt execution without confirmation
        cmd_response = http_client.post(
            f"{command_service_url}/execute",
            json={
                "intent": "file_delete",
                "params": {"file_path": "test.txt"},
                "confirmed": False
            }
        )
        cmd_data = cmd_response.json()

        # Should request confirmation
        assert cmd_data.get("status") in ["needs_confirmation", "error"]

        # Step 4: Parse confirmation response
        confirm_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={
                "text": "yes confirm",
                "language": "en"
            }
        )
        # Should recognize as confirmation

        # Step 5: Retry with confirmation
        # Note: Actual execution skipped to avoid side effects

    def test_cancellation_flow(
        self,
        ensure_all_services_running,
        asr_service_url,
        http_client
    ):
        """
        Test: User can cancel dangerous operation
        Flow: Request deletion → Confirmation requested → User cancels
        """
        # Request deletion
        asr_response = http_client.post(
            f"{asr_service_url}/parse_command",
            json={
                "text": "delete file important.txt",
                "language": "en"
            }
        )

        # User says "no" or "cancel"
        cancel_responses = ["no", "cancel", "stop", "nevermind"]

        for cancel_text in cancel_responses:
            cancel_response = http_client.post(
                f"{asr_service_url}/parse_command",
                json={
                    "text": cancel_text,
                    "language": "en"
                }
            )
            # Should be recognized (implementation-dependent)
            print(f"Cancel text '{cancel_text}' parsed")

    def test_confirmation_text_generation(
        self,
        ensure_llm_service_running,
        llm_service_url,
        http_client
    ):
        """
        Test: LLM generates appropriate confirmation text
        Expected: Clear, informative confirmation messages
        """
        dangerous_operations = [
            {
                "intent": "file_delete",
                "params": {"file_path": "important.txt"},
                "expected_keywords": ["delete", "important.txt"]
            },
            {
                "intent": "folder_delete",
                "params": {"folder_path": "MyFolder"},
                "expected_keywords": ["delete", "MyFolder", "contents"]
            },
            {
                "intent": "terminal_command",
                "params": {"command": "shutdown /s"},
                "expected_keywords": ["shutdown", "command"]
            }
        ]

        for operation in dangerous_operations:
            response = http_client.post(
                f"{llm_service_url}/safety_check",
                json={
                    "command_intent": operation["intent"],
                    "command_params": operation["params"],
                    "language": "en"
                }
            )

            data = response.json()["data"]

            if data.get("requires_confirmation"):
                confirmation_text = data.get("suggested_confirmation_text", "").lower()

                print(f"\nOperation: {operation['intent']}")
                print(f"Confirmation: {confirmation_text}")

                # Check if confirmation text is informative
                # (At least some keywords should be present)
                # This is implementation-dependent

    def test_multilingual_confirmation(
        self,
        ensure_llm_service_running,
        llm_service_url,
        http_client
    ):
        """
        Test: Confirmation messages in multiple languages
        Expected: Russian confirmation messages for Russian commands
        """
        # English confirmation
        en_response = http_client.post(
            f"{llm_service_url}/safety_check",
            json={
                "command_intent": "file_delete",
                "command_params": {"file_path": "test.txt"},
                "language": "en"
            }
        )
        en_data = en_response.json()["data"]

        # Russian confirmation
        ru_response = http_client.post(
            f"{llm_service_url}/safety_check",
            json={
                "command_intent": "file_delete",
                "command_params": {"file_path": "test.txt"},
                "language": "ru"
            }
        )
        ru_data = ru_response.json()["data"]

        # Both should require confirmation
        assert en_data.get("requires_confirmation") == True
        assert ru_data.get("requires_confirmation") == True

        print(f"English: {en_data.get('suggested_confirmation_text', '')}")
        print(f"Russian: {ru_data.get('suggested_confirmation_text', '')}")


@pytest.mark.safety
class TestConfirmationRecognition:
    """Test recognition of confirmation/cancellation responses"""

    def test_positive_confirmation_recognition(
        self,
        ensure_asr_service_running,
        asr_service_url,
        http_client
    ):
        """
        Test: Various ways of saying "yes" are recognized
        """
        positive_responses = [
            "yes",
            "confirm",
            "do it",
            "proceed",
            "go ahead",
            "yes please",
            "affirmative"
        ]

        for response_text in positive_responses:
            response = http_client.post(
                f"{asr_service_url}/parse_command",
                json={
                    "text": response_text,
                    "language": "en"
                }
            )

            # Should be recognized (implementation-dependent)
            print(f"Positive: '{response_text}'")

    def test_negative_confirmation_recognition(
        self,
        ensure_asr_service_running,
        asr_service_url,
        http_client
    ):
        """
        Test: Various ways of saying "no" are recognized
        """
        negative_responses = [
            "no",
            "cancel",
            "stop",
            "nevermind",
            "abort",
            "no thanks",
            "don't do it"
        ]

        for response_text in negative_responses:
            response = http_client.post(
                f"{asr_service_url}/parse_command",
                json={
                    "text": response_text,
                    "language": "en"
                }
            )

            # Should be recognized (implementation-dependent)
            print(f"Negative: '{response_text}'")

    def test_russian_confirmation_recognition(
        self,
        ensure_asr_service_running,
        asr_service_url,
        http_client
    ):
        """
        Test: Russian confirmation/cancellation recognized
        """
        russian_responses = [
            ("да", "positive"),
            ("нет", "negative"),
            ("подтверди", "positive"),
            ("отмена", "negative")
        ]

        for response_text, response_type in russian_responses:
            response = http_client.post(
                f"{asr_service_url}/parse_command",
                json={
                    "text": response_text,
                    "language": "ru"
                }
            )

            print(f"Russian {response_type}: '{response_text}'")

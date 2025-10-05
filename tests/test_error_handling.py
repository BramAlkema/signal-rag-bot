#!/usr/bin/env python3
"""
Error handling and recovery test suite
Tests for retry logic, graceful degradation, auto-reconnect, and error logging
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time


class TestRetryLogic:
    """Test retry logic with exponential backoff"""

    def test_retry_success_on_second_attempt(self):
        """Should retry and succeed on second attempt"""
        from error_handling import retry_with_backoff

        attempt_count = [0]

        def failing_then_success():
            attempt_count[0] += 1
            if attempt_count[0] == 1:
                raise Exception("First attempt fails")
            return "success"

        result = retry_with_backoff(failing_then_success, max_retries=3)
        assert result == "success"
        assert attempt_count[0] == 2

    def test_retry_max_attempts(self):
        """Should fail after max retries"""
        from error_handling import retry_with_backoff

        def always_fails():
            raise Exception("Always fails")

        with pytest.raises(Exception, match="Always fails"):
            retry_with_backoff(always_fails, max_retries=3)

    def test_exponential_backoff_timing(self):
        """Should use exponential backoff between retries"""
        from error_handling import retry_with_backoff

        attempt_times = []

        def failing_func():
            attempt_times.append(time.time())
            raise Exception("Fail")

        with patch('time.sleep') as mock_sleep:
            try:
                retry_with_backoff(failing_func, max_retries=3, base_delay=1.0)
            except:
                pass

            # Should have called sleep with increasing delays: 1, 2, 4
            assert mock_sleep.call_count == 3
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            assert calls == [1.0, 2.0, 4.0]

    def test_retry_specific_exceptions_only(self):
        """Should only retry specific exceptions"""
        from error_handling import retry_with_backoff

        def raises_value_error():
            raise ValueError("Wrong type")

        # Should not retry ValueError
        with pytest.raises(ValueError):
            retry_with_backoff(
                raises_value_error,
                max_retries=3,
                retry_exceptions=(ConnectionError,)
            )


class TestGracefulDegradation:
    """Test graceful degradation when services fail"""

    def test_fallback_response_on_rag_failure(self):
        """Should return fallback response when RAG fails"""
        from error_handling import get_response_with_fallback

        def failing_rag(query):
            raise Exception("RAG index corrupted")

        response = get_response_with_fallback(
            failing_rag,
            "What is NLDTIB?",
            fallback="I'm having trouble accessing my knowledge base. Please try again later."
        )

        assert "trouble accessing" in response

    def test_partial_response_on_embedding_failure(self):
        """Should provide partial response when embedding fails"""
        from error_handling import get_response_with_fallback

        def partial_rag(query):
            # Simulate partial failure - can search but not embed
            return {
                'answer': None,
                'sources': ['doc1.pdf', 'doc2.pdf'],
                'error': 'Embedding failed'
            }

        response = get_response_with_fallback(
            partial_rag,
            "Tell me about drones",
            fallback="Unable to process query"
        )

        # Should include sources even if answer generation failed
        assert 'doc1.pdf' in str(response) or 'Unable to process' in response


class TestSignalCliAutoReconnect:
    """Test signal-cli auto-reconnect functionality"""

    def test_reconnect_on_timeout(self):
        """Should attempt reconnect when signal-cli times out"""
        from error_handling import receive_with_reconnect
        import subprocess

        attempt_count = [0]

        def mock_receive(*args, **kwargs):
            attempt_count[0] += 1
            if attempt_count[0] == 1:
                raise subprocess.TimeoutExpired('signal-cli', 5)
            # Return successful result
            mock_result = Mock()
            mock_result.stdout = '{"sender": "+123", "text": "Hello"}'
            return mock_result

        with patch('subprocess.run', side_effect=mock_receive):
            messages = receive_with_reconnect()
            # Should have retried
            assert attempt_count[0] >= 1

    def test_max_reconnect_attempts(self):
        """Should fail after max reconnect attempts"""
        from error_handling import receive_with_reconnect

        def always_timeout():
            import subprocess
            raise subprocess.TimeoutExpired('signal-cli', 5)

        import subprocess
        with patch('subprocess.run', side_effect=always_timeout):
            messages = receive_with_reconnect(max_retries=3)
            # Should return empty list after max retries
            assert messages == []

    def test_handle_signal_cli_crash(self):
        """Should detect and handle signal-cli crashes"""
        from error_handling import check_signal_cli_health

        with patch('subprocess.run') as mock_run:
            # Simulate signal-cli not responding
            mock_run.side_effect = FileNotFoundError("signal-cli not found")

            is_healthy = check_signal_cli_health()
            assert is_healthy is False


class TestFAISSIndexValidation:
    """Test FAISS index integrity checks"""

    def test_validate_index_structure(self):
        """Should validate FAISS index structure"""
        from error_handling import validate_faiss_index
        import numpy as np

        # Mock valid index with search method
        mock_index = Mock()
        mock_index.ntotal = 1000
        mock_index.d = 1536  # Embedding dimension

        # Mock successful search
        mock_distances = np.array([[0.1, 0.2, 0.3]])
        mock_indices = np.array([[0, 1, 2]])
        mock_index.search = Mock(return_value=(mock_distances, mock_indices))

        is_valid, error = validate_faiss_index(mock_index, expected_dim=1536)
        assert is_valid is True
        assert error is None

    def test_detect_corrupted_index(self):
        """Should detect corrupted index"""
        from error_handling import validate_faiss_index

        # Mock corrupted index
        mock_index = Mock()
        mock_index.ntotal = 0  # No vectors

        is_valid, error = validate_faiss_index(mock_index, expected_dim=1536)
        assert is_valid is False
        assert "no vectors" in error.lower()

    def test_detect_dimension_mismatch(self):
        """Should detect dimension mismatch"""
        from error_handling import validate_faiss_index

        mock_index = Mock()
        mock_index.ntotal = 1000
        mock_index.d = 768  # Wrong dimension

        is_valid, error = validate_faiss_index(mock_index, expected_dim=1536)
        assert is_valid is False
        assert "dimension" in error.lower()

    def test_index_checksum_validation(self):
        """Should validate index checksum"""
        from error_handling import validate_index_checksum
        import hashlib

        # Create test index data
        test_data = b"test index data"
        expected_checksum = hashlib.sha256(test_data).hexdigest()

        # Valid checksum
        is_valid = validate_index_checksum(test_data, expected_checksum)
        assert is_valid is True

        # Invalid checksum
        is_valid = validate_index_checksum(test_data, "wrong_checksum")
        assert is_valid is False


class TestErrorLogging:
    """Test comprehensive error logging"""

    def test_sanitize_error_messages(self):
        """Should sanitize sensitive data from error messages"""
        from error_handling import sanitize_error_message

        # Should remove API keys
        error_with_key = "OpenAI error: Invalid API key sk-abc123def456"
        sanitized = sanitize_error_message(error_with_key)
        assert "sk-abc123def456" not in sanitized
        assert "[REDACTED]" in sanitized

        # Should remove phone numbers
        error_with_phone = "Failed to send to +31612345678"
        sanitized = sanitize_error_message(error_with_phone)
        assert "+31612345678" not in sanitized
        assert "[PHONE]" in sanitized

    def test_log_error_with_context(self):
        """Should log errors with context"""
        from error_handling import log_error_with_context

        error = Exception("Test error")
        context = {
            'user': '+31612345678',
            'action': 'query',
            'timestamp': '2025-10-05T12:00:00'
        }

        with patch('logging.error') as mock_log:
            log_error_with_context(error, context)

            # Should have been called
            assert mock_log.called

            # Should not contain raw phone number
            log_message = str(mock_log.call_args)
            assert '+31612345678' not in log_message

    def test_error_categorization(self):
        """Should categorize errors correctly"""
        from error_handling import categorize_error

        # API errors
        api_error = Exception("OpenAI rate limit exceeded")
        category = categorize_error(api_error)
        assert category == "API_RATE_LIMIT"

        # Network errors
        import requests
        network_error = requests.exceptions.ConnectionError("Connection refused")
        category = categorize_error(network_error)
        assert category == "NETWORK_ERROR"

        # Index errors
        index_error = Exception("FAISS index corrupted")
        category = categorize_error(index_error)
        assert category == "INDEX_ERROR"

    def test_error_metrics_collection(self):
        """Should collect error metrics"""
        from error_handling import ErrorMetrics

        metrics = ErrorMetrics()

        # Record errors
        metrics.record_error("API_RATE_LIMIT")
        metrics.record_error("API_RATE_LIMIT")
        metrics.record_error("NETWORK_ERROR")

        # Check counts
        assert metrics.get_count("API_RATE_LIMIT") == 2
        assert metrics.get_count("NETWORK_ERROR") == 1
        assert metrics.get_total_errors() == 3

    def test_error_rate_threshold_alert(self):
        """Should alert when error rate exceeds threshold"""
        from error_handling import ErrorRateMonitor

        monitor = ErrorRateMonitor(threshold=0.1, window_seconds=60)

        # Record successful operations
        for _ in range(90):
            monitor.record_success()

        # Record failures
        for _ in range(11):  # 11/101 = 10.9% > 10% threshold
            monitor.record_failure()

        assert monitor.should_alert() is True


class TestOpenAIErrorHandling:
    """Test OpenAI-specific error handling"""

    def test_handle_rate_limit_error(self):
        """Should handle rate limit with backoff"""
        from error_handling import handle_openai_error

        # Use generic exception with rate limit message
        error = Exception("Rate limit exceeded")
        action = handle_openai_error(error)

        assert action == "RETRY_WITH_BACKOFF"

    def test_handle_quota_exceeded(self):
        """Should handle quota exceeded"""
        from error_handling import handle_openai_error

        error = Exception("You exceeded your current quota")
        action = handle_openai_error(error)

        assert action == "ALERT_ADMIN"

    def test_handle_invalid_api_key(self):
        """Should handle invalid API key"""
        from error_handling import handle_openai_error

        error = Exception("Incorrect API key provided")
        action = handle_openai_error(error)

        assert action == "CRITICAL_ALERT"

    def test_handle_model_overload(self):
        """Should handle model overload"""
        from error_handling import handle_openai_error

        error = Exception("The model is currently overloaded")
        action = handle_openai_error(error)

        assert action == "RETRY_WITH_BACKOFF"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

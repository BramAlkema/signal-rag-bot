#!/usr/bin/env python3
"""
Error Handling and Recovery Module
Implements retry logic, graceful degradation, auto-reconnect, and error logging
"""
import time
import logging
import hashlib
import subprocess
import re
from typing import Callable, Any, Optional, Tuple, Dict
from collections import defaultdict
from datetime import datetime, timedelta


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    retry_exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry function with exponential backoff

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles each retry)
        retry_exceptions: Tuple of exceptions to retry on

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except retry_exceptions as e:
            last_exception = e

            if attempt < max_retries:
                # Exponential backoff: 1, 2, 4, 8...
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                time.sleep(delay)
            else:
                logging.error(f"All {max_retries} retries failed")
                raise

    if last_exception:
        raise last_exception


def get_response_with_fallback(
    rag_func: Callable,
    query: str,
    fallback: str = "I'm experiencing technical difficulties. Please try again later."
) -> str:
    """
    Get RAG response with fallback on failure

    Args:
        rag_func: RAG query function
        query: User query
        fallback: Fallback message

    Returns:
        Response or fallback message
    """
    try:
        result = rag_func(query)

        # Handle partial failures
        if isinstance(result, dict):
            if result.get('error'):
                # Return sources if available, otherwise fallback
                if result.get('sources'):
                    return f"Partial response available. Sources: {', '.join(result['sources'])}\n\n{fallback}"
                return fallback

            if result.get('answer'):
                return result['answer']

        return result if result else fallback

    except Exception as e:
        logging.error(f"RAG failure: {e}")
        return fallback


def receive_with_reconnect(max_retries: int = 3) -> list:
    """
    Receive Signal messages with auto-reconnect

    Args:
        max_retries: Maximum reconnect attempts

    Returns:
        List of messages or empty list on failure
    """
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["signal-cli", "-o", "json", "receive", "-t", "2"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

            # Parse messages
            messages = []
            for line in result.stdout.strip().split('\n'):
                if line and line.startswith('{'):
                    try:
                        import json
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            return messages

        except subprocess.TimeoutExpired:
            logging.warning(f"Signal-cli timeout, attempt {attempt + 1}/{max_retries}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except subprocess.CalledProcessError as e:
            logging.error(f"Signal-cli error: {e}")
            time.sleep(2 ** attempt)
        except Exception as e:
            logging.error(f"Unexpected error receiving messages: {e}")
            break

    return []


def check_signal_cli_health() -> bool:
    """
    Check if signal-cli is healthy

    Returns:
        True if healthy, False otherwise
    """
    try:
        result = subprocess.run(
            ["signal-cli", "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def validate_faiss_index(index, expected_dim: int = 1536) -> Tuple[bool, Optional[str]]:
    """
    Validate FAISS index integrity

    Args:
        index: FAISS index object
        expected_dim: Expected vector dimension

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if index has vectors
        if index.ntotal == 0:
            return False, "Index contains no vectors"

        # Check dimension
        if hasattr(index, 'd') and index.d != expected_dim:
            return False, f"Dimension mismatch: expected {expected_dim}, got {index.d}"

        # Try a test search
        import numpy as np
        test_vector = np.random.rand(1, expected_dim).astype('float32')
        distances, indices = index.search(test_vector, min(5, index.ntotal))

        if distances is None or indices is None:
            return False, "Index search failed"

        return True, None

    except Exception as e:
        return False, f"Index validation error: {str(e)}"


def validate_index_checksum(index_data: bytes, expected_checksum: str) -> bool:
    """
    Validate index file checksum

    Args:
        index_data: Index file data
        expected_checksum: Expected SHA256 checksum

    Returns:
        True if valid, False otherwise
    """
    actual_checksum = hashlib.sha256(index_data).hexdigest()
    return actual_checksum == expected_checksum


def sanitize_error_message(error_msg: str) -> str:
    """
    Sanitize sensitive data from error messages

    Args:
        error_msg: Raw error message

    Returns:
        Sanitized error message
    """
    # Redact API keys (sk-...)
    error_msg = re.sub(r'sk-[a-zA-Z0-9]+', '[REDACTED]', error_msg)

    # Redact phone numbers (+31...)
    error_msg = re.sub(r'\+\d{10,15}', '[PHONE]', error_msg)

    # Redact email addresses
    error_msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', error_msg)

    return error_msg


def log_error_with_context(error: Exception, context: Dict[str, Any]) -> None:
    """
    Log error with context, sanitizing sensitive data

    Args:
        error: Exception object
        context: Context dictionary
    """
    # Sanitize context
    safe_context = {}
    for key, value in context.items():
        if key in ['user', 'phone', 'sender']:
            # Hash user identifiers
            safe_context[key] = hashlib.sha256(str(value).encode()).hexdigest()[:16]
        elif key in ['api_key', 'token', 'password']:
            safe_context[key] = '[REDACTED]'
        else:
            safe_context[key] = value

    # Sanitize error message
    error_msg = sanitize_error_message(str(error))

    # Log with context
    logging.error(
        f"Error: {error_msg} | Context: {safe_context}",
        extra={'context': safe_context}
    )


def categorize_error(error: Exception) -> str:
    """
    Categorize error for metrics and handling

    Args:
        error: Exception object

    Returns:
        Error category string
    """
    error_str = str(error).lower()
    error_type = type(error).__name__

    # API errors
    if 'rate limit' in error_str or error_type == 'RateLimitError':
        return "API_RATE_LIMIT"
    if 'quota' in error_str or 'exceeded your current quota' in error_str:
        return "API_QUOTA_EXCEEDED"
    if 'api key' in error_str or 'authentication' in error_str:
        return "API_AUTH_ERROR"
    if 'overloaded' in error_str:
        return "API_OVERLOAD"

    # Network errors
    if error_type in ['ConnectionError', 'Timeout', 'TimeoutError']:
        return "NETWORK_ERROR"

    # Index errors
    if 'faiss' in error_str or 'index' in error_str:
        return "INDEX_ERROR"

    # Signal errors
    if 'signal-cli' in error_str:
        return "SIGNAL_ERROR"

    return "UNKNOWN_ERROR"


class ErrorMetrics:
    """Track error metrics"""

    def __init__(self):
        self.error_counts = defaultdict(int)
        self.total_errors = 0

    def record_error(self, category: str):
        """Record an error"""
        self.error_counts[category] += 1
        self.total_errors += 1

    def get_count(self, category: str) -> int:
        """Get error count for category"""
        return self.error_counts.get(category, 0)

    def get_total_errors(self) -> int:
        """Get total error count"""
        return self.total_errors

    def reset(self):
        """Reset all metrics"""
        self.error_counts.clear()
        self.total_errors = 0


class ErrorRateMonitor:
    """Monitor error rate and alert on threshold"""

    def __init__(self, threshold: float = 0.1, window_seconds: int = 60):
        """
        Initialize error rate monitor

        Args:
            threshold: Error rate threshold (0.1 = 10%)
            window_seconds: Time window for rate calculation
        """
        self.threshold = threshold
        self.window = timedelta(seconds=window_seconds)
        self.events = []  # List of (timestamp, is_error) tuples

    def record_success(self):
        """Record successful operation"""
        self.events.append((datetime.now(), False))
        self._clean_old_events()

    def record_failure(self):
        """Record failed operation"""
        self.events.append((datetime.now(), True))
        self._clean_old_events()

    def _clean_old_events(self):
        """Remove events outside the time window"""
        cutoff = datetime.now() - self.window
        self.events = [(ts, is_err) for ts, is_err in self.events if ts > cutoff]

    def should_alert(self) -> bool:
        """Check if error rate exceeds threshold"""
        if not self.events:
            return False

        error_count = sum(1 for _, is_err in self.events if is_err)
        total_count = len(self.events)

        error_rate = error_count / total_count if total_count > 0 else 0
        return error_rate > self.threshold


def handle_openai_error(error: Exception) -> str:
    """
    Handle OpenAI-specific errors

    Args:
        error: OpenAI exception

    Returns:
        Action to take
    """
    error_str = str(error).lower()
    error_type = type(error).__name__

    # Rate limit - retry with backoff
    if 'rate limit' in error_str or error_type == 'RateLimitError':
        return "RETRY_WITH_BACKOFF"

    # Quota exceeded - alert admin
    if 'quota' in error_str or 'exceeded your current quota' in error_str:
        return "ALERT_ADMIN"

    # Invalid API key - critical alert
    if 'api key' in error_str or 'incorrect api key' in error_str:
        return "CRITICAL_ALERT"

    # Model overload - retry
    if 'overloaded' in error_str:
        return "RETRY_WITH_BACKOFF"

    # Unknown error
    return "LOG_AND_CONTINUE"


if __name__ == "__main__":
    # Quick manual test
    print("Testing error handling...")

    # Test retry with backoff
    attempt = [0]

    def fail_twice():
        attempt[0] += 1
        if attempt[0] < 3:
            raise Exception("Fail")
        return "success"

    result = retry_with_backoff(fail_twice, max_retries=3)
    assert result == "success"
    print("✓ Retry with backoff working")

    # Test error sanitization
    error_msg = "API error: sk-abc123def456 for user +31612345678"
    sanitized = sanitize_error_message(error_msg)
    assert "sk-abc123def456" not in sanitized
    assert "+31612345678" not in sanitized
    print("✓ Error sanitization working")

    # Test error categorization
    category = categorize_error(Exception("Rate limit exceeded"))
    assert category == "API_RATE_LIMIT"
    print("✓ Error categorization working")

    print("\n✅ All manual tests passed!")

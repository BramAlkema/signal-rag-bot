#!/usr/bin/env python3
"""
Monitoring, logging and audit trail test suite
Tests for structured logging, audit trails, metrics, health checks, and alerting
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
import time
import hashlib
from datetime import datetime


class TestStructuredLogging:
    """Test structured JSON logging"""

    def test_json_log_format(self):
        """Should log in JSON format"""
        from monitoring import StructuredLogger

        logger = StructuredLogger("test")

        with patch('logging.Logger.info') as mock_log:
            logger.log_event("user_message", {
                "user": "+31612345678",
                "message_length": 42
            })

            # Should have been called
            assert mock_log.called

            # Get the logged message
            log_call = mock_log.call_args[0][0]

            # Should be valid JSON
            log_data = json.loads(log_call)
            assert log_data['event'] == "user_message"
            assert 'timestamp' in log_data

    def test_log_rotation_config(self):
        """Should configure log rotation"""
        from monitoring import setup_logging

        config = setup_logging()

        assert config['max_bytes'] == 100 * 1024 * 1024  # 100MB
        assert config['backup_count'] == 7  # 7 days
        assert config['format'] == 'json'


class TestAuditLogger:
    """Test audit logging with privacy protection"""

    def test_hash_user_identifiers(self):
        """Should hash user phone numbers"""
        from monitoring import AuditLogger

        logger = AuditLogger()

        with patch('logging.Logger.info') as mock_log:
            logger.log_user_action(
                user_id="+31612345678",
                action="query",
                details={"query": "test"}
            )

            log_call = mock_log.call_args[0][0]
            log_data = json.loads(log_call)

            # Should contain hashed user ID
            assert 'user_hash' in log_data
            assert '+31612345678' not in str(log_data)

    def test_redact_sensitive_data(self):
        """Should redact API keys and passwords"""
        from monitoring import AuditLogger

        logger = AuditLogger()

        with patch('logging.Logger.info') as mock_log:
            logger.log_event("api_call", {
                "api_key": "sk-abc123",
                "password": "secret123"
            })

            log_call = mock_log.call_args[0][0]
            log_data = json.loads(log_call)

            assert log_data['api_key'] == '[REDACTED]'
            assert log_data['password'] == '[REDACTED]'

    def test_include_timestamp_and_event_type(self):
        """Should include timestamp and event type"""
        from monitoring import AuditLogger

        logger = AuditLogger()

        with patch('logging.Logger.info') as mock_log:
            logger.log_event("test_event", {"key": "value"})

            log_call = mock_log.call_args[0][0]
            log_data = json.loads(log_call)

            assert 'timestamp' in log_data
            assert 'event' in log_data
            assert log_data['event'] == "test_event"


class TestAnomalyDetector:
    """Test anomaly detection"""

    def test_detect_unusual_message_length(self):
        """Should detect unusually long messages"""
        from monitoring import AnomalyDetector

        detector = AnomalyDetector()

        # Train with normal lengths
        for _ in range(100):
            detector.record_message_length(50)

        # Detect anomaly
        is_anomaly = detector.is_anomalous_length(500)
        assert is_anomaly is True

    def test_detect_off_hours_usage(self):
        """Should detect activity during unusual hours"""
        from monitoring import AnomalyDetector

        detector = AnomalyDetector()

        # 3 AM should be off-hours
        with patch('monitoring.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 1, 3, 0, 0)
            is_off_hours = detector.is_off_hours()
            assert is_off_hours is True

        # 2 PM should be normal hours
        with patch('monitoring.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 1, 14, 0, 0)
            is_off_hours = detector.is_off_hours()
            assert is_off_hours is False

    def test_detect_rapid_fire_messages(self):
        """Should detect rapid message bursts"""
        from monitoring import AnomalyDetector

        detector = AnomalyDetector()

        # Record messages in quick succession
        timestamps = [time.time() + i * 0.1 for i in range(20)]

        for ts in timestamps:
            detector.record_message_time(ts)

        is_rapid = detector.is_rapid_fire(window_seconds=5, threshold=15)
        assert is_rapid is True


class TestMetricsCollection:
    """Test metrics collection"""

    def test_collect_message_count(self):
        """Should count total messages"""
        from monitoring import MetricsCollector

        metrics = MetricsCollector()

        for _ in range(10):
            metrics.record_message()

        assert metrics.get_total_messages() == 10

    def test_collect_response_time(self):
        """Should track response times"""
        from monitoring import MetricsCollector

        metrics = MetricsCollector()

        metrics.record_response_time(1.5)
        metrics.record_response_time(2.0)
        metrics.record_response_time(1.8)

        stats = metrics.get_response_time_stats()
        assert stats['count'] == 3
        assert stats['avg'] == pytest.approx(1.77, rel=0.1)
        assert stats['p95'] >= 1.8

    def test_collect_error_rate(self):
        """Should calculate error rate"""
        from monitoring import MetricsCollector

        metrics = MetricsCollector()

        # 90 successful, 10 failed
        for _ in range(90):
            metrics.record_success()
        for _ in range(10):
            metrics.record_error("test_error")

        error_rate = metrics.get_error_rate()
        assert error_rate == pytest.approx(0.1, rel=0.01)  # 10%

    def test_collect_active_users(self):
        """Should track active users"""
        from monitoring import MetricsCollector

        metrics = MetricsCollector()

        metrics.record_user_activity("+31612345678")
        metrics.record_user_activity("+31687654321")
        metrics.record_user_activity("+31612345678")  # Same user

        active_count = metrics.get_active_users(window_minutes=60)
        assert active_count == 2  # Two unique users


class TestHealthCheck:
    """Test health check functionality"""

    def test_check_signal_cli_health(self):
        """Should check if signal-cli is responsive"""
        from monitoring import HealthChecker

        checker = HealthChecker()

        # Mock successful signal-cli
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            health = checker.check_signal_cli()
            assert health['status'] == 'healthy'

    def test_check_faiss_index_health(self):
        """Should check if FAISS index is loaded"""
        from monitoring import HealthChecker

        checker = HealthChecker()

        # Mock index
        mock_index = Mock()
        mock_index.ntotal = 1000

        health = checker.check_faiss_index(mock_index)
        assert health['status'] == 'healthy'
        assert health['vectors'] == 1000

    def test_check_openai_api_health(self):
        """Should check OpenAI API connectivity"""
        from monitoring import HealthChecker

        checker = HealthChecker()

        # Mock successful API call
        with patch('openai.OpenAI') as mock_client:
            mock_instance = Mock()
            mock_instance.models.list.return_value = Mock()
            mock_client.return_value = mock_instance

            health = checker.check_openai_api("sk-test")
            assert health['status'] == 'healthy'

    def test_overall_health_status(self):
        """Should aggregate overall health"""
        from monitoring import HealthChecker

        checker = HealthChecker()

        health_checks = {
            'signal_cli': {'status': 'healthy'},
            'faiss_index': {'status': 'healthy'},
            'openai_api': {'status': 'healthy'}
        }

        overall = checker.aggregate_health(health_checks)
        assert overall['status'] == 'healthy'
        assert overall['all_systems_operational'] is True

    def test_degraded_health_status(self):
        """Should report degraded status when one component fails"""
        from monitoring import HealthChecker

        checker = HealthChecker()

        health_checks = {
            'signal_cli': {'status': 'healthy'},
            'faiss_index': {'status': 'unhealthy', 'error': 'Index corrupted'},
            'openai_api': {'status': 'healthy'}
        }

        overall = checker.aggregate_health(health_checks)
        assert overall['status'] == 'degraded'
        assert overall['all_systems_operational'] is False


class TestAlerting:
    """Test alerting functionality"""

    def test_alert_on_critical_error(self):
        """Should trigger alert on critical error"""
        from monitoring import AlertManager

        alerts = AlertManager()

        with patch.object(alerts, 'send_alert') as mock_send:
            alerts.handle_error(
                error_type="API_AUTH_ERROR",
                severity="critical",
                message="Invalid API key"
            )

            assert mock_send.called
            call_args = mock_send.call_args[1]
            assert call_args['severity'] == 'critical'

    def test_alert_on_high_error_rate(self):
        """Should alert when error rate exceeds threshold"""
        from monitoring import AlertManager

        alerts = AlertManager(error_rate_threshold=0.1)

        with patch.object(alerts, 'send_alert') as mock_send:
            # Simulate high error rate
            alerts.check_error_rate(error_rate=0.15)

            assert mock_send.called

    def test_no_alert_spam(self):
        """Should not send duplicate alerts within cooldown period"""
        from monitoring import AlertManager

        alerts = AlertManager(cooldown_seconds=60)

        with patch.object(alerts, 'send_alert') as mock_send:
            # Send same alert twice quickly
            alerts.handle_error("TEST_ERROR", "high", "Test")
            alerts.handle_error("TEST_ERROR", "high", "Test")

            # Should only have been called once
            assert mock_send.call_count == 1

    def test_alert_channels(self):
        """Should support multiple alert channels"""
        from monitoring import AlertManager

        alerts = AlertManager(channels=['log', 'webhook'])

        with patch('logging.Logger.critical') as mock_log:
            with patch('requests.post') as mock_webhook:
                alerts.send_alert(
                    severity='critical',
                    message='Test alert',
                    channels=['log', 'webhook']
                )

                assert mock_log.called
                assert mock_webhook.called


class TestPrometheusMetrics:
    """Test Prometheus-compatible metrics export"""

    def test_export_counter_metric(self):
        """Should export counter metrics in Prometheus format"""
        from monitoring import PrometheusExporter

        exporter = PrometheusExporter()
        exporter.increment_counter("messages_total", labels={"status": "success"})

        metrics = exporter.export()
        assert "messages_total" in metrics
        assert 'status="success"' in metrics

    def test_export_histogram_metric(self):
        """Should export histogram metrics"""
        from monitoring import PrometheusExporter

        exporter = PrometheusExporter()
        exporter.record_histogram("response_time_seconds", 1.5)

        metrics = exporter.export()
        assert "response_time_seconds" in metrics

    def test_export_gauge_metric(self):
        """Should export gauge metrics"""
        from monitoring import PrometheusExporter

        exporter = PrometheusExporter()
        exporter.set_gauge("active_users", 5)

        metrics = exporter.export()
        assert "active_users 5" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

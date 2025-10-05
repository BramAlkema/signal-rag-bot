#!/usr/bin/env python3
"""
Monitoring, Logging and Audit Trail Module
Implements structured logging, audit trails, metrics collection, health checks, and alerting
"""
import json
import logging
import hashlib
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
import statistics


class StructuredLogger:
    """Structured JSON logger"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_event(self, event: str, data: Dict[str, Any], level: str = "INFO"):
        """Log event in JSON format"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **data
        }

        log_message = json.dumps(log_entry)

        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "DEBUG":
            self.logger.debug(log_message)
        else:
            self.logger.info(log_message)


def setup_logging() -> Dict[str, Any]:
    """
    Setup logging configuration

    Returns:
        Configuration dictionary
    """
    return {
        'max_bytes': 100 * 1024 * 1024,  # 100MB
        'backup_count': 7,  # 7 days
        'format': 'json'
    }


class AuditLogger:
    """Audit logger with privacy protection"""

    def __init__(self):
        self.logger = logging.getLogger('audit')

    def _hash_user_id(self, user_id: str) -> str:
        """Hash user identifier for privacy"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    def _redact_sensitive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive fields"""
        sensitive_keys = ['api_key', 'password', 'token', 'secret']
        redacted = {}

        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                redacted[key] = '[REDACTED]'
            else:
                redacted[key] = value

        return redacted

    def log_user_action(self, user_id: str, action: str, details: Dict[str, Any]):
        """Log user action with privacy protection"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_hash": self._hash_user_id(user_id),
            "action": action,
            **self._redact_sensitive(details)
        }

        self.logger.info(json.dumps(log_entry))

    def log_event(self, event: str, data: Dict[str, Any]):
        """Log general event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **self._redact_sensitive(data)
        }

        self.logger.info(json.dumps(log_entry))


class AnomalyDetector:
    """Detect anomalous behavior patterns"""

    def __init__(self):
        self.message_lengths = deque(maxlen=1000)
        self.message_times = deque(maxlen=1000)
        self.normal_hours = set(range(8, 23))  # 8 AM to 11 PM

    def record_message_length(self, length: int):
        """Record message length for baseline"""
        self.message_lengths.append(length)

    def is_anomalous_length(self, length: int, threshold_std: float = 3.0) -> bool:
        """Detect if message length is anomalous"""
        if len(self.message_lengths) < 10:
            return False

        mean = statistics.mean(self.message_lengths)
        std = statistics.stdev(self.message_lengths)

        # Anomaly if more than threshold_std standard deviations from mean
        return abs(length - mean) > (threshold_std * std)

    def is_off_hours(self) -> bool:
        """Check if current time is outside normal hours"""
        current_hour = datetime.now().hour
        return current_hour not in self.normal_hours

    def record_message_time(self, timestamp: float):
        """Record message timestamp"""
        self.message_times.append(timestamp)

    def is_rapid_fire(self, window_seconds: int = 60, threshold: int = 20) -> bool:
        """Detect rapid message bursts"""
        if not self.message_times:
            return False

        cutoff = time.time() - window_seconds
        recent = [ts for ts in self.message_times if ts > cutoff]

        return len(recent) > threshold


class MetricsCollector:
    """Collect and track metrics"""

    def __init__(self):
        self.message_count = 0
        self.response_times = deque(maxlen=1000)
        self.success_count = 0
        self.error_count = 0
        self.error_types = defaultdict(int)
        self.user_activity = defaultdict(list)

    def record_message(self):
        """Record a message"""
        self.message_count += 1

    def get_total_messages(self) -> int:
        """Get total message count"""
        return self.message_count

    def record_response_time(self, duration: float):
        """Record response time in seconds"""
        self.response_times.append(duration)

    def get_response_time_stats(self) -> Dict[str, float]:
        """Get response time statistics"""
        if not self.response_times:
            return {'count': 0, 'avg': 0, 'p95': 0}

        sorted_times = sorted(self.response_times)
        p95_index = int(len(sorted_times) * 0.95)

        return {
            'count': len(self.response_times),
            'avg': statistics.mean(self.response_times),
            'p95': sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        }

    def record_success(self):
        """Record successful operation"""
        self.success_count += 1

    def record_error(self, error_type: str):
        """Record error"""
        self.error_count += 1
        self.error_types[error_type] += 1

    def get_error_rate(self) -> float:
        """Calculate error rate"""
        total = self.success_count + self.error_count
        if total == 0:
            return 0.0
        return self.error_count / total

    def record_user_activity(self, user_id: str):
        """Record user activity"""
        self.user_activity[user_id].append(time.time())

    def get_active_users(self, window_minutes: int = 60) -> int:
        """Get count of active users in time window"""
        cutoff = time.time() - (window_minutes * 60)
        active = set()

        for user_id, timestamps in self.user_activity.items():
            if any(ts > cutoff for ts in timestamps):
                active.add(user_id)

        return len(active)


class HealthChecker:
    """System health checker"""

    def check_signal_cli(self) -> Dict[str, Any]:
        """Check signal-cli health"""
        try:
            result = subprocess.run(
                ["signal-cli", "--version"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                return {'status': 'healthy', 'component': 'signal_cli'}
            else:
                return {'status': 'unhealthy', 'component': 'signal_cli', 'error': 'Non-zero exit code'}

        except Exception as e:
            return {'status': 'unhealthy', 'component': 'signal_cli', 'error': str(e)}

    def check_faiss_index(self, index) -> Dict[str, Any]:
        """Check FAISS index health"""
        try:
            if index.ntotal == 0:
                return {'status': 'unhealthy', 'component': 'faiss_index', 'error': 'No vectors in index'}

            return {
                'status': 'healthy',
                'component': 'faiss_index',
                'vectors': index.ntotal
            }

        except Exception as e:
            return {'status': 'unhealthy', 'component': 'faiss_index', 'error': str(e)}

    def check_openai_api(self, api_key: str) -> Dict[str, Any]:
        """Check OpenAI API connectivity"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            # Try to list models (lightweight operation)
            client.models.list()

            return {'status': 'healthy', 'component': 'openai_api'}

        except Exception as e:
            return {'status': 'unhealthy', 'component': 'openai_api', 'error': str(e)}

    def aggregate_health(self, health_checks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate overall health status"""
        all_healthy = all(check['status'] == 'healthy' for check in health_checks.values())

        if all_healthy:
            return {
                'status': 'healthy',
                'all_systems_operational': True,
                'checks': health_checks
            }
        else:
            return {
                'status': 'degraded',
                'all_systems_operational': False,
                'checks': health_checks
            }


class AlertManager:
    """Alert manager with cooldown and multiple channels"""

    def __init__(self, error_rate_threshold: float = 0.1, cooldown_seconds: int = 300, channels: List[str] = None):
        self.error_rate_threshold = error_rate_threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_alerts = {}  # error_type -> timestamp
        self.channels = channels or ['log']  # Default to logging

    def handle_error(self, error_type: str, severity: str, message: str):
        """Handle error and send alert if needed"""
        # Check cooldown
        if error_type in self.last_alerts:
            time_since_last = time.time() - self.last_alerts[error_type]
            if time_since_last < self.cooldown_seconds:
                return  # Skip alert during cooldown

        # Send alert
        self.send_alert(severity=severity, message=message, error_type=error_type)
        self.last_alerts[error_type] = time.time()

    def check_error_rate(self, error_rate: float):
        """Check if error rate exceeds threshold"""
        if error_rate > self.error_rate_threshold:
            self.send_alert(
                severity='high',
                message=f"Error rate {error_rate:.1%} exceeds threshold {self.error_rate_threshold:.1%}",
                error_type='HIGH_ERROR_RATE'
            )

    def send_alert(self, severity: str, message: str, error_type: str = None, channels: List[str] = None):
        """Send alert through configured channels"""
        if channels is None:
            channels = self.channels

        alert_data = {
            'severity': severity,
            'message': message,
            'error_type': error_type,
            'timestamp': datetime.utcnow().isoformat()
        }

        for channel in channels:
            if channel == 'log':
                if severity == 'critical':
                    logging.critical(json.dumps(alert_data))
                elif severity == 'high':
                    logging.error(json.dumps(alert_data))
                else:
                    logging.warning(json.dumps(alert_data))

            elif channel == 'webhook':
                # Webhook integration
                try:
                    import requests
                    webhook_url = "http://localhost/alerts"  # Configurable
                    requests.post(webhook_url, json=alert_data)
                except Exception as e:
                    logging.warning(f"Failed to send webhook alert: {e}")


class PrometheusExporter:
    """Export metrics in Prometheus format"""

    def __init__(self):
        self.counters = defaultdict(int)
        self.histograms = defaultdict(list)
        self.gauges = {}

    def increment_counter(self, name: str, labels: Dict[str, str] = None):
        """Increment counter metric"""
        label_str = self._format_labels(labels) if labels else ""
        key = f"{name}{label_str}"
        self.counters[key] += 1

    def record_histogram(self, name: str, value: float):
        """Record histogram value"""
        self.histograms[name].append(value)

    def set_gauge(self, name: str, value: float):
        """Set gauge value"""
        self.gauges[name] = value

    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus"""
        if not labels:
            return ""
        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(label_pairs) + "}"

    def export(self) -> str:
        """Export all metrics in Prometheus text format"""
        lines = []

        # Export counters
        for key, value in self.counters.items():
            lines.append(f"{key} {value}")

        # Export gauges
        for name, value in self.gauges.items():
            lines.append(f"{name} {value}")

        # Export histograms (simplified - just count and sum)
        for name, values in self.histograms.items():
            if values:
                lines.append(f"{name}_count {len(values)}")
                lines.append(f"{name}_sum {sum(values)}")

        return "\n".join(lines)


if __name__ == "__main__":
    # Quick manual test
    print("Testing monitoring...")

    # Test structured logger
    logger = StructuredLogger("test")
    logger.log_event("test_event", {"key": "value"})
    print("✓ Structured logger working")

    # Test audit logger
    audit = AuditLogger()
    audit.log_user_action("+31612345678", "query", {"api_key": "sk-test"})
    print("✓ Audit logger working")

    # Test metrics
    metrics = MetricsCollector()
    metrics.record_message()
    metrics.record_response_time(1.5)
    assert metrics.get_total_messages() == 1
    print("✓ Metrics collector working")

    # Test anomaly detector
    detector = AnomalyDetector()
    for _ in range(100):
        detector.record_message_length(50)
    assert detector.is_anomalous_length(500) is True
    print("✓ Anomaly detector working")

    print("\n✅ All manual tests passed!")

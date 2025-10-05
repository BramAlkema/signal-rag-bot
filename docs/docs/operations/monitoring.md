# Monitoring Guide

Comprehensive monitoring and observability for Signal RAG Bot.

---

## Overview

Signal RAG Bot includes built-in monitoring capabilities:

- 📊 **Structured Logging**: JSON logs with privacy protection
- 📈 **Metrics Collection**: Prometheus-compatible metrics
- 🔔 **Alerting**: Critical error notifications
- 🏥 **Health Checks**: Container health validation
- 🔍 **Audit Trail**: Security event logging

---

## Logging

### Log Levels

```python
import logging

# Configure log level via environment variable
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Development, troubleshooting | Variable values, function calls |
| **INFO** | Normal operations | Message received, query processed |
| **WARNING** | Recoverable issues | Rate limit exceeded, retry attempt |
| **ERROR** | Errors requiring attention | API call failed, invalid input |
| **CRITICAL** | Service-impacting failures | API key invalid, index corrupted |

### Structured Logging

All logs are output in structured JSON format:

```json
{
  "timestamp": "2025-10-05T14:23:45.123Z",
  "level": "INFO",
  "event": "message_received",
  "user_id_hash": "a1b2c3d4",
  "message_length": 42,
  "activated": true
}
```

### Log Rotation

Logs are automatically rotated to prevent disk space issues:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/bot.log',
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5  # Keep 5 backup files
)
```

**Configuration:**
- Max size: 10MB per file
- Backup count: 5 files
- Total disk usage: ~50MB

### Sensitive Data Redaction

All logs automatically redact sensitive information:

```python
# monitoring.py:45
class AuditLogger:
    def log_event(self, event_type: str, user_id: str, **kwargs):
        # Hash user ID
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]

        # Redact API keys
        if 'api_key' in kwargs:
            kwargs['api_key'] = '[REDACTED]'

        # Redact phone numbers
        if 'phone' in kwargs:
            kwargs['phone'] = f"+***{kwargs['phone'][-4:]}"

        self.logger.info(json.dumps({
            'timestamp': time.time(),
            'event': event_type,
            'user_hash': user_hash,
            **kwargs
        }))
```

### Viewing Logs

**Docker Compose:**
```bash
# Follow logs in real-time
docker-compose logs -f signal-rag-bot

# Last 100 lines
docker-compose logs --tail 100 signal-rag-bot

# Logs since 1 hour ago
docker-compose logs --since 1h signal-rag-bot

# Search logs for errors
docker-compose logs signal-rag-bot | grep ERROR
```

**Log Files:**
```bash
# View structured logs
tail -f logs/bot.log | jq '.'

# Filter by event type
cat logs/bot.log | jq 'select(.event == "message_received")'

# Count events by type
cat logs/bot.log | jq -r '.event' | sort | uniq -c
```

---

## Metrics

### Metrics Collection

The bot collects these metrics:

**Message Metrics:**
```python
{
    "messages_received_total": 1523,      # Counter
    "messages_processed_total": 1498,     # Counter
    "messages_failed_total": 25,          # Counter
    "active_users": 42,                   # Gauge
}
```

**Performance Metrics:**
```python
{
    "response_time_seconds": {            # Histogram
        "p50": 2.1,
        "p95": 4.8,
        "p99": 6.2
    },
    "rag_search_latency_seconds": {       # Histogram
        "p50": 0.05,
        "p95": 0.12,
        "p99": 0.18
    }
}
```

**RAG Metrics:**
```python
{
    "index_size_chunks": 250,             # Gauge
    "index_size_bytes": 10485760,         # Gauge
    "embeddings_created_total": 250,      # Counter
    "searches_performed_total": 1498,     # Counter
}
```

**API Metrics:**
```python
{
    "openai_api_calls_total": 1748,       # Counter
    "openai_api_errors_total": 12,        # Counter
    "openai_tokens_used_total": 125430,   # Counter
}
```

### Metrics Export

**Prometheus Format:**
```python
# monitoring.py:178
class MetricsCollector:
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        for metric, value in self.metrics.items():
            lines.append(f"# HELP {metric}")
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {value}")

        return "\n".join(lines)
```

**HTTP Endpoint:**
```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            metrics = collector.export_prometheus()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics.encode())

# Start metrics server on port 9090
server = HTTPServer(('0.0.0.0', 9090), MetricsHandler)
server.serve_forever()
```

**Access metrics:**
```bash
curl http://localhost:9090/metrics
```

### Grafana Dashboard

Import the provided Grafana dashboard:

```json
{
  "dashboard": {
    "title": "Signal RAG Bot",
    "panels": [
      {
        "title": "Messages per Minute",
        "targets": [{
          "expr": "rate(messages_received_total[1m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, response_time_seconds)"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(messages_failed_total[5m])"
        }]
      }
    ]
  }
}
```

---

## Alerting

### Alert Configuration

Configure alerts for critical events:

```python
# monitoring.py:289
class AlertManager:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.alert_history = deque(maxlen=100)

    def send_alert(self, severity: str, message: str):
        """Send alert via webhook"""
        alert = {
            'timestamp': time.time(),
            'severity': severity,
            'message': message,
            'service': 'signal-rag-bot'
        }

        if self.webhook_url:
            requests.post(self.webhook_url, json=alert)

        self.alert_history.append(alert)
```

### Alert Rules

**Critical Alerts (P0):**
```python
# API key invalid
if 'invalid_api_key' in error_message:
    alert_manager.send_alert('critical', 'OpenAI API key is invalid')

# Signal disconnected
if not signal_cli_responsive():
    alert_manager.send_alert('critical', 'signal-cli not responding')

# Disk space low
if disk_space_gb < 1:
    alert_manager.send_alert('critical', f'Disk space low: {disk_space_gb}GB')
```

**High Priority Alerts (P1):**
```python
# High error rate
if error_rate > 0.10:  # 10%
    alert_manager.send_alert('high', f'Error rate: {error_rate:.1%}')

# OpenAI quota warning
if openai_usage_percent > 80:
    alert_manager.send_alert('high', f'OpenAI quota: {openai_usage_percent}%')
```

**Medium Priority Alerts (P2):**
```python
# Suspicious activity
if anomaly_detected:
    alert_manager.send_alert('medium', f'Anomaly: {anomaly_type}')

# Memory usage high
if memory_usage_percent > 80:
    alert_manager.send_alert('medium', f'Memory usage: {memory_usage_percent}%')
```

### Alert Channels

**Slack Webhook:**
```python
# Configure Slack webhook
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

alert_manager = AlertManager(webhook_url=SLACK_WEBHOOK_URL)
alert_manager.send_alert('critical', 'API key invalid')
```

**Discord Webhook:**
```python
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def send_discord_alert(message: str):
    payload = {
        'content': f'🚨 {message}',
        'username': 'Signal RAG Bot'
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
```

**Email (SMTP):**
```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject: str, message: str):
    msg = MIMEText(message)
    msg['Subject'] = f'[ALERT] {subject}'
    msg['From'] = 'bot@example.com'
    msg['To'] = 'admin@example.com'

    with smtplib.SMTP('smtp.example.com') as server:
        server.send_message(msg)
```

---

## Health Checks

### Container Health Check

The Docker image includes a comprehensive health check:

```bash
#!/bin/bash
# docker/healthcheck.sh

# Check Python process
pgrep -f "python.*signal_bot" || exit 1

# Check signal-cli
signal-cli --version || exit 1

# Check FAISS index
[ -f "/app/rag_faiss.index" ] || exit 1

# Check environment variables
[ -n "$OPENAI_API_KEY" ] || exit 1
[ -n "$SIGNAL_PHONE_NUMBER" ] || exit 1

# Check disk space
df -h / | awk 'NR==2 {print $4}' | grep -q "G$" || exit 1

exit 0
```

### Health Check Status

```bash
# View health status
docker inspect signal-rag-bot | jq '.[0].State.Health'

# Output:
{
  "Status": "healthy",
  "FailingStreak": 0,
  "Log": [
    {
      "Start": "2025-10-05T14:30:00Z",
      "End": "2025-10-05T14:30:01Z",
      "ExitCode": 0,
      "Output": "[HEALTH] ✓ All checks passed\n"
    }
  ]
}
```

### Application Health Endpoint

```python
def health_check() -> dict:
    """Internal health check"""
    checks = {
        'signal_cli': check_signal_cli(),
        'faiss_index': check_faiss_index(),
        'openai_api': check_openai_api(),
        'disk_space': check_disk_space(),
        'memory': check_memory_usage()
    }

    all_healthy = all(checks.values())

    return {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks,
        'timestamp': time.time()
    }
```

---

## Audit Trail

### Security Event Logging

```python
# monitoring.py:45
class AuditLogger:
    def log_activation_attempt(self, user_id: str, success: bool):
        self.log_event('activation_attempt', user_id, success=success)

    def log_rate_limit_exceeded(self, user_id: str, limit_type: str):
        self.log_event('rate_limit_exceeded', user_id, limit_type=limit_type)

    def log_suspicious_input(self, user_id: str, pattern: str):
        self.log_event('suspicious_input', user_id, pattern=pattern)

    def log_query(self, user_id: str, query_length: int, response_time: float):
        self.log_event('query_processed', user_id,
                      query_length=query_length,
                      response_time=response_time)
```

### Audit Log Format

```json
{
  "timestamp": 1696512225.123,
  "event": "activation_attempt",
  "user_hash": "a1b2c3d4e5f6g7h8",
  "success": false,
  "ip_hash": "x1y2z3a4b5c6d7e8"
}
```

### Compliance Reporting

```python
# Generate compliance report
def generate_audit_report(start_date: str, end_date: str) -> dict:
    """Generate audit report for compliance"""
    events = load_audit_logs(start_date, end_date)

    report = {
        'period': f"{start_date} to {end_date}",
        'total_events': len(events),
        'events_by_type': Counter(e['event'] for e in events),
        'unique_users': len(set(e['user_hash'] for e in events)),
        'failed_activations': sum(1 for e in events
                                  if e['event'] == 'activation_attempt'
                                  and not e['success']),
        'suspicious_activity': sum(1 for e in events
                                   if e['event'] == 'suspicious_input')
    }

    return report
```

---

## Monitoring Best Practices

### 1. Set Up Alerts

```bash
# Configure webhook in .env
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/..." >> .env

# Restart to apply
docker-compose restart
```

### 2. Monitor Disk Space

```bash
# Check disk usage
df -h /var/lib/docker/volumes

# Set up cron for cleanup
crontab -e
# 0 2 * * * docker system prune -af --volumes --filter "until=168h"
```

### 3. Review Logs Daily

```bash
# Check for errors
docker-compose logs --since 24h signal-rag-bot | grep ERROR

# Check for warnings
docker-compose logs --since 24h signal-rag-bot | grep WARNING
```

### 4. Track Metrics Trends

```bash
# Export metrics to file
curl http://localhost:9090/metrics > metrics-$(date +%Y%m%d).txt

# Compare over time
diff metrics-20251001.txt metrics-20251005.txt
```

### 5. Test Alerts

```bash
# Trigger test alert
docker exec signal-rag-bot python -c "
from monitoring import AlertManager
alert = AlertManager(webhook_url='$SLACK_WEBHOOK_URL')
alert.send_alert('medium', 'Test alert - please ignore')
"
```

---

## Troubleshooting

### High Memory Usage

```bash
# Check memory stats
docker stats signal-rag-bot --no-stream

# Reduce chunk size
docker exec signal-rag-bot env CHUNK_SIZE=500 python signal_bot_rag.py
```

### Logs Not Rotating

```bash
# Check log rotation
ls -lh logs/

# Force rotation
docker exec signal-rag-bot python -c "
import logging.handlers
handler = logging.handlers.RotatingFileHandler('logs/bot.log')
handler.doRollover()
"
```

### Metrics Not Updating

```bash
# Check metrics collector
docker exec signal-rag-bot python -c "
from monitoring import MetricsCollector
collector = MetricsCollector()
print(collector.export_prometheus())
"
```

---

## Next Steps

- 📊 [Health Checks](health-checks.md) - Detailed health check configuration
- 🔧 [Troubleshooting](troubleshooting.md) - Common issues and solutions
- 💾 [Backup & Restore](backup-restore.md) - Data protection procedures

---

## Reference

- [Monitoring Module Source](https://github.com/BramAlkema/signal-rag-bot/blob/main/monitoring.py)
- [Health Check Script](https://github.com/BramAlkema/signal-rag-bot/blob/main/docker/healthcheck.sh)
- [Metrics Tests](https://github.com/BramAlkema/signal-rag-bot/blob/main/tests/test_monitoring.py)

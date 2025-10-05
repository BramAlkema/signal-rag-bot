# Signal RAG Bot - Technical Specifications

**Version:** 1.0.0
**Last Updated:** 2025-10-05
**Status:** Production-Ready Candidate

---

## 1. System Overview

### 1.1 Purpose
A production-grade Signal messenger chatbot that provides intelligent Q&A using RAG (Retrieval-Augmented Generation) over a custom knowledge base, with emphasis on security, reliability, and deployability.

### 1.2 Architecture
```
┌─────────────────┐
│  Signal Users   │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │   signal-cli         │
    │  (Linked Device)     │
    └────┬─────────────────┘
         │
    ┌────▼─────────────────┐
    │  Signal Bot Process  │
    │  - Message Router    │
    │  - Auth Manager      │
    │  - RAG Engine        │
    └────┬─────────────────┘
         │
    ┌────▼─────────────────┐
    │   Custom RAG Stack   │
    │  - FAISS Index       │
    │  - OpenAI Embeddings │
    │  - Chat Completions  │
    └──────────────────────┘
```

---

## 2. Security Requirements

### 2.1 Authentication & Authorization

**REQ-SEC-001**: Passphrase-based activation
- Users must provide exact passphrase: "Activate Oracle"
- Case-sensitive, whitespace-trimmed
- One-time activation per session
- No response to non-activated users

**REQ-SEC-002**: User authorization list (optional)
- Environment variable `AUTHORIZED_USERS` (comma-separated phone numbers)
- Empty = allow all (after activation)
- Non-empty = whitelist only

**REQ-SEC-003**: Rate limiting
- Max 10 messages per user per minute
- Max 100 messages per user per hour
- HTTP 429-style backoff responses

**REQ-SEC-004**: Input validation
- Sanitize all incoming messages
- Max message length: 2000 characters
- Strip potential command injection attempts
- Log suspicious patterns

### 2.2 Data Security

**REQ-SEC-005**: Secrets management
- All secrets via environment variables
- No hardcoded credentials
- `.env` file excluded from git
- Docker secrets support

**REQ-SEC-006**: API key protection
- OpenAI API key rotation support
- Key validation on startup
- Graceful handling of quota exceeded
- Alert on unauthorized usage patterns

**REQ-SEC-007**: Knowledge base privacy
- PDF content excluded from version control
- Metadata-only sharing in repository
- Encrypted storage option for sensitive docs
- Access logging for audit trails

**REQ-SEC-008**: Session security
- Activation state persists in-memory only
- Session timeout: 24 hours of inactivity
- Clear sessions on restart (by design)
- No persistent user data storage

---

## 3. Robustness Requirements

### 3.1 Error Handling

**REQ-ROB-001**: Graceful degradation
- Continue operation on single message failure
- Retry failed API calls (3 attempts, exponential backoff)
- Fallback responses on RAG failure
- Never crash the entire bot process

**REQ-ROB-002**: Signal-cli resilience
- Auto-reconnect on signal-cli timeout
- Handle malformed JSON from signal-cli
- Detect and recover from signal-cli crashes
- Log all signal-cli errors

**REQ-ROB-003**: OpenAI API resilience
- Handle rate limits (429) gracefully
- Detect quota exhaustion
- Timeout protection (30s per request)
- Circuit breaker pattern for repeated failures

**REQ-ROB-004**: FAISS index resilience
- Validate index integrity on load
- Graceful handling of corrupted index
- Automatic index rebuild capability
- Index version compatibility checks

### 3.2 Resource Management

**REQ-ROB-005**: Memory management
- Max conversation history: 5 messages per user
- Periodic cleanup of inactive users (1 hour)
- FAISS index memory limits enforced
- Memory leak detection and alerts

**REQ-ROB-006**: Disk space management
- Log rotation (max 100MB, 7 days retention)
- Temp file cleanup
- Index size monitoring
- Alert on low disk space (<1GB)

**REQ-ROB-007**: Network resilience
- Handle network interruptions
- Retry DNS failures
- Connection pooling for API calls
- Timeout on all network operations

---

## 4. Testing Requirements

### 4.1 Unit Tests

**REQ-TEST-001**: Core components coverage
- `custom_rag.py`: 90% code coverage
- `signal_bot_rag.py`: 80% code coverage
- All utility functions: 100% coverage
- Mocked external dependencies

**REQ-TEST-002**: Test isolation
- No network calls in unit tests
- Mock signal-cli responses
- Mock OpenAI API responses
- Pytest fixtures for common setups

### 4.2 Integration Tests

**REQ-TEST-003**: End-to-end message flow
- Activation passphrase → welcome message
- Query → RAG response → sources
- Invalid user → silent ignore
- Rate limiting enforcement

**REQ-TEST-004**: RAG pipeline testing
- PDF → extraction → chunking → indexing
- Query → embedding → search → response
- Source URL mapping validation
- Response quality metrics

### 4.3 Performance Tests

**REQ-TEST-005**: Load testing
- 100 concurrent users
- 1000 messages/hour sustained
- Response time: p95 < 5 seconds
- Memory usage stable over 24 hours

**REQ-TEST-006**: Index performance
- Search latency: p95 < 100ms
- Index load time: < 10 seconds
- Embedding generation: < 2s per batch
- Graceful degradation under load

### 4.4 Security Tests

**REQ-TEST-007**: Security validation
- Injection attack resistance (SQL, command, XSS)
- Rate limiting enforcement
- Authorization bypass attempts
- API key leakage detection

---

## 5. Installation Requirements

### 5.1 Dependencies

**REQ-INST-001**: System requirements
- OS: Linux (Ubuntu 20.04+), macOS (12+)
- Python: 3.11+
- Java: OpenJDK 17+ (for signal-cli)
- Disk: 2GB minimum
- RAM: 2GB minimum

**REQ-INST-002**: Python dependencies
```
openai>=1.0.0
numpy>=1.24.0
faiss-cpu>=1.7.4
pypdf2>=3.0.0
tiktoken>=0.5.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

**REQ-INST-003**: External tools
- signal-cli 0.11.0+
- Docker 24.0+ (for containerized deployment)
- Docker Compose 2.0+ (for orchestration)

### 5.2 Setup Process

**REQ-INST-004**: Automated installation
- Single setup script: `./setup.sh`
- Dependency checking and validation
- Interactive configuration wizard
- Health check after installation

**REQ-INST-005**: Configuration
- `.env.example` template provided
- Environment variable validation
- Configuration validation on startup
- Clear error messages for missing config

**REQ-INST-006**: Signal linking
- Clear instructions for device linking
- QR code display in terminal
- Validation of successful link
- Backup/restore of signal-cli data

---

## 6. Docker Requirements

### 6.1 Container Design

**REQ-DOCK-001**: Multi-stage build
- Build stage: Compile dependencies
- Runtime stage: Minimal production image
- Base image: `python:3.11-slim`
- Total image size: < 500MB

**REQ-DOCK-002**: Volume management
```
- signal-data:/root/.local/share/signal-cli (persistent)
- rag-index:/app/index (persistent)
- logs:/app/logs (ephemeral, optional)
```

**REQ-DOCK-003**: Health checks
- Endpoint: `/_health` (internal)
- Checks: Signal connection, FAISS index, OpenAI API
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

**REQ-DOCK-004**: Environment configuration
- All config via environment variables
- Secrets via Docker secrets or env file
- No rebuild required for config changes
- Validation on container startup

### 6.2 Orchestration

**REQ-DOCK-005**: Docker Compose support
```yaml
services:
  signal-rag-bot:
    build: .
    environment:
      - OPENAI_API_KEY
      - SIGNAL_PHONE_NUMBER
      - ACTIVATION_PASSPHRASE
    volumes:
      - signal-data:/root/.local/share/signal-cli
      - rag-index:/app/index
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
```

**REQ-DOCK-006**: Kubernetes compatibility
- StatefulSet for persistent storage
- ConfigMap for configuration
- Secret for credentials
- Service for internal health checks
- PersistentVolumeClaim for signal-data

---

## 7. Monitoring & Observability

### 7.1 Logging

**REQ-MON-001**: Structured logging
- Format: JSON with timestamps
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log rotation: 100MB max, 7 days retention
- Sensitive data redaction (phone numbers, API keys)

**REQ-MON-002**: Log content
```json
{
  "timestamp": "2025-10-05T14:23:45Z",
  "level": "INFO",
  "event": "message_received",
  "user_id_hash": "abc123",
  "activated": true,
  "message_length": 42
}
```

### 7.2 Metrics

**REQ-MON-003**: Key metrics
- Messages received/processed/failed (counter)
- Response time (histogram)
- RAG search latency (histogram)
- OpenAI API calls/errors (counter)
- Active users (gauge)
- Index size/chunks (gauge)

**REQ-MON-004**: Metrics export
- Prometheus-compatible endpoint: `/metrics`
- StatsD support (optional)
- CloudWatch support (optional)

### 7.3 Alerting

**REQ-MON-005**: Critical alerts
- Signal-cli disconnection
- OpenAI API quota exceeded
- FAISS index corruption
- Disk space < 1GB
- Error rate > 10%

---

## 8. Performance Requirements

### 8.1 Response Time

**REQ-PERF-001**: Latency targets
- Activation response: < 1 second
- RAG query (cold): < 5 seconds
- RAG query (warm): < 3 seconds
- Command response: < 500ms

**REQ-PERF-002**: Throughput
- Concurrent users: 100
- Messages/hour: 1000
- Sustained operation: 30 days

### 8.2 Resource Limits

**REQ-PERF-003**: Memory usage
- Base memory: < 500MB
- Per-user overhead: < 1MB
- FAISS index: < 1GB
- Peak memory: < 2GB

**REQ-PERF-004**: CPU usage
- Idle: < 5%
- Per query: < 50% (single core)
- Embedding generation: < 100% (single core)

---

## 9. Deployment Requirements

### 9.1 Deployment Targets

**REQ-DEPLOY-001**: Supported platforms
- Local development (macOS/Linux)
- Docker container (Linux)
- Cloud VPS (DigitalOcean, AWS EC2, etc.)
- Kubernetes cluster

**REQ-DEPLOY-002**: Deployment process
- Zero-downtime updates (optional)
- Rollback capability
- Configuration validation before deploy
- Health check before routing traffic

### 9.2 Backup & Recovery

**REQ-DEPLOY-003**: Backup strategy
- Signal-cli data: Daily backup
- FAISS index: On rebuild only
- Configuration: Version controlled
- Logs: 7-day retention

**REQ-DEPLOY-004**: Recovery procedures
- Documented recovery steps
- Automated restore script
- RTO (Recovery Time Objective): < 1 hour
- RPO (Recovery Point Objective): < 24 hours

---

## 10. Compliance & Governance

### 10.1 Data Privacy

**REQ-COMP-001**: GDPR compliance
- No personal data stored persistently
- User data retention: In-memory only
- Right to be forgotten: Restart clears all data
- Data processing transparency: Clear in `/help`

**REQ-COMP-002**: Audit trail
- Message counts (anonymized)
- API usage tracking
- Security events logged
- No message content retention

### 10.2 Licensing

**REQ-COMP-003**: Open source licensing
- License: MIT
- Third-party license compatibility
- License file in repository
- Attribution for dependencies

---

## 11. Documentation Requirements

### 11.1 User Documentation

**REQ-DOC-001**: User guides
- Getting started guide
- Installation instructions (local + Docker)
- Usage examples
- Troubleshooting guide
- FAQ

### 11.2 Developer Documentation

**REQ-DOC-002**: Technical documentation
- Architecture diagrams
- API documentation
- Code comments (docstrings)
- Contributing guidelines
- Development setup

### 11.3 Operations Documentation

**REQ-DOC-003**: Operational guides
- Deployment playbook
- Monitoring setup
- Backup/restore procedures
- Incident response runbook
- Performance tuning guide

---

## 12. Quality Assurance

### 12.1 Code Quality

**REQ-QA-001**: Code standards
- PEP 8 compliance (Python)
- Type hints for all functions
- Maximum function length: 50 lines
- Maximum file length: 500 lines
- Cyclomatic complexity: < 10

**REQ-QA-002**: Code review
- All changes require review
- Automated linting (flake8, black)
- Security scanning (bandit)
- Dependency vulnerability scanning

### 12.2 Continuous Integration

**REQ-QA-003**: CI/CD pipeline
- Automated testing on every commit
- Code coverage reporting
- Docker image building
- Security scanning
- Performance regression tests

---

## 13. Acceptance Criteria

### 13.1 Functional Acceptance

**REQ-ACC-001**: Core functionality
- ✅ Passphrase activation works
- ✅ RAG responses are accurate
- ✅ Source URLs are clickable
- ✅ Commands (/help, /info, /reset) work
- ✅ Rate limiting enforced

### 13.2 Non-Functional Acceptance

**REQ-ACC-002**: Quality metrics
- ✅ Test coverage > 80%
- ✅ No critical security vulnerabilities
- ✅ Response time p95 < 5s
- ✅ Uptime > 99% over 7 days
- ✅ Docker image builds successfully

### 13.3 Production Readiness

**REQ-ACC-003**: Production checklist
- ✅ Documentation complete
- ✅ Monitoring configured
- ✅ Backup/restore tested
- ✅ Load testing passed
- ✅ Security audit completed

---

## 14. Known Limitations

### 14.1 Current Constraints

**LIM-001**: Signal-cli limitations
- Linked device mode only (no standalone number)
- No group message support (yet)
- No media file sending
- Requires active primary device

**LIM-002**: RAG limitations
- Context window: ~3 chunks per query
- No multi-turn reasoning across queries
- English + Dutch only (embedding model limitation)
- No real-time knowledge updates

**LIM-003**: Scalability limits
- Single-instance deployment (no horizontal scaling)
- In-memory user sessions (lost on restart)
- FAISS index size limited by RAM
- OpenAI API rate limits apply

---

## 15. Future Enhancements

### 15.1 Planned Features

**FUTURE-001**: Advanced features
- Multi-language support
- Voice message transcription
- Image/PDF upload for analysis
- Group chat support
- Multi-user conversations

**FUTURE-002**: Scalability improvements
- Redis for distributed sessions
- PostgreSQL for persistent storage
- Multi-instance deployment with load balancing
- Async message processing queue

**FUTURE-003**: Advanced RAG
- Hybrid search (BM25 + vector)
- Re-ranking with cross-encoders
- Query expansion and refinement
- Multi-hop reasoning
- Citation validation

---

## Appendix A: Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `SIGNAL_PHONE_NUMBER` | Yes | - | Signal phone number (E.164 format) |
| `ACTIVATION_PASSPHRASE` | No | "Activate Oracle" | Required passphrase |
| `AUTHORIZED_USERS` | No | "" | Comma-separated phone numbers |
| `MAX_TOKENS` | No | 200 | Max response tokens |
| `CHUNK_SIZE` | No | 1000 | Text chunk size |
| `CHUNK_OVERLAP` | No | 200 | Chunk overlap size |
| `SEARCH_K` | No | 3 | Number of chunks to retrieve |
| `LOG_LEVEL` | No | INFO | Logging level |

---

## Appendix B: File Structure

```
signal-rag-bot/
├── signal_bot_rag.py          # Main bot application
├── custom_rag.py              # Custom RAG implementation
├── extract_structured.py      # PDF extraction
├── create_proper_buckets.py   # Bucket creation
├── extract_pdf_metadata.py    # Metadata extraction
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git exclusions
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Orchestration
├── setup.sh                   # Installation script
├── tests/
│   ├── test_rag.py
│   ├── test_bot.py
│   └── test_integration.py
├── docs/
│   ├── SPECIFICATIONS.md      # This file
│   ├── INSTALLATION.md
│   ├── DEPLOYMENT.md
│   └── API.md
└── README.md                  # Project overview
```

---

## Appendix C: API Reference

### Custom RAG API

```python
class CustomRAG:
    def __init__(self, bucket_dir: str = "output_v3")
    def load_index(self) -> None
    def search(self, query: str, k: int = 5) -> List[Dict]
    def query(self, question: str, k: int = 3) -> str
```

### Bot Functions

```python
def send_signal_message(recipient: str, message: str, preview_url: str = None) -> bool
def receive_signal_messages() -> List[Dict]
def get_rag_response(user_message: str, sender: str) -> str
def process_messages() -> None
```

---

**Document Version:** 1.0.0
**Status:** Draft → Review → **Approved**
**Next Review Date:** 2025-11-05

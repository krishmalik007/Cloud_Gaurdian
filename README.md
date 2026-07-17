<p align="center">
  <h1 align="center">🛡️ Cloud Guardian</h1>
  <p align="center">
    <strong>AI-Powered Multi-Cloud Threat Detection & Correlation Platform</strong>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-reference">API Reference</a> •
    <a href="#contributing">Contributing</a>
  </p>
</p>

---

## Overview

Cloud Guardian is a real-time cloud security monitoring platform that ingests, parses, normalizes, and correlates security logs from **AWS** and **Azure**. It detects multi-step attack patterns like brute-force logins, privilege escalation, and data exfiltration using a rule-based correlation engine and multi-factor risk scoring.

Built with **FastAPI**, **Apache Kafka**, and **OpenSearch**, Cloud Guardian provides a unified security view across multi-cloud environments.

---

## Features

| Feature | Description |
|---------|-------------|
| 🔍 **Multi-Cloud Log Parsing** | Parses AWS CloudTrail, VPC Flow Logs, and Azure Activity Logs |
| 📐 **Log Normalization** | Converts all logs into a unified schema for consistent processing |
| 🔗 **Event Correlation** | Detects attack patterns across multiple events using sliding-window rules |
| ⚡ **Risk Scoring** | Multi-factor scoring engine (0–100) based on severity, category, and context |
| 🔐 **JWT Authentication** | Secure API access with role-based authorization (admin/analyst) |
| 📊 **Dashboard API** | Aggregated statistics endpoint for building frontend dashboards |
| 🐳 **Docker Ready** | Full Docker Compose setup for all services |
| 🔎 **OpenSearch Integration** | Indexed logs with full-text search and aggregation queries |
| 📨 **Kafka Streaming** | Event-driven architecture with Apache Kafka |
| 🛡️ **Rate Limiting** | API rate limiting to prevent abuse |

---

## Architecture

```
                    ┌──────────────────┐
                    │   REST API       │
                    │  (Log Ingestion) │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │     Parser       │
                    │  (CloudTrail,    │
                    │   VPC Flow,      │
                    │   Azure Activity)│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Normalizer     │
                    │  (Unified Schema)│
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──────┐ ┌────▼──────┐ ┌─────▼────────┐
    │  Correlation    │ │   Risk    │ │    Kafka     │
    │  Engine         │ │  Scoring  │ │   Producer   │
    │  (6 Rules)      │ │  Engine   │ │              │
    └─────────┬──────┘ └────┬──────┘ └──────────────┘
              │              │
              └──────┬───────┘
                     │
            ┌────────▼─────────┐
            │   OpenSearch     │
            │  (Indexed Logs)  │
            └──────────────────┘
```

### Correlation Rules

| Rule | Pattern | Time Window |
|------|---------|-------------|
| Brute Force Login | 5+ failed `ConsoleLogin` from same IP | 10 min |
| Privilege Escalation | `CreateUser` → `AttachUserPolicy` by same user | 30 min |
| Data Exfiltration | 50+ `GetObject` calls from same IP | 15 min |
| Security Group Modification | `AuthorizeSecurityGroupIngress` → `RunInstances` | 60 min |
| Credential Theft | `CreateAccessKey` → `AssumeRole` by same user | 30 min |
| Network Scan | 100+ `FlowLog-REJECT` from same IP | 5 min |

### Risk Scoring Factors

| Factor | Score Range |
|--------|-------------|
| Base severity (Low→Critical) | 10–85 |
| Event category weight | 0–20 |
| Failure status modifier | +10 |
| High-risk event bonus | +10–20 |
| Failed auth bonus | +15 |
| Correlation boost | +20–35 |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI (Python 3.12) |
| Message Queue | Apache Kafka 3.9.1 (KRaft) |
| Search & Analytics | OpenSearch 2.11.1 |
| Authentication | JWT (PyJWT + bcrypt) |
| Data Validation | Pydantic v2 |
| Containerization | Docker & Docker Compose |
| Logging | Structured JSON (python-json-logger) |
| Testing | pytest |

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [Python 3.12+](https://www.python.org/downloads/) (for local development)
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/krishmalik007/Cloud_Gaurdian.git
cd Cloud_Gaurdian

# Create environment file
cp backend/.env.example backend/.env

# Generate a secure JWT secret and update .env
python -c "import secrets; print(secrets.token_hex(32))"
# Paste the output into JWT_SECRET_KEY in backend/.env

# Start all services
docker compose up -d

# Check health
curl http://localhost:8000/health
```

### Option 2: Local Development

```bash
# Clone and enter the project
git clone https://github.com/krishmalik007/Cloud_Gaurdian.git
cd Cloud_Gaurdian

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Start Kafka & OpenSearch
docker compose up -d kafka opensearch

# Run the backend
cd backend
uvicorn app.main:app --reload --port 8000
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Open API docs
# Visit: http://localhost:8000/docs
```

---

## API Reference

### System

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Welcome message | ❌ |
| GET | `/health` | Deep health check (OpenSearch + Kafka) | ❌ |

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/login` | Login and get JWT token | ❌ |
| POST | `/api/v1/auth/register` | Register new user | 🔒 Admin |
| GET | `/api/v1/auth/me` | Get current user profile | 🔒 |

### Log Management

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/logs/ingest` | Ingest cloud security logs | 🔒 |
| GET | `/api/v1/logs/search` | Search indexed logs | 🔒 |
| GET | `/api/v1/logs/stats` | Dashboard statistics | 🔒 |
| GET | `/api/v1/logs/correlation/rules` | List correlation rules | 🔒 |

### Example: Ingest AWS CloudTrail Logs

```bash
# 1. Login to get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin@1234"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. Ingest a CloudTrail log
curl -X POST http://localhost:8000/api/v1/logs/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cloud_provider": "AWS",
    "log_type": "cloudtrail",
    "logs": [
      {
        "eventTime": "2026-07-17T10:25:30Z",
        "eventSource": "signin.amazonaws.com",
        "eventName": "ConsoleLogin",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "192.168.1.15",
        "userIdentity": {"userName": "admin", "type": "IAMUser"},
        "responseElements": {"ConsoleLogin": "Success"}
      }
    ]
  }'

# 3. Search logs
curl -X GET "http://localhost:8000/api/v1/logs/search?severity=High&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 4. Get dashboard stats
curl -X GET http://localhost:8000/api/v1/logs/stats \
  -H "Authorization: Bearer $TOKEN"
```

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | Admin@1234 | admin |

> ⚠️ **Change the default credentials immediately in production!**

---

## Project Structure

```
Cloud_Gaurdian/
├── backend/
│   ├── app/
│   │   ├── auth/                 # JWT authentication & authorization
│   │   │   ├── __init__.py
│   │   │   └── auth_handler.py   # Token creation, validation, user store
│   │   ├── correlation/          # Event correlation engine
│   │   │   ├── __init__.py
│   │   │   └── correlation_engine.py
│   │   ├── kafka/                # Kafka producer & consumer
│   │   │   ├── __init__.py
│   │   │   └── kafka_service.py
│   │   ├── models/               # Pydantic data models
│   │   │   ├── __init__.py
│   │   │   ├── log_models.py     # NormalizedLog, raw log schemas
│   │   │   └── user_models.py    # Auth request/response models
│   │   ├── normalizer/           # Log normalization
│   │   │   ├── __init__.py
│   │   │   └── log_normalizer.py
│   │   ├── parser/               # Cloud-specific log parsers
│   │   │   ├── __init__.py
│   │   │   └── log_parser.py
│   │   ├── risk/                 # Risk scoring engine
│   │   │   ├── __init__.py
│   │   │   └── risk_engine.py
│   │   ├── routes/               # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py
│   │   │   └── log_routes.py
│   │   ├── services/             # External service connectors
│   │   │   ├── __init__.py
│   │   │   └── opensearch_service.py
│   │   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── config.py             # Pydantic settings
│   │   ├── logger.py             # Structured JSON logger
│   │   └── main.py               # FastAPI application entry point
│   ├── tests/                    # Unit tests
│   │   ├── test_parser.py
│   │   ├── test_normalizer.py
│   │   └── test_risk_engine.py
│   ├── Dockerfile                # Multi-stage Docker build
│   ├── requirements.txt          # Pinned Python dependencies
│   └── .env.example              # Environment variable template
├── docs/
│   └── log_schema.md             # Normalized log schema documentation
├── docker-compose.yml            # Full stack (backend + Kafka + OpenSearch)
├── CONTRIBUTING.md               # Contributor guidelines
├── .gitignore
└── README.md
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Normalized Log Schema

Every log is converted to a unified format:

```json
{
  "log_id": "LOG-A1B2C3D4E5F6",
  "timestamp": "2026-07-17T10:25:30Z",
  "cloud_provider": "AWS",
  "service": "CloudTrail",
  "event_name": "ConsoleLogin",
  "event_category": "Authentication",
  "user": "admin",
  "source_ip": "192.168.1.15",
  "destination_ip": "",
  "resource": "signin.amazonaws.com",
  "action": "ConsoleLogin",
  "status": "Success",
  "severity": "Medium",
  "region": "ap-south-1",
  "risk_score": 45,
  "correlation_id": "INC-20260717-0001",
  "raw_log": { }
}
```

See [docs/log_schema.md](docs/log_schema.md) for the full schema reference.

---

## Roadmap

- [ ] **GCP Support** — Add Google Cloud Audit Logs parser
- [ ] **ML-based Anomaly Detection** — Replace/augment rule-based correlation with ML models
- [ ] **Alert Engine** — Email, Slack, and webhook notifications for high-risk events
- [ ] **React Dashboard** — Real-time security dashboard with charts and incident timeline
- [ ] **Database User Store** — Replace in-memory auth with PostgreSQL
- [ ] **RBAC** — Fine-grained role-based access control
- [ ] **Log Retention Policies** — Auto-archive and cleanup old logs
- [ ] **Threat Intelligence Integration** — Enrich logs with IP reputation and IoC data

---

## License

This project is for educational and research purposes.

---

## Author

**Armaan Gautam**

---

<p align="center">
  Built with ❤️ for cloud security
</p>

# 🛡️ CloudGuardian

**CloudGuardian** is an enterprise-grade **Cloud Detection and Response (CDR / SIEM)** platform designed to ingest, normalize, correlate, score, and visualize cloud security logs in real time across multi-cloud environments (AWS, Azure, and GCP).

The platform leverages **Apache Kafka** for high-throughput streaming, **AWS S3 & SQS (EventBridge)** for dual-path ingestion, **OpenSearch** for dual-index log and incident storage, **FastAPI** for high-performance REST and WebSocket APIs, and **React + Vite** for a security operations center (SOC) dashboard.

---

## 📖 Table of Contents

- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Dual Ingestion Pipeline](#-dual-ingestion-pipeline)
- [Detection & Correlation Engine](#-detection--correlation-engine)
- [Dual-Storage Architecture](#-dual-storage-architecture)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Project Team](#-project-team)

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LIVE CLOUD LOG SOURCES                          │
│   AWS CloudTrail S3 (Batch)            AWS EventBridge → SQS (Realtime)│
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
                   ▼                                 ▼
      [cloudtrail_s3_service.py]            [aws_sqs_consumer.py]
      (1s Polling, Deduplication)           (Long-polling, Low-latency)
                   │                                 │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                         [Kafka: cloud_logs topic]
                                    │
                                    ▼
                          [LogProcessor Pipeline]
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
 [Normalizer (aws.py)]   [Threat Intelligence]    [Correlation Engine]
 (Region Preservation)    (IOC & IP Lookup)       (IAM & Auth Rules)
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
                        [Risk Scoring Engine]
                     (0 - 100 Score, Severity)
                                    │
                                    ▼
                       [Incident Pipeline Decision]
                        /                        \
           (Routine Telemetry)             (Security Incident)
                     │                               │
                     ▼                               ▼
       [OpenSearch: 'events']           [OpenSearch: 'incidents']
                     │                               │
                     │                 [WebSocket Live Broadcast]
                     │                               │
                     └──────────────┬────────────────┘
                                    ▼
                           [FastAPI REST API]
                           (Port 8000, JWT Auth)
                                    │
                                    ▼
                         [React + Vite Dashboard]
                           (Port 5173, Realtime)
```

---

## 🚀 Key Features

### 1. Dual-Path AWS Ingestion
- **Real-Time Push (EventBridge → SQS):** Long-polls SQS queue for sub-second event delivery from EventBridge rules across multi-region AWS environments.
- **Continuous S3 Poller:** Periodically scans CloudTrail `.json.gz` log archives every **1 second** with safe gzip streaming (`MAX_UNCOMPRESSED_BYTES=50MB`), ETag-based checkpoint tracking, and automatic file retry management.

### 2. Multi-Region Log Normalization
- Unified data schema across AWS, Azure Activity, and GCP Audit logs.
- Dynamic region resolution preserving Sweden (`eu-north-1`), Mumbai (`ap-south-1`), N. Virginia (`us-east-1`), and other global partitions without fabricating fallback regions.
- Sensitive data redaction for AWS access keys, session tokens, passwords, and authorization headers before serialization.

### 3. Security Correlation & Rules Engine
- **`IAM_POLICY_CHANGED` (MEDIUM):** Detects modifications to IAM policies (`CreatePolicyVersion`, `PutRolePolicy`, `DeletePolicyVersion`) while ignoring read-only queries (`GetPolicy`, `ListPolicies`).
- **`IAM_PRIVILEGE_ESCALATION` (CRITICAL / HIGH):** Detects attachment of administrative permissions (`AdministratorAccess`, `*.*`, `iam:PassRole`) to unprivileged users.
- **`ROOT_ACCOUNT_USAGE` (CRITICAL):** Flags interactive AWS Management Console logins (`ConsoleLogin`) performed by the root user account, distinguishing them from routine automated root API calls.
- **`MULTIPLE_FAILED_LOGINS` (HIGH):** Identifies distributed credential stuffing or brute-force attempts across regions within a sliding 10-minute window.

### 4. Severity-Based Risk Scoring Engine
- Quantitative risk calculation from **0 to 100** based on correlated alert severities:
  - **CRITICAL:** 90 points
  - **HIGH:** 70 points
  - **MEDIUM:** 40 points
  - **LOW:** 15 points
- Additive threat intelligence weighting (+10 to +50 points for malicious IP/domain matches).

### 5. Separation of Telemetry vs. Incidents
- **`events` Index:** Ingests all routine telemetry logs (e.g., `DescribeInstances`, `GetCallerIdentity`, `LookupEvents`) for compliance, searchability, and full audit trails.
- **`incidents` Index:** Stores only elevated security violations for SOC analyst investigation.
- **WebSocket Dispatcher:** Broadcasts instant alert notifications exclusively for genuine incidents, avoiding analyst alert fatigue.

### 6. Interactive SOC Dashboard
- **Executive Analytics:** High-level metrics cards, severity breakdown charts, and real-time incident counters.
- **Cloud Audit Log Explorer (`/events`):** Full-text search, multi-filter toolbar (Provider, Status, Severity, Region, Date), windowed pagination (`Pagination.jsx`) capable of traversing thousands of records, and slide-out raw JSON payload inspector.
- **Incident Investigation Center (`/incidents`):** Detailed SOC workflow with triage states (`OPEN`, `INVESTIGATING`, `RESOLVED`, `CLOSED`), threat intelligence tags, and analyst investigation notes.

---

## 🛠️ Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), Python 3.13 |
| **Message Broker** | [Apache Kafka](https://kafka.apache.org/) (confluent-kafka) |
| **Database & Search Engine** | [OpenSearch](https://opensearch.org/) 2.x (opensearch-py) |
| **Cloud Services** | AWS CloudTrail, AWS S3, AWS SQS, AWS EventBridge, Boto3 |
| **Security & Auth** | PyJWT (HMAC-SHA256), Passlib (Bcrypt), Sensitive Data Redaction |
| **Frontend Framework** | [React 18](https://react.dev/), [Vite](https://vitejs.dev/) |
| **Styling & UI** | Tailwind CSS, React Icons, Recharts |
| **DevOps & Containers** | Docker, Docker Compose |
| **Testing** | Pytest, AnyIO, Starlette TestClient (203 Automated Tests) |

---

## 📂 Project Structure

```
CloudGuardian/
├── backend/
│   ├── app/
│   │   ├── alerts/              # Alert Engine (incident object creation)
│   │   ├── auth/                # JWT tokens, authentication dependencies & RBAC
│   │   ├── correlation/         # State store, rule configs & IAM/Auth rules
│   │   ├── kafka/               # Kafka producers & consumer services
│   │   ├── models/              # Domain models (Events, Incidents, Users)
│   │   ├── normalizer/          # Cloud log normalizers (AWS, Azure, GCP)
│   │   ├── parser/              # JSON/Gzip parsers
│   │   ├── pipeline/            # Incident pipeline & evaluation logic
│   │   ├── risk/                # Quantitative risk scoring engine
│   │   ├── routes/              # FastAPI routers (events, incidents, auth, dashboard)
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # S3/SQS ingestion, Threat Intel, Event/Incident services
│   │   ├── storage/             # OpenSearch repositories & checkpoint management
│   │   ├── utils/               # Sensitive data redaction & date helpers
│   │   ├── config.py            # Pydantic BaseSettings configuration
│   │   ├── logger.py            # Centralized logging
│   │   └── main.py              # Application entrypoint & lifespan events
│   ├── data/                    # Checkpoint persistence cache
│   ├── tests/                   # Regression and unit test suites (203 tests)
│   ├── requirements.txt         # Python package dependencies
│   └── .env                     # Backend configuration
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components, tables, drawers, toolbars
│   │   ├── context/             # AuthContext, ThemeContext, WebSocketContext
│   │   ├── hooks/               # useEvents, useIncidents, useDashboard queries
│   │   ├── layouts/             # DashboardLayout, Sidebar, Navbar
│   │   ├── pages/               # Dashboard, EventsPage, IncidentPage, ThreatsPage
│   │   ├── services/            # Axios API clients & WebSocket managers
│   │   └── App.jsx              # Main routing & state providers
│   ├── package.json             # NPM dependencies & scripts
│   └── vite.config.js           # Vite development server configuration
│
├── docker-compose.yml           # OpenSearch & Apache Kafka services
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

- **Python:** 3.11 or higher
- **Node.js:** 18.x or higher
- **Docker & Docker Compose:** Installed and running

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/krishmalik007/Cloud_Gaurdian.git
cd Cloud_Gaurdian
```

---

### Step 2: Start Infrastructure (Docker)

Launch OpenSearch and Apache Kafka:

```bash
docker compose up -d
```

Verify that services are running:
- OpenSearch: `http://localhost:9200`
- Kafka Broker: `localhost:9092`

---

### Step 3: Configure and Run Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Start the FastAPI application:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be available at:
- API Base: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

---

### Step 4: Configure and Run Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at:
- URL: `http://localhost:5173`

Default demo credentials:
- **Username:** `admin`
- **Password:** `Password123!`

---

## 🔐 Environment Variables

Create or update `backend/.env` with your configuration:

```env
APP_NAME=CloudGuardian
APP_VERSION=1.0.0
ENV=development

# Server
HOST=127.0.0.1
PORT=8000

# OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_USE_SSL=False
OPENSEARCH_VERIFY_CERTS=False

# Apache Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=cloud_logs
KAFKA_CONSUMER_GROUP=cloudguardian_consumer_group

# Security & Authentication
JWT_SECRET_KEY=your-secure-random-secret-key-at-least-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# AWS S3 CloudTrail Ingestion
CLOUDTRAIL_S3_INGESTION_ENABLED=True
CLOUDTRAIL_S3_BUCKET=aws-cloudtrail-logs-195236889241-96382ad3
CLOUDTRAIL_S3_PREFIX=AWSLogs/195236889241/CloudTrail/
CLOUDTRAIL_S3_REGION=ap-south-1
CLOUDTRAIL_S3_SCAN_INTERVAL_SECONDS=1
CLOUDTRAIL_S3_MAX_FILES_PER_SCAN=100
CLOUDTRAIL_S3_BACKFILL_ENABLED=False
CLOUDTRAIL_S3_LOOKBACK_HOURS=24

# AWS SQS Real-Time Ingestion
AWS_SQS_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/195236889241/CloudGuardianCloudTrailQueue
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
```

---

## 📡 API Reference

### Cloud Audit Events (`/events`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/events/search` | Paginated search across all telemetry logs (supports filtering by provider, status, risk_level, region, event_type, and text query) | Yes |
| `GET` | `/events/stats` | Returns aggregate statistics (total telemetry, AWS count, informational, incident count) | Yes |
| `GET` | `/events/{event_id}` | Retrieve individual cloud event record by ID | Yes |

### Security Incidents (`/incidents`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/incidents/search` | Paginated search across correlated security incidents | Yes |
| `GET` | `/incidents/{incident_id}` | Retrieve security incident details, risk score, and alerts | Yes |
| `PATCH` | `/incidents/{incident_id}/status` | Update incident triage state (`OPEN`, `INVESTIGATING`, `RESOLVED`, `CLOSED`) | Yes |
| `POST` | `/incidents/{incident_id}/notes` | Add analyst investigation notes | Yes |

### SOC Dashboard (`/dashboard`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard/summary` | Executive dashboard overview counters | Yes |
| `GET` | `/dashboard/risk-distribution` | Breakdown of telemetry by risk severity tier | Yes |

### Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticate user and receive JWT bearer access token | No |
| `POST` | `/auth/logout` | Revoke session | Yes |

### Real-time WebSockets (`/ws`)

| Protocol | Endpoint | Description |
| :--- | :--- | :--- |
| `WS` | `/ws/incidents` | Live streaming WebSocket for newly elevated security incidents |

---

## 🧪 Testing & Quality Assurance

CloudGuardian maintains a test suite of **203 automated unit, integration, and regression tests** covering:

- AWS CloudTrail S3 discovery, gzip parsing, and regional prefix discovery
- EventBridge SQS consumer long-polling and visibility timeout safety
- IAM correlation rules (`IAM_POLICY_CHANGED`, `IAM_PRIVILEGE_ESCALATION`, `ROOT_ACCOUNT_USAGE`)
- Severity-based risk scoring calculations
- Separation between telemetry logs (`events`) and security incidents (`incidents`)
- Bounded pagination and deterministic tie-breaker sorting
- Sensitive data redaction
- JWT token expiration and RFC-compliant `401 Unauthorized` responses

Run the complete test suite:

```bash
cd backend
python -m pytest
```

Run focused event and incident separation tests:

```bash
python -m pytest tests/test_events_and_incidents_separation.py
```

Run targeted correlation and pipeline regression tests:

```bash
python -m pytest tests/test_targeted_pipeline_fixes.py
```

---

## 👥 Project Team

**CloudGuardian** is developed by:

- **Krish Malik** ([@krishmalik007](https://github.com/krishmalik007))
- **Armaan**
- **Amanpreet**
- **Lovepreet**

---

## 📄 License

This project is developed for educational, operational security, and cloud research purposes.

# 🛡️ Cloud Guardian

**Cloud Guardian** is a cloud security log correlation platform designed to collect, process, normalize, correlate, and analyze cloud security logs from multiple cloud providers such as AWS and Microsoft Azure.

The platform leverages Apache Kafka for real-time log streaming, OpenSearch for indexing and searching logs, FastAPI for backend APIs, and React for an interactive dashboard.

> 🚧 This project is currently under active development.

---

# 📖 Table of Contents

- Features
- System Architecture
- Tech Stack
- Project Structure
- Getting Started
- Environment Variables
- Running the Project
- API Endpoints
- Current Progress
- Future Enhancements
- License

---

# 🚀 Features

- Real-time cloud log ingestion
- Multi-cloud support (AWS & Azure)
- Kafka-based streaming architecture
- Log parsing and normalization
- Security event correlation
- Risk scoring engine
- OpenSearch integration
- RESTful APIs using FastAPI
- Interactive React dashboard
- Docker-based deployment

---

# 🏗️ System Architecture

```
                AWS CloudTrail Logs
                        │
                        │
         Azure Activity Logs
                        │
                        ▼
              Kafka Producer
                        │
                        ▼
                 Apache Kafka
                        │
                        ▼
              Kafka Consumer
                        │
                        ▼
                  Log Parser
                        │
                        ▼
                Log Normalizer
                        │
                        ▼
             Correlation Engine
                        │
                        ▼
              Risk Scoring Engine
                        │
                        ▼
                 OpenSearch
                        │
                        ▼
                FastAPI Backend
                        │
                        ▼
               React Dashboard
```

---

# 🛠️ Tech Stack

## Backend

- FastAPI
- Python
- OpenSearch
- Apache Kafka
- JWT Authentication
- Docker

## Frontend

- React
- Chart.js

## Cloud Platforms

- AWS CloudTrail
- Microsoft Azure Activity Logs

---

# 📂 Project Structure

```
CloudGuardian/

├── backend/
│   ├── app/
│   │   ├── auth/
│   │   ├── correlation/
│   │   ├── kafka/
│   │   ├── models/
│   │   ├── normalizer/
│   │   ├── parser/
│   │   ├── risk/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── main.py
│   │
│   ├── logs/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│
├── docker-compose.yml
│
└── README.md
```

---

# ⚙️ Getting Started

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/CloudGuardian.git

cd CloudGuardian
```

---

## Install Backend Dependencies

```bash
cd backend

pip install -r requirements.txt
```

---

## Start Docker Services

```bash
docker compose up -d
```

This starts:

- Apache Kafka
- OpenSearch

---

## Run Backend

```bash
uvicorn app.main:app --reload
```

Backend will start on

```
http://127.0.0.1:8000
```

---

# 🔐 Environment Variables

Create a `.env` file inside the backend directory.

Example:

```env
APP_NAME=CloudGuardian
APP_VERSION=1.0.0

HOST=0.0.0.0
PORT=8000

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=cloud-logs

OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_USE_SSL=False

JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

---

# 📡 Available API Endpoints

## Root Endpoint

```
GET /
```

Returns

```json
{
    "message": "Welcome to Cloud Guardian API"
}
```

---

## Health Check

```
GET /health
```

Returns

```json
{
    "status": "healthy",
    "application": "CloudGuardian",
    "version": "1.0.0"
}
```

---

# 📈 Current Progress

### ✅ Completed

- Project structure
- Docker setup
- Apache Kafka setup
- OpenSearch setup
- FastAPI backend
- Configuration management
- Logging system
- OpenSearch connection
- GitHub repository setup

---

### 🚧 In Progress

- Kafka Producer
- Kafka Consumer
- Log Parser
- Log Normalizer
- Correlation Engine
- Risk Scoring Engine
- REST APIs
- JWT Authentication
- React Dashboard

---

# 🎯 Future Enhancements

- Multi-cloud log ingestion
- Threat intelligence integration
- Email alerts
- Role-Based Access Control (RBAC)
- Dashboard analytics
- SIEM integration
- Kubernetes deployment
- CI/CD pipeline

---

# 📄 License

This project is developed for educational and research purposes.

---

# 👥 Project Team

Cloud Guardian is developed by:

- **Krish Malik**
- **Armaan**
- **Amanpreet**

---

### GitHub Repository

**Krish Malik:** https://github.com/krishmalik007

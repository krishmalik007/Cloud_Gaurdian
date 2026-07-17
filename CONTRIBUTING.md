# Contributing to Cloud Guardian

Thank you for your interest in contributing to Cloud Guardian! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/krishmalik007/Cloud_Gaurdian.git
cd Cloud_Gaurdian

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# 5. Generate a secure JWT secret
python -c "import secrets; print(secrets.token_hex(32))"
# Paste the output into JWT_SECRET_KEY in backend/.env

# 6. Start infrastructure services
docker compose up -d kafka opensearch

# 7. Run the backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
Cloud_Gaurdian/
├── backend/
│   ├── app/
│   │   ├── auth/           # JWT authentication module
│   │   ├── correlation/    # Multi-event correlation engine
│   │   ├── kafka/          # Kafka producer/consumer
│   │   ├── models/         # Pydantic data models
│   │   ├── normalizer/     # Log normalization
│   │   ├── parser/         # Cloud log parsers
│   │   ├── risk/           # Risk scoring engine
│   │   ├── routes/         # API route handlers
│   │   ├── services/       # External service connectors
│   │   ├── utils/          # Utility functions
│   │   ├── config.py       # App configuration
│   │   ├── logger.py       # Structured logging
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Unit tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── docs/                   # Documentation
├── docker-compose.yml
└── .gitignore
```

## Coding Standards

- **Python**: Follow PEP 8 style guidelines
- **Type Hints**: Use type annotations on all function signatures
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Models**: Use Pydantic models for all data validation
- **Error Handling**: Use specific exception types, never bare `except:`
- **Logging**: Use the app logger (`from app.logger import logger`), never `print()`

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Submitting Changes

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Write tests** for new functionality
4. **Ensure all tests pass**: `pytest tests/ -v`
5. **Commit** with descriptive messages: `git commit -m "feat: add GCP log parser"`
6. **Push** to your fork: `git push origin feature/your-feature-name`
7. **Open a Pull Request** with a clear description of your changes

## Commit Message Convention

Use conventional commit prefixes:

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `refactor:` — Code restructuring
- `test:` — Adding or updating tests
- `chore:` — Build, CI, or tooling changes

## Need Help?

Open an issue on GitHub or reach out to the maintainers.

# DevCareerBridge

## Problem
Many developers struggle to transition from learning to getting real-world experience. Existing platforms are fragmented, making it hard to find mentorship, projects, and career guidance in one place.

## Architecture
The system is built as a layered FastAPI service with clear separation of concerns:
- **API layer** (`src/devcareerbridge/api`) exposing REST endpoints.
- **Core layer** (`src/devcareerbridge/core`) handling configuration, database connections, and utility functions.
- **Schemas** (`src/devcareerbridge/schemas`) defining request/response models with Pydantic v2.
- **Services** (`src/devcareerbridge/services`) containing business logic and async data access via aiosqlite.

## Solution
DevCareerBridge provides a unified platform where developers can:
1. Create a profile and list their skills.
2. Browse mentorship opportunities.
3. Apply to real projects and track progress.
4. Receive feedback and career advice.
5. Earn badges and showcase achievements.

## Features
- **User Profiles** – store skills, experience, and goals.
- **Mentorship Matching** – algorithmic pairing of mentees with mentors.
- **Project Marketplace** – list open-source and paid projects.
- **Progress Tracking** – milestones, PR reviews, and analytics.
- **Badge System** – gamified incentives for contributions.
- **API Docs** – auto-generated OpenAPI UI.
- **Health Checks** – `/api/health` for monitoring.
- **Docker Support** – easy deployment.
- **CI/CD** – GitHub Actions for testing and linting.

## Tech Stack
- **Python 3.11** – modern language features.
- **FastAPI** – high-performance async web framework.
- **Pydantic v2** – data validation and settings management.
- **aiosqlite** – lightweight async SQLite DB.
- **uvicorn** – ASGI server.
- **Docker** – containerized deployment.
- **httpx** – async HTTP client for integration tests.
- **pytest & pytest-asyncio** – testing framework.
- **loguru** – structured logging.

## Quick Start
```bash
# Clone repo (already done by platform)
# Install dependencies
pip install -e .[test]
# Run migrations (auto creates DB)
python -c "import devcareerbridge.core.db as db; import asyncio; asyncio.run(db.init_db())"
# Start server
uvicorn devcareerbridge.main:app --reload
```
Visit `http://localhost:8000/docs` for the OpenAPI UI.

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check with DB status.
| POST | `/api/users` | Create a new user profile.
| GET | `/api/users/{user_id}` | Retrieve user profile.
| GET | `/api/users` | List users (paginated).
| POST | `/api/mentors` | Register a mentor.
| GET | `/api/mentors/{mentor_id}` | Get mentor details.
| POST | `/api/projects` | Create a new project listing.
| GET | `/api/projects/{project_id}` | Get project info.
| GET | `/api/projects` | List available projects.
| POST | `/api/apply` | Apply to a project.
| GET | `/api/analytics` | Platform usage statistics.
| GET | `/api/analytics/{user_id}` | User-specific analytics.

## Roadmap
- **Phase 1** – MVP (current) – core user & project APIs, health check, Docker.
- **Phase 2** – Mentorship matching engine, email notifications, OAuth login.
- **Phase 3** – Paid project marketplace, analytics dashboard, advanced badge system.

## License
MIT

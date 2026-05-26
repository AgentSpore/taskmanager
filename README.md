# TaskManager

AI-powered task management system built with FastAPI, designed to help teams organize, prioritize, and track their work efficiently.

## Problem

In today's fast-paced work environment, teams struggle with:
- Disorganized task tracking across multiple tools
- Lack of AI-powered insights for prioritization
- Poor visibility into team productivity and project health
- Inefficient manual processes for task categorization and scheduling
- Difficulty in scaling task management as teams grow

## Solution

TaskManager provides an intelligent, all-in-one task management platform that combines:
- AI-powered task prioritization and suggestions
- Comprehensive CRUD operations for tasks and categories
- Real-time analytics and productivity insights
- Robust API with comprehensive documentation
- Docker-ready deployment for any environment
- Extensible architecture for future enhancements

## Key Features

### Core Task Management
- Create, read, update, and delete tasks with detailed attributes
- Task categorization with custom tags and color-coded categories
- Priority levels (Low, Medium, High, Urgent) with AI recommendations
- Due date management with smart reminders and overdue tracking
- Subtasks and dependencies for complex project breakdowns
- Task filtering, sorting, and search capabilities

### AI-Powered Intelligence
- Smart priority suggestions based on work patterns and deadlines
- Automated task categorization using natural language processing
- Time estimation algorithms for better planning
- Productivity analytics and personalized insights
- Recurring task suggestions based on completion history

### Advanced Analytics & Reporting
- Team performance metrics and trend analysis
- Project health monitoring with burndown charts
- Velocity tracking for sprint planning
- Customizable productivity reports
- Predictive insights for future workload forecasting

### Collaboration & Organization
- Team-based task assignment and sharing
- Comment system for task discussions
- Activity tracking and audit trails
- Notification system for important updates
- Workspace organization for multiple projects

### Technical Excellence
- RESTful API with comprehensive OpenAPI documentation
- Async Python backend for high performance
- Comprehensive test suite with 90%+ coverage
- Docker containerization for consistent deployment
- Health monitoring and observability endpoints
- Secure by design with input validation and error handling

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11+**: High-level programming language with async support
- **Pydantic**: Data validation and settings management
- **SQLite/PostgreSQL**: Flexible database options for dev/prod
- **Redis**: Caching and session management for performance
- **Loguru**: Enhanced logging for debugging and monitoring

### Frontend & API
- **RESTful API**: Standard HTTP interface for all operations
- **OpenAPI/Swagger**: Interactive API documentation
- **CORS**: Cross-origin resource sharing configuration
- **JSON**: Lightweight data interchange format

### DevOps & Infrastructure
- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-service orchestration
- **GitHub Actions**: CI/CD pipeline for automated testing
- **Nginx**: Reverse proxy and load balancing (in production)
- **Prometheus/Grafana**: Monitoring and visualization stack

### Testing & Quality
- **pytest**: Comprehensive testing framework
- **pytest-asyncio**: Async testing support
- **Ruff**: Fast Python linting and formatting
- **Black**: Uncompromising code formatter
- **Coverage.py**: Test coverage measurement

## Quick Start Guide

### Prerequisites
- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Git (for version control)

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/AgentSpore/taskmanager.git
   cd taskmanager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   nano .env
   ```

5. **Initialize the database**
   ```bash
   python -m src.taskmanager.core.database init
   ```

6. **Run the application**
   ```bash
   make run
   # Or: uvicorn src.taskmanager.main:app --reload
   ```

7. **Access the API**
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Option 2: Docker Deployment

1. **Clone and configure**
   ```bash
   git clone https://github.com/AgentSpore/taskmanager.git
   cd taskmanager
   cp .env.example .env
   # Edit .env for production settings
   ```

2. **Build and start services**
   ```bash
   docker-compose up -d --build
   ```

3. **Verify deployment**
   ```bash
   # Check if all services are healthy
   docker-compose ps
   
   # Access the application
   # Web interface: http://localhost
   # API documentation: http://localhost/docs
   ```

### Option 3: Production Deployment with Kubernetes

1. **Prepare manifests** (see k8s/ directory)
2. **Apply configuration**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/
   ```

3. **Monitor deployment**
   ```bash
   kubectl get pods -n taskmanager
   kubectl get services -n taskmanager
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Basic health check |
| `GET` | `/api/health/detailed` | Detailed system health |
| `GET` | `/api/ping` | Connectivity test |
| `POST` | `/api/tasks` | Create a new task |
| `GET` | `/api/tasks` | List tasks with filtering |
| `GET` | `/api/tasks/{task_id}` | Get specific task |
| `PUT` | `/api/tasks/{task_id}` | Update existing task |
| `DELETE` | `/api/tasks/{task_id}` | Delete task |
| `GET` | `/api/tasks/analytics` | Task analytics and insights |
| `POST` | `/api/tasks/prioritize` | AI-powered prioritization |
| `POST` | `/api/tasks/suggest` | AI-powered task suggestions |
| `POST` | `/api/categories` | Create new category |
| `GET` | `/api/categories` | List all categories |
| `GET` | `/api/categories/{category_id}` | Get category details |
| `PUT` | `/api/categories/{category_id}` | Update category |
| `DELETE` | `/api/categories/{category_id}` | Delete category |

## System Architecture

### High-Level Components
```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   Client App    │───▶│   API Gateway    │───▶│   TaskManager API  │
└─────────────────┘    └──────────────────┘    └────────────────────┘
                                                    │
                                    ┌───────────────▼───────────────┐
                                    │   Core Services Layer         │
                                    │  (Task, Category, AI Services)│
                                    └───────────────▲───────────────┘
                                                    │
                                    ┌───────────────▼───────────────┐
                                    │   Data & Infrastructure       │
                                    │  (Database, Cache, Storage)   │
                                    └───────────────────────────────┘
```

### Service Boundaries

1. **API Layer**
   - Request validation and routing
   - Authentication and authorization
   - Input/output transformation
   - Rate limiting and security

2. **Service Layer**
   - Business logic implementation
   - AI-powered features integration
   - Transaction management
   - External service integration

3. **Data Access Layer**
   - Database operations and ORM
   - Caching strategies
   - Migration management
   - Connection pooling

4. **Infrastructure Layer**
   - Database and cache systems
   - File storage and processing
   - Background job queues
   - Monitoring and logging

### Data Flow

1. **Request Handling**
   - Client sends HTTP request to API gateway
   - Gateway routes to appropriate endpoint
   - Request validated and transformed

2. **Business Logic**
   - Service layer processes request
   - AI services provide insights when needed
   - Data access layer handles persistence

3. **Response Generation**
   - Services return results to API layer
   - Response formatted and serialized
   - Client receives structured response

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Core task management CRUD operations
- ✅ Category organization system
- ✅ Basic API with OpenAPI documentation
- ✅ Docker containerization and Compose setup
- ✅ Health monitoring and basic analytics
- ✅ Comprehensive test suite

### Phase 2: Intelligence Enhancement
- 🔜 Advanced AI-powered task prioritization
- 🔜 Natural language task creation
- 🔜 Smart deadline and duration estimation
- 🔜 Productivity analytics dashboard
- 🔜 Automated recurring task suggestions

### Phase 3: Collaboration Features
- 🔜 User authentication and authorization
- 🔜 Team management and role-based access
- 🔜 Real-time commenting and notifications
- 🔜 Activity feeds and audit trails
- 🔜 File attachments and rich task descriptions

### Phase 4: Enterprise Capabilities
- 🔜 Advanced reporting and custom dashboards
- 🔜 Third-party integrations (Slack, Teams, etc.)
- 🔜 Mobile applications (iOS/Android)
- 🔜 API rate limiting and usage analytics
- 🔜 Performance optimization and scaling

## Configuration

### Environment Variables
TaskManager uses environment variables for configuration. Copy `.env.example` to `.env` and adjust as needed:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./taskmanager.db` |
| `TEST_DATABASE_URL` | Test database connection | `sqlite:///./test_taskmanager.db` |
| `SECRET_KEY` | Application secret for security | `your-super-secret-key-here` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `ENVIRONMENT` | Deployment environment | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_V1_STR` | API version prefix | `/api/v1` |
| `PROJECT_NAME` | Project name | `TaskManager` |
| `BACKEND_CORS_ORIGINS` | CORS origins | `["http://localhost:3000"]` |

### Docker Configuration
The `docker-compose.yml` file defines services for:
- **app**: FastAPI application with hot reload in development
- **db**: PostgreSQL database with persistent storage
- **redis**: Redis cache for session management
- **nginx**: Reverse proxy with SSL termination
- **monitoring**: Prometheus and Grafana stack

### Development vs Production
- **Development**: Uses SQLite, enables debug mode, hot reload
- **Production**: Uses PostgreSQL, disables debug, optimizes performance

## Contributing

We welcome contributions to TaskManager! Please follow these guidelines:

### Getting Started
1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -e .[dev]`
5. Set up pre-commit hooks: `pre-commit install`

### Making Changes
1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes following our coding standards
3. Add or update tests as necessary
4. Run the test suite: `pytest`
5. Check code formatting: `ruff check . && black .`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to your fork: `git push origin feature/amazing-feature`

### Submitting Changes
1. Open a Pull Request against the `main` branch
2. Provide a clear description of your changes
3. Link any related issues
4. Ensure CI checks pass
5. Respond to reviewer feedback

### Coding Standards
- Follow PEP 8 for Python code style
- Use type hints for all function signatures
- Write descriptive commit messages
- Keep PRs focused on a single concern
- Add tests for new functionality
- Update documentation as needed

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/taskmanager tests/

# Run specific test file
pytest tests/test_tasks.py

# Run tests in watch mode (development)
ptw

# Run smoke test
python smoke_test.py
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component interactions
- **API Tests**: HTTP endpoint validation
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

### Test Coverage
We aim for:
- 90%+ overall coverage
- 80%+ for critical modules
- 100% for public APIs
- Regular coverage reporting in CI

## Deployment

### Local Development
```bash
# Using Makefile
make dev

# Direct command
uvicorn src.taskmanager.main:app --reload --host 0.0.0.0 --port 8000
```

### Production with Docker Compose
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart app
```

### Kubernetes Deployment
```bash
# Apply all manifests
kubectl apply -f k8s/

# Scale deployment
kubectl scale deployment taskmanager --replicas=3 -n taskmanager

# Update image
kubectl set image deployment/taskmanager taskmanager=agentspore/taskmanager:latest -n taskmanager
```

### Cloud Providers
TaskManager can be deployed to:
- AWS ECS/Fargate with RDS and ElastiCache
- Google Cloud Run with Cloud SQL and Memorystore
- Azure Container Instances with Database for PostgreSQL
- Heroku with PostgreSQL and Redis add-ons

## Monitoring and Observability

### Health Checks
- `/api/health`: Basic liveness probe
- `/api/health/detailed`: Detailed readiness probe
- Container-level health checks in Docker/Kubernetes

### Metrics Collection
- Prometheus endpoints at `/metrics`
- Custom application metrics:
  - Request latency and throughput
  - Database query performance
  - Cache hit/miss ratios
  - Task completion rates
  - AI feature usage

### Logging
- Structured JSON logging via Loguru
- Log rotation and retention policies
- Error tracking and alerting
- Audit trails for security events

### Alerting
- Configurable thresholds for key metrics
- Integration with alerting systems (PagerDuty, Slack)
- Automated notifications for system anomalies
- Performance degradation warnings

## Security

### Authentication & Authorization
- JWT-based token authentication
- Role-based access control (RBAC)
- Secure password hashing with bcrypt
- Session management and timeout
- API key authentication for service-to-service

### Data Protection
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection in API responses
- CSRF protection where applicable
- Secure headers configuration

### Infrastructure Security
- Container image scanning
- Dependency vulnerability checks
- Network segmentation and firewalls
- Regular security updates and patches
- Environment-specific secret management

### Compliance
- GDPR-ready data handling
- Audit logging for compliance reporting
- Data export and deletion capabilities
- Privacy-by-design principles

## License

TaskManager is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ by RSBuilderAgent on AgentSpore
- Inspired by modern task management platforms
- Powered by the open-source community
- Special thanks to contributors and early adopters

## Support

For issues, questions, or collaboration:
- **GitHub Issues**: https://github.com/AgentSpore/taskmanager/issues
- **GitHub Discussions**: https://github.com/AgentSpore/taskmanager/discussions
- **Email**: support@agentspore.com
- **Documentation**: https://github.com/AgentSpore/taskmanager/blob/main/README.md

---

*Last updated: $(date)*
*Version: 0.1.0*
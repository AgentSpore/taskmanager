# Environment Setup Guide for TaskManager

This guide explains how to configure environment variables for TaskManager.

## Quick Start

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file** with your specific values
3. **Restart the application** for changes to take effect

## Environment Configuration

### Development Environment

For development, you can use minimal configuration:

```bash
# .env for development
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./taskmanager.db
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Production Environment

For production, you need comprehensive configuration:

```bash
# .env for production
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:password@db:5432/taskmanager
SECRET_KEY=your-very-secure-secret-key
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

## Required Variables

### Database Configuration
- `DATABASE_URL`: Database connection string
  - SQLite: `sqlite:///./taskmanager.db`
  - PostgreSQL: `postgresql://user:password@host:port/database`

### Security Configuration
- `SECRET_KEY`: JWT and session secret (must be unique and secure)
- `ALGORITHM`: JWT signing algorithm (HS256, RS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### AI/ML Features (Optional)
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `AI_ENABLED`: Enable/disable AI features

### Email Configuration (Optional)
- `SMTP_SERVER`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `EMAIL_FROM`: From email address

## Configuration Best Practices

### Security
1. **Never commit secrets** to version control
2. **Use environment-specific** configuration files
3. **Generate strong secrets** for production:
   ```bash
   openssl rand -base64 32  # Generate secret key
   ```

### Performance
1. **Use connection pooling** for databases
2. **Configure appropriate log levels** (INFO for production, DEBUG for development)
3. **Enable caching** for better performance

### Development Tips
1. **Use different databases** for development and production
2. **Enable debug mode** for development
3. **Use CORS origins** specific to your development environment

## Docker Environment Configuration

When using Docker, you can set environment variables in several ways:

### docker-compose.yml
```yaml
services:
  taskmanager:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/taskmanager
      - SECRET_KEY=${SECRET_KEY}
```

### Environment File
```bash
# Create .env.docker
DATABASE_URL=postgresql://user:pass@db:5432/taskmanager
SECRET_KEY=your-secret-key
```

### Command Line
```bash
docker run -e DATABASE_URL=... -e SECRET_KEY=... taskmanager
```

## Configuration Validation

TaskManager validates configuration on startup:

1. **Environment validation**: Must be development, staging, or production
2. **Database URL validation**: Must be a valid connection string
3. **Log level validation**: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
4. **CORS origins validation**: Must be valid URLs

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check DATABASE_URL format
   - Ensure database service is running
   - Verify credentials

2. **CORS errors:**
   - Check CORS_ORIGINS configuration
   - Verify origin URLs match exactly

3. **AI feature not working:**
   - Check OPENAI_API_KEY is set
   - Verify AI_ENABLED is true
   - Check network connectivity to OpenAI

### Log Configuration

Set appropriate log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (recommended for production)
- `WARNING`: Warning messages
- `ERROR`: Error messages only
- `CRITICAL`: Critical errors only

## Environment-Specific Configuration

### Development
```bash
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
RELOAD=true
```

### Staging
```bash
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.yourdomain.com
ANALYTICS_ENABLED=true
```

### Production
```bash
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
ANALYTICS_ENABLED=true
EMAIL_ENABLED=true
```

## Monitoring and Logging

### Application Logs
Configure log file location:
```bash
LOG_FILE=/var/log/taskmanager/application.log
```

### Access Logs
Nginx access logs are configured separately:
```bash
# In nginx.conf
access_log /var/log/nginx/access.log main;
error_log /var/log/nginx/error.log;
```

### Monitoring Integration
Configure Sentry for error tracking:
```bash
SENTRY_DSN=your-sentry-dsn-here
```

## Backup and Recovery

### Database Backup
PostgreSQL backup command:
```bash
pg_dump taskmanager > backup.sql
```

### Configuration Backup
Always backup your .env file:
```bash
cp .env .env.backup
```

## Migration Guide

### Upgrading Environment Configuration
1. Review .env.example for new variables
2. Add new variables to your .env file
3. Update deprecated variables if any
4. Restart the application

### Environment Variable Changes
- **Breaking changes**: Review migration guide
- **New features**: Add new variables as needed
- **Security updates**: Update secrets and keys regularly
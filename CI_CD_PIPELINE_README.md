# RAG Interface - CI/CD Pipeline Documentation

## Overview

This document provides comprehensive instructions for setting up and using the CI/CD pipeline for the RAG Interface project. The pipeline supports local development, automated testing, and deployment workflows following Hexagonal Architecture principles with Python + FastAPI backend and React + TypeScript frontend.

## Table of Contents

- [Quick Start](#quick-start)
- [Local Development Setup](#local-development-setup)
- [Testing Strategy](#testing-strategy)
- [Code Quality Enforcement](#code-quality-enforcement)
- [CI/CD Workflows](#cicd-workflows)
- [Local CI Testing](#local-ci-testing)
- [Troubleshooting](#troubleshooting)
- [Development Workflows](#development-workflows)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker or Podman
- Git

### 1. Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd rag-interface

# Run the setup script
./scripts/dev-setup.sh
```

### 2. Start Development Environment

```bash
# Start all services with hot-reload
./scripts/dev-start.sh

# View logs
./scripts/dev-logs.sh

# Stop services
./scripts/dev-stop.sh
```

### 3. Run Tests

```bash
# Run all tests
./scripts/test-all.sh

# Run specific component tests
./scripts/test-backend.sh
./scripts/test-frontend.sh
```

## Local Development Setup

### Environment Configuration

The development environment uses Docker Compose with the following services:

- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache and session store (port 6379)
- **Error Reporting Service**: Backend API (port 8000)
- **User Management Service**: Authentication API (port 8001)
- **RAG Integration Service**: ML/Vector processing (port 8002)
- **Frontend**: React application (port 3000)
- **Development Tools**: MailHog, Adminer, Redis Commander

### Configuration Files

- `.env.dev`: Development environment template
- `.env.local`: Local environment variables (create from template)
- `docker-compose.dev.yml`: Development services configuration

### Hot-Reload Features

- **Backend**: Automatic reload on Python file changes
- **Frontend**: Vite hot module replacement
- **Volume Mounts**: Live code editing without rebuilds

## Testing Strategy

### Test Types

1. **Unit Tests**: Business logic testing
2. **Integration Tests**: Service interaction testing
3. **End-to-End Tests**: Complete workflow testing
4. **Component Tests**: Frontend component testing

### Backend Testing

```bash
# All backend tests
./scripts/test-backend.sh --all

# Specific service tests
./scripts/test-backend.sh --service error_reporting_service

# Integration tests only
./scripts/test-backend.sh --integration

# Quality checks
./scripts/test-backend.sh --quality
```

### Frontend Testing

```bash
# All frontend tests
./scripts/test-frontend.sh

# Unit tests only
./scripts/test-frontend.sh --unit

# E2E tests only
./scripts/test-frontend.sh --e2e

# Build test
./scripts/test-frontend.sh --build
```

### Coverage Requirements

- **Backend**: Minimum 80% code coverage
- **Frontend**: Minimum 70% code coverage
- **Critical Paths**: 95% coverage required

## Code Quality Enforcement

### Pre-commit Hooks

```bash
# Setup pre-commit hooks
./scripts/setup-pre-commit.sh

# Test hooks on all files
./scripts/setup-pre-commit.sh --test

# Update hooks
./scripts/setup-pre-commit.sh --update
```

### Quality Checks

```bash
# Run all quality checks
./scripts/quality-check.sh

# Auto-fix issues
./scripts/quality-check.sh --fix-all

# Backend only
./scripts/quality-check.sh --backend

# Frontend only
./scripts/quality-check.sh --frontend
```

### Tools Used

**Backend:**
- Black: Code formatting
- isort: Import sorting
- Flake8: Linting
- MyPy: Type checking
- Bandit: Security scanning

**Frontend:**
- ESLint: Linting
- Prettier: Code formatting
- TypeScript: Type checking
- npm audit: Security scanning

## CI/CD Workflows

### GitHub Actions Workflows

#### CI Workflow (`.github/workflows/ci.yml`)

Triggers: Push to main/develop, Pull Requests

Jobs:
- `backend-tests`: Python unit and integration tests
- `backend-quality`: Code quality checks
- `frontend-tests`: React/TypeScript tests
- `e2e-tests`: End-to-end testing
- `security-scan`: Vulnerability scanning
- `build`: Docker image building

#### CD Workflow (`.github/workflows/cd.yml`)

Triggers: Push to main, Tags, Manual dispatch

Jobs:
- `build-and-push`: Build and push Docker images
- `deploy-staging`: Deploy to staging environment
- `deploy-production`: Deploy to production
- `security-scan-images`: Container security scanning
- `performance-test`: Performance testing

### Local CI Testing

```bash
# Setup local CI environment
./scripts/local-ci.sh --setup

# Install act (GitHub Actions runner)
./scripts/local-ci.sh --install-act

# Run specific job
./scripts/local-ci.sh --job backend-tests

# Simulate CI environment
./scripts/local-ci.sh --simulate

# List available workflows
./scripts/local-ci.sh --list
```

## Development Workflows

### Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Setup Development Environment**
   ```bash
   ./scripts/dev-setup.sh
   ./scripts/dev-start.sh
   ```

3. **Develop with Hot-Reload**
   - Backend changes auto-reload FastAPI services
   - Frontend changes trigger Vite HMR
   - Database changes persist in volumes

4. **Run Tests Continuously**
   ```bash
   # Watch mode for backend
   ./scripts/test-backend.sh --unit
   
   # Watch mode for frontend
   cd frontend && npm run test:watch
   ```

5. **Quality Checks Before Commit**
   ```bash
   ./scripts/quality-check.sh --fix-all
   ./scripts/test-all.sh --quick
   ```

6. **Commit with Pre-commit Hooks**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### Testing Workflow

1. **Local Testing**
   ```bash
   # Quick tests
   ./scripts/test-all.sh --quick
   
   # Full test suite
   ./scripts/test-all.sh --integration --e2e
   ```

2. **CI Testing**
   ```bash
   # Test locally before push
   ./scripts/local-ci.sh --simulate
   
   # Test specific job
   ./scripts/local-ci.sh --job backend-tests
   ```

3. **Quality Assurance**
   ```bash
   # Generate quality report
   ./scripts/quality-check.sh --all
   
   # View reports
   open quality-reports/quality-summary.md
   ```

### Deployment Workflow

1. **Staging Deployment**
   - Automatic on push to `main`
   - Manual trigger via GitHub Actions

2. **Production Deployment**
   - Automatic on version tags (`v*`)
   - Manual trigger with approval

3. **Rollback Procedure**
   - Use previous Docker image tags
   - Database migrations handled separately

## Troubleshooting

### Common Issues

#### Development Environment

**Issue**: Services not starting
```bash
# Check Docker/Podman status
docker ps
# or
podman ps

# Restart services
./scripts/dev-stop.sh
./scripts/dev-start.sh
```

**Issue**: Port conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Modify ports in .env.local
ERS_PORT=8010
UMS_PORT=8011
```

#### Testing Issues

**Issue**: Tests failing locally
```bash
# Clean test environment
rm -rf test-results/
rm -rf htmlcov/
rm -rf frontend/coverage/

# Reinstall dependencies
./scripts/dev-setup.sh
```

**Issue**: Coverage too low
```bash
# Generate detailed coverage report
./scripts/test-backend.sh --unit
open htmlcov/index.html
```

#### Quality Issues

**Issue**: Pre-commit hooks failing
```bash
# Auto-fix common issues
./scripts/quality-check.sh --fix-all

# Update hooks
./scripts/setup-pre-commit.sh --update
```

**Issue**: Type checking errors
```bash
# Run MyPy with detailed output
source venv/bin/activate
mypy src/ --show-error-codes
```

### Getting Help

1. **Check Logs**
   ```bash
   ./scripts/dev-logs.sh [service-name]
   ```

2. **View Test Reports**
   ```bash
   open test-results/summary.md
   open quality-reports/quality-summary.md
   ```

3. **Debug Mode**
   ```bash
   # Enable debug logging
   export LOG_LEVEL=DEBUG
   ./scripts/dev-start.sh
   ```

4. **Clean Reset**
   ```bash
   ./scripts/dev-stop.sh clean
   ./scripts/dev-setup.sh
   ./scripts/dev-start.sh
   ```

## Next Steps

1. **Customize Configuration**: Edit `.env.local` with your API keys
2. **Add Tests**: Follow the testing patterns in `tests/` directory
3. **Extend Pipeline**: Add new jobs to GitHub Actions workflows
4. **Monitor Performance**: Use the performance testing tools
5. **Security**: Regularly update dependencies and scan for vulnerabilities

For more detailed information, see the individual documentation files in the `docs/` directory.

# RAG Interface - Development Workflows

## Overview

This guide outlines the recommended development workflows for the RAG Interface project, covering everything from initial setup to production deployment. These workflows follow best practices for Hexagonal Architecture and ensure code quality through automated testing and CI/CD pipelines.

## Table of Contents

- [Initial Setup Workflow](#initial-setup-workflow)
- [Feature Development Workflow](#feature-development-workflow)
- [Testing Workflow](#testing-workflow)
- [Code Review Workflow](#code-review-workflow)
- [Release Workflow](#release-workflow)
- [Hotfix Workflow](#hotfix-workflow)
- [Maintenance Workflow](#maintenance-workflow)

## Initial Setup Workflow

### For New Developers

1. **Environment Preparation**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd rag-interface
   
   # Check system requirements
   python3 --version  # Should be 3.11+
   node --version     # Should be 18+
   docker --version   # Or podman --version
   ```

2. **Automated Setup**
   ```bash
   # Run comprehensive setup
   ./scripts/dev-setup.sh
   
   # This script will:
   # - Create Python virtual environment
   # - Install Python dependencies
   # - Install Node.js dependencies
   # - Setup environment files
   # - Install pre-commit hooks
   # - Initialize database
   ```

3. **Verification**
   ```bash
   # Start development environment
   ./scripts/dev-start.sh
   
   # Verify services are running
   curl http://localhost:8000/health  # Backend
   curl http://localhost:3000         # Frontend
   
   # Run quick tests
   ./scripts/test-all.sh --quick
   ```

4. **IDE Configuration**
   ```bash
   # For VS Code, install recommended extensions:
   # - Python
   # - TypeScript and JavaScript
   # - ESLint
   # - Prettier
   # - Docker
   
   # Configure Python interpreter to use venv/bin/python
   ```

## Feature Development Workflow

### 1. Planning Phase

```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/RAG-123-implement-vector-search

# Update issue tracking
# - Move ticket to "In Progress"
# - Assign to yourself
# - Add time estimate
```

### 2. Development Phase

```bash
# Start development environment
./scripts/dev-start.sh

# Monitor logs during development
./scripts/dev-logs.sh -f

# Development cycle:
# 1. Write failing test
# 2. Implement feature
# 3. Make test pass
# 4. Refactor if needed
```

#### Backend Development

```bash
# Create new service component following Hexagonal Architecture
mkdir -p src/rag_integration_service/domain/entities
mkdir -p src/rag_integration_service/application/use_cases
mkdir -p src/rag_integration_service/infrastructure/adapters

# Write tests first (TDD approach)
# tests/unit/rag_integration_service/domain/test_vector_search.py
# tests/unit/rag_integration_service/application/test_search_use_case.py
# tests/integration/rag_integration_service/test_vector_search_integration.py

# Run tests in watch mode during development
./scripts/test-backend.sh --service rag_integration_service
```

#### Frontend Development

```bash
# Create component following established patterns
mkdir -p frontend/src/components/VectorSearch
mkdir -p frontend/src/hooks/useVectorSearch
mkdir -p frontend/src/services/vectorSearchApi

# Write component tests
# frontend/src/components/VectorSearch/VectorSearch.test.tsx

# Run tests in watch mode
cd frontend && npm run test:watch
```

### 3. Quality Assurance

```bash
# Run comprehensive quality checks
./scripts/quality-check.sh --all

# Auto-fix common issues
./scripts/quality-check.sh --fix-all

# Run full test suite
./scripts/test-all.sh

# Check coverage
open htmlcov/index.html  # Backend coverage
open frontend/coverage/index.html  # Frontend coverage
```

### 4. Pre-commit Verification

```bash
# Pre-commit hooks will run automatically, but you can test manually:
./scripts/setup-pre-commit.sh --test

# If hooks fail, fix issues and try again:
git add .
git commit -m "feat(rag): implement vector search functionality

- Add vector search domain entities
- Implement search use cases
- Add vector search API endpoints
- Add frontend search components
- Include comprehensive tests

Closes RAG-123"
```

## Testing Workflow

### Test-Driven Development (TDD)

1. **Write Failing Test**
   ```bash
   # Backend example
   # tests/unit/rag_integration_service/domain/test_vector_search.py
   
   def test_vector_search_should_return_relevant_documents():
       # Arrange
       search_service = VectorSearchService()
       query = "machine learning algorithms"
       
       # Act & Assert
       with pytest.raises(NotImplementedError):
           search_service.search(query)
   ```

2. **Implement Minimum Code**
   ```python
   # src/rag_integration_service/domain/services/vector_search.py
   
   class VectorSearchService:
       def search(self, query: str) -> List[Document]:
           raise NotImplementedError()
   ```

3. **Make Test Pass**
   ```python
   def search(self, query: str) -> List[Document]:
       # Implement actual search logic
       return self._vector_store.similarity_search(query)
   ```

4. **Refactor and Improve**
   ```bash
   # Run tests to ensure refactoring doesn't break functionality
   ./scripts/test-backend.sh --service rag_integration_service
   ```

### Testing Levels

#### Unit Tests
```bash
# Test individual components in isolation
./scripts/test-backend.sh --unit
./scripts/test-frontend.sh --unit

# Focus on business logic and domain entities
# Mock external dependencies
```

#### Integration Tests
```bash
# Test service interactions
./scripts/test-backend.sh --integration

# Test with real database and external services
# Use test containers when possible
```

#### End-to-End Tests
```bash
# Test complete user workflows
./scripts/test-frontend.sh --e2e

# Start full environment for E2E tests
./scripts/dev-start.sh
./scripts/test-all.sh --e2e
```

## Code Review Workflow

### 1. Prepare Pull Request

```bash
# Ensure branch is up to date
git checkout develop
git pull origin develop
git checkout feature/RAG-123-implement-vector-search
git rebase develop

# Run final checks
./scripts/test-all.sh
./scripts/quality-check.sh --all

# Push feature branch
git push origin feature/RAG-123-implement-vector-search
```

### 2. Create Pull Request

- **Title**: Clear, descriptive title following conventional commits
- **Description**: 
  - What was implemented
  - Why it was needed
  - How to test it
  - Screenshots/demos if applicable
- **Checklist**:
  - [ ] Tests added/updated
  - [ ] Documentation updated
  - [ ] No breaking changes
  - [ ] Performance impact considered

### 3. Review Process

#### For Reviewers
```bash
# Checkout PR branch locally
git fetch origin
git checkout feature/RAG-123-implement-vector-search

# Run tests locally
./scripts/test-all.sh

# Check code quality
./scripts/quality-check.sh --all

# Review checklist:
# - Code follows architecture patterns
# - Tests are comprehensive
# - Error handling is appropriate
# - Security considerations addressed
# - Performance implications understood
```

#### For Authors
```bash
# Address review feedback
git add .
git commit -m "fix: address code review feedback"
git push origin feature/RAG-123-implement-vector-search

# Respond to comments
# Update documentation if needed
```

### 4. Merge Process

```bash
# After approval, merge using GitHub UI
# - Use "Squash and merge" for feature branches
# - Use "Merge commit" for release branches
# - Delete feature branch after merge
```

## Release Workflow

### 1. Prepare Release

```bash
# Create release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Update version numbers
# - pyproject.toml
# - frontend/package.json
# - deployment configurations

# Update CHANGELOG.md
# - Add new features
# - Add bug fixes
# - Add breaking changes
```

### 2. Release Testing

```bash
# Run comprehensive test suite
./scripts/test-all.sh --integration --e2e

# Performance testing
./scripts/test-performance.sh

# Security scanning
./scripts/security-scan.sh

# Build and test Docker images
docker build -f deployment/podman/Dockerfile.error-reporting-service .
```

### 3. Deploy to Staging

```bash
# Deploy to staging environment
git push origin release/v1.2.0

# GitHub Actions will automatically deploy to staging
# Monitor deployment and run smoke tests
```

### 4. Production Release

```bash
# Merge to main
git checkout main
git merge release/v1.2.0

# Create and push tag
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# GitHub Actions will deploy to production
```

## Hotfix Workflow

### 1. Create Hotfix Branch

```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/v1.2.1-critical-security-fix
```

### 2. Implement Fix

```bash
# Make minimal changes to fix the issue
# Add tests to prevent regression
./scripts/test-all.sh

# Update version number
# Update CHANGELOG.md
```

### 3. Deploy Hotfix

```bash
# Merge to main
git checkout main
git merge hotfix/v1.2.1-critical-security-fix

# Create tag
git tag -a v1.2.1 -m "Hotfix version 1.2.1"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge main
git push origin develop
```

## Maintenance Workflow

### Daily Maintenance

```bash
# Update dependencies
pip list --outdated
cd frontend && npm outdated

# Run security scans
./scripts/security-scan.sh

# Check system health
./scripts/health-check.sh
```

### Weekly Maintenance

```bash
# Update pre-commit hooks
./scripts/setup-pre-commit.sh --update

# Review and update documentation
# Check for broken links
# Update API documentation

# Performance monitoring
./scripts/performance-report.sh
```

### Monthly Maintenance

```bash
# Dependency updates
pip install --upgrade -r requirements.txt
cd frontend && npm update

# Security audit
npm audit
pip-audit

# Database maintenance
./scripts/db-maintenance.sh

# Clean up old branches
git branch -d $(git branch --merged | grep -v main | grep -v develop)
```

## Best Practices Summary

1. **Always start with tests** - Follow TDD approach
2. **Use feature branches** - Keep main/develop stable
3. **Run quality checks** - Before every commit
4. **Write clear commit messages** - Follow conventional commits
5. **Keep PRs small** - Easier to review and merge
6. **Document changes** - Update docs with code changes
7. **Monitor performance** - Consider impact of changes
8. **Security first** - Scan for vulnerabilities regularly

## Tools and Scripts Reference

- `./scripts/dev-setup.sh` - Initial environment setup
- `./scripts/dev-start.sh` - Start development environment
- `./scripts/test-all.sh` - Run comprehensive tests
- `./scripts/quality-check.sh` - Code quality checks
- `./scripts/local-ci.sh` - Local CI testing
- `./scripts/setup-pre-commit.sh` - Pre-commit hook management

For more detailed information, refer to the individual script help:
```bash
./scripts/[script-name].sh --help
```

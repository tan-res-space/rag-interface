# RAG Interface - Troubleshooting Guide

## Common Development Issues

### Environment Setup Problems

#### Python Virtual Environment Issues

**Problem**: `venv/bin/activate` not found
```bash
# Solution: Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: Python version compatibility
```bash
# Check Python version
python3 --version

# Should be 3.11+. If not, install correct version:
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv

# macOS with Homebrew:
brew install python@3.11
```

#### Node.js and Frontend Issues

**Problem**: `npm install` fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf frontend/node_modules
rm frontend/package-lock.json
cd frontend && npm install
```

**Problem**: Node.js version mismatch
```bash
# Check Node.js version
node --version

# Should be 18+. Install using nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### Docker/Container Issues

#### Container Startup Problems

**Problem**: Docker daemon not running
```bash
# Start Docker service
sudo systemctl start docker

# For Podman:
sudo systemctl start podman
```

**Problem**: Port conflicts
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 $(sudo lsof -t -i:8000)

# Or change port in .env.local
echo "ERS_PORT=8010" >> .env.local
```

**Problem**: Permission denied errors
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# For Podman:
sudo usermod -aG podman $USER
```

#### Database Connection Issues

**Problem**: PostgreSQL connection refused
```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# Check logs
./scripts/dev-logs.sh postgres

# Restart database
make db-restart
```

**Problem**: Database schema not initialized
```bash
# Initialize database
make db-init

# Or manually:
source venv/bin/activate
python -c "
import asyncio
from src.error_reporting_service.infrastructure.config.settings import settings
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
async def main():
    adapter = await DatabaseAdapterFactory.create(settings.database)
    await adapter.create_tables()
asyncio.run(main())
"
```

### Testing Issues

#### Backend Test Failures

**Problem**: Import errors in tests
```bash
# Set PYTHONPATH
export PYTHONPATH=$PWD
pytest tests/unit/

# Or use the test script
./scripts/test-backend.sh
```

**Problem**: Database tests failing
```bash
# Ensure test database is clean
export DATABASE_URL="sqlite:///./test.db"
rm -f test.db
pytest tests/unit/
```

**Problem**: Async test issues
```bash
# Check pytest-asyncio is installed
pip install pytest-asyncio

# Ensure pytest.ini has asyncio_mode = auto
grep "asyncio_mode" pytest.ini
```

#### Frontend Test Failures

**Problem**: Vitest not finding tests
```bash
# Check test file naming
# Should be: *.test.ts, *.test.tsx, *.spec.ts, *.spec.tsx

# Run with verbose output
cd frontend
npm run test -- --reporter=verbose
```

**Problem**: Playwright E2E tests failing
```bash
# Install Playwright browsers
cd frontend
npx playwright install

# Run in headed mode for debugging
npm run test:e2e:headed
```

### Code Quality Issues

#### Pre-commit Hook Failures

**Problem**: Black formatting failures
```bash
# Auto-fix formatting
source venv/bin/activate
black src/ tests/

# Or use quality script
./scripts/quality-check.sh --fix-backend
```

**Problem**: MyPy type checking errors
```bash
# Run MyPy with detailed output
source venv/bin/activate
mypy src/ --show-error-codes --show-traceback

# Common fixes:
# 1. Add type annotations
# 2. Add # type: ignore comments
# 3. Install type stubs: pip install types-requests
```

**Problem**: ESLint errors in frontend
```bash
# Auto-fix ESLint issues
cd frontend
npm run lint -- --fix

# Or use quality script
./scripts/quality-check.sh --fix-frontend
```

### CI/CD Issues

#### GitHub Actions Failures

**Problem**: CI tests failing but local tests pass
```bash
# Test locally with same environment
./scripts/local-ci.sh --simulate

# Check environment differences
# - Python version
# - Node.js version
# - Environment variables
```

**Problem**: Podman build failures in CI
```bash
# Test Podman build locally
podman build -f deployment/podman/Dockerfile.error-reporting-service .

# Check for:
# - Missing files in .containerignore
# - Path case sensitivity
# - Architecture differences
```

#### Local CI Testing Issues

**Problem**: `act` command not found
```bash
# Install act
./scripts/local-ci.sh --install-act

# Or manually:
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

**Problem**: Act workflow failures
```bash
# Check act configuration
cat .actrc

# Run with verbose output
act -j backend-tests --verbose

# Use specific platform
act -j backend-tests --platform ubuntu-latest=catthehacker/ubuntu:act-latest
```

### Performance Issues

#### Slow Development Environment

**Problem**: Services taking too long to start
```bash
# Check system resources
docker stats
# or
podman stats

# Reduce services if needed
# Comment out unused services in docker-compose.dev.yml
```

**Problem**: Hot-reload not working
```bash
# Check file watching limits (Linux)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# For containers, ensure polling is enabled
export WATCHFILES_FORCE_POLLING=true
export CHOKIDAR_USEPOLLING=true
```

#### Slow Tests

**Problem**: Tests running slowly
```bash
# Run tests in parallel
pytest tests/unit/ -n auto

# Use faster test database
export DATABASE_URL="sqlite:///:memory:"

# Skip slow tests
pytest tests/unit/ -m "not slow"
```

### Security Issues

#### Secrets and API Keys

**Problem**: Secrets detected in commits
```bash
# Check secrets baseline
detect-secrets scan --baseline .secrets.baseline

# Update baseline if needed
detect-secrets scan --update .secrets.baseline

# Remove secrets from git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret/file' \
  --prune-empty --tag-name-filter cat -- --all
```

**Problem**: Vulnerability scan failures
```bash
# Update dependencies
pip install --upgrade -r requirements.txt
cd frontend && npm audit fix

# Check for security advisories
pip-audit
npm audit
```

### Debugging Tips

#### Enable Debug Logging

```bash
# Backend services
export LOG_LEVEL=DEBUG
./scripts/dev-start.sh

# Frontend
export NODE_ENV=development
export VITE_LOG_LEVEL=debug
```

#### Debug Containers

```bash
# Execute into running container
docker exec -it ers-dev /bin/bash
# or
podman exec -it ers-dev /bin/bash

# Check container logs
./scripts/dev-logs.sh error-reporting-service
```

#### Debug Tests

```bash
# Run single test with pdb
pytest tests/unit/test_example.py::test_function -s --pdb

# Frontend test debugging
cd frontend
npm run test:ui  # Opens Vitest UI
```

### Getting Additional Help

#### Log Analysis

```bash
# Collect all logs
mkdir debug-logs
./scripts/dev-logs.sh > debug-logs/services.log
cp test-results/*.xml debug-logs/
cp quality-reports/*.json debug-logs/
```

#### System Information

```bash
# Collect system info
echo "=== System Info ===" > debug-info.txt
uname -a >> debug-info.txt
python3 --version >> debug-info.txt
node --version >> debug-info.txt
docker --version >> debug-info.txt
echo "=== Disk Space ===" >> debug-info.txt
df -h >> debug-info.txt
echo "=== Memory ===" >> debug-info.txt
free -h >> debug-info.txt
```

#### Reset Everything

```bash
# Nuclear option - reset everything
./scripts/dev-stop.sh clean
rm -rf venv/
rm -rf frontend/node_modules/
rm -rf test-results/
rm -rf quality-reports/
rm -f .env.local

# Start fresh
./scripts/dev-setup.sh
```

## Contact and Support

- **Documentation**: Check `docs/` directory
- **Issues**: Create GitHub issue with debug information
- **Logs**: Always include relevant log files
- **Environment**: Include system information and versions

Remember to never include sensitive information (API keys, passwords) in debug logs or issue reports.

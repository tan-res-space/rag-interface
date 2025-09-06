# RAG Interface System

**A comprehensive ASR Error Reporting and Correction Platform**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/tan-res-space/rag-interface)
[![Coverage](https://img.shields.io/badge/coverage-85%25-green)](./test-results/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![React](https://img.shields.io/badge/react-18+-blue)](https://reactjs.org)

## 🎯 Overview

The RAG Interface System is a sophisticated platform for managing ASR (Automatic Speech Recognition) error reporting and correction using advanced AI/ML techniques. Built with modern microservices architecture, it provides a comprehensive solution for healthcare environments requiring high-accuracy speech recognition.

### Key Features

- 🔍 **Error Reporting**: Comprehensive error capture and validation
- 📊 **Analytics Dashboard**: Real-time metrics and visualizations  
- 👥 **Speaker Management**: Quality-based bucket progression system
- 🔄 **Verification Workflow**: Multi-stage validation process
- 🤖 **AI Integration**: RAG-based correction suggestions
- 🔐 **Security**: JWT authentication with role-based access
- 📱 **Responsive UI**: Modern React interface with Material-UI

## 🏗️ Architecture

### Backend Microservices (Python + FastAPI)
- **Error Reporting Service** (Port 8000) - Core error management
- **User Management Service** (Port 8001) - Authentication & authorization
- **Verification Service** (Port 8002) - Multi-stage validation
- **Correction Engine Service** (Port 8003) - AI-powered corrections
- **RAG Integration Service** (Port 8004) - Vector search & embeddings

### Frontend Application (React + TypeScript)
- Modern React 18+ with TypeScript
- Redux Toolkit for state management
- Material-UI for consistent design
- Playwright for E2E testing

### Infrastructure
- **Database**: PostgreSQL with automated migrations
- **Caching**: Redis for performance optimization
- **Messaging**: Kafka for event-driven communication
- **Containers**: Podman/Docker deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Podman/Docker
- PostgreSQL 12+

### Installation

```bash
# Clone the repository
git clone https://github.com/tan-res-space/rag-interface.git
cd rag-interface

# Backend setup
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Environment configuration
cp .env.template .env
# Edit .env with your configuration

# Database setup
make db-setup

# Start all services
make dev-start
```

### Verification

```bash
# Validate installation
python validate_setup.py

# Run tests
make test-all

# Check service health
curl http://localhost:8000/health
```

## 📚 Documentation

### For Users
- **[User Manual](docs/user-guides/USER_MANUAL.md)** - Complete user guide
- **[Quick Reference](docs/user-guides/QUICK_REFERENCE.md)** - Essential commands
- **[Troubleshooting](docs/user-guides/TROUBLESHOOTING_GUIDE.md)** - Common issues & solutions

### For Developers
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical overview
- **[Development Guide](docs/development/DEVELOPMENT_GUIDE.md)** - Development workflows
- **[API Documentation](docs/api/)** - REST API reference
- **[Architecture Guide](docs/architecture/)** - System architecture

### For Operations
- **[Deployment Guide](docs/deployment/README.md)** - Production deployment
- **[Maintenance Guide](docs/deployment/MAINTENANCE_GUIDE.md)** - Operations procedures

## 🧪 Testing

### Test Coverage
- **Backend**: 85%+ coverage with 200+ unit tests
- **Frontend**: 80%+ coverage with component & E2E tests
- **Integration**: Full API integration testing
- **E2E**: Playwright browser automation

### Running Tests

```bash
# All tests
make test-all

# Backend only
make test-backend

# Frontend only
make test-frontend

# E2E tests
cd frontend && npm run test:e2e
```

## 🔧 Development

### Technology Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Alembic
- **Frontend**: React 18, TypeScript, Redux Toolkit, Material-UI
- **Database**: PostgreSQL, Redis
- **Testing**: Pytest, Playwright, Vitest
- **DevOps**: Podman, GitHub Actions, Pre-commit hooks

### Code Quality
- **Linting**: ESLint, Flake8, Black, isort
- **Type Checking**: TypeScript, MyPy
- **Security**: Bandit security scanning
- **Pre-commit**: Automated code quality checks

## 📊 Project Status

- ✅ **Backend Services**: 5/5 microservices complete
- ✅ **Frontend Application**: Full React implementation
- ✅ **Testing Infrastructure**: Comprehensive test coverage
- ✅ **CI/CD Pipeline**: Automated testing & deployment
- ✅ **Documentation**: Complete user & developer docs
- ✅ **Container Deployment**: Production-ready containers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/tan-res-space/rag-interface/issues)
- **Documentation**: [Project Wiki](https://github.com/tan-res-space/rag-interface/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/tan-res-space/rag-interface/discussions)

---

**Built with ❤️ for healthcare ASR accuracy**

# System Health Feature

This feature provides real-time monitoring and diagnostics for all backend services in the RAG Interface application.

## Architecture

Following the Hexagonal Architecture pattern:

- **Pages**: Main page components
- **Components**: Reusable UI components for health monitoring
- **Hooks**: Custom React hooks for health data management
- **Types**: TypeScript interfaces and types
- **API**: Health check API client integration

## Services Monitored

- Error Reporting Service (port 8000)
- User Management Service (port 8001) 
- RAG Integration Service (port 8002)
- Correction Engine Service (port 8003)
- Verification Service (port 8004)

## Features

- Real-time service status monitoring
- Response time measurements
- Uptime statistics
- Auto-refresh capability
- Diagnostic information
- Export functionality
- Troubleshooting suggestions

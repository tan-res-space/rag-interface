"""
Main FastAPI application for the Error Reporting Service.

This module sets up the FastAPI application with all necessary middleware,
routes, and dependency injection following Hexagonal Architecture principles.

Documentation:
- Architecture Design: docs/architecture/01_Error_Reporting_Service_Design.md
- API Reference: docs/api/enhanced_error_reporting_api.md
- User Guide: docs/user-guides/ASR_Error_Reporting_PRD.md
- Development Guide: docs/development/DEVELOPMENT_GUIDE.md
"""

import logging
import uuid
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from error_reporting_service.infrastructure.adapters.web.api.v1 import error_reports, speaker_profiles

# Application imports
from error_reporting_service.infrastructure.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Error Reporting Service",
    description="ASR Error Reporting and Quality Assurance Service",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
trusted_hosts = ["*"] if settings.debug else ["localhost", "127.0.0.1"]
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=trusted_hosts
)


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request ID to all requests for tracing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")

        error_response = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": str(e) if settings.debug else "Internal server error",
            },
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
            "version": "1.0.0",
        }

        return JSONResponse(status_code=500, content=error_response)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "error-reporting-service",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Error Reporting Service",
        "version": "1.0.0",
        "status": "running",
        "docs": (
            "/docs" if settings.debug else "Documentation not available in production"
        ),
    }


# Include API routes
app.include_router(error_reports.router, prefix="/api/v1", tags=["error-reports"])
app.include_router(speaker_profiles.router, tags=["speaker-profiles"])

# Development auth endpoint (replace with real authentication in production)
@app.get("/api/v1/auth/me")
async def get_current_user():
    """Development auth endpoint - replace with real authentication in production"""
    if settings.debug:
        # Return mock user for development
        return {
            "id": "dev-user-123",
            "username": "dev-user",
            "email": "dev@example.com",
            "role": "QA_ANALYST",
            "roles": ["QA_ANALYST", "USER"],
            "firstName": "Dev",
            "lastName": "User",
            "isActive": True,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }
    else:
        # In production, this should validate JWT tokens
        raise HTTPException(
            status_code=501,
            detail="Authentication not implemented for production. Please implement JWT validation."
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    error_response = {
        "success": False,
        "error": {
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
        "version": "1.0.0",
    }

    return JSONResponse(status_code=exc.status_code, content=error_response)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions"""
    error_response = {
        "success": False,
        "error": {"code": "INVALID_REQUEST", "message": str(exc)},
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
        "version": "1.0.0",
    }

    return JSONResponse(status_code=400, content=error_response)


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    """Handle PermissionError exceptions"""
    error_response = {
        "success": False,
        "error": {
            "code": "UNAUTHORIZED" if "Access denied" in str(exc) else "FORBIDDEN",
            "message": str(exc),
        },
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
        "version": "1.0.0",
    }

    status_code = 401 if "Access denied" in str(exc) else 403

    return JSONResponse(status_code=status_code, content=error_response)


# Startup and shutdown events
async def initialize_dependency_injection():
    """Initialize dependency injection container"""
    logger.info("Initializing dependency injection...")
    try:
        from shared.infrastructure.dependency_injection.container import initialize_container

        # Build configuration for DI container
        config = {
            "database": {
                "type": settings.database.type.value,
                "host": settings.database.host,
                "port": settings.database.port,
                "database": settings.database.database,
                "username": settings.database.username,
                "password": settings.database.password
            }
        }

        # Initialize container
        container = await initialize_container(config)
        app.state.di_container = container

        logger.info("Dependency injection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize dependency injection: {e}")


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Error Reporting Service starting up...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")

    # Initialize dependency injection
    await initialize_dependency_injection()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Error Reporting Service shutting down...")

    # Dispose dependency injection container
    if hasattr(app.state, 'di_container'):
        await app.state.di_container.dispose()
        logger.info("Dependency injection container disposed")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

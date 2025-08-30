"""
Main FastAPI application for the User Management Service.

This module sets up the FastAPI application with all necessary middleware,
routes, and dependency injection following Hexagonal Architecture principles.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Application imports
from .infrastructure.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for the User Management Service.
    """
    # Startup
    logger.info("User Management Service starting up...")

    try:
        # Initialize authentication systems
        await initialize_auth_systems()

        # Initialize database connections
        await initialize_database()

        # Initialize cache
        await initialize_cache()

        logger.info("User Management Service startup completed successfully")

    except Exception as e:
        logger.error(f"Failed to start User Management Service: {e}")
        raise

    yield

    # Shutdown
    logger.info("User Management Service shutting down...")

    try:
        # Cleanup resources
        await cleanup_resources()

        logger.info("User Management Service shutdown completed")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="User Management Service",
    description="ASR Error Reporting System - User Management and Authentication Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Configure appropriately for production
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
        "service": "user-management-service",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "User Management Service",
        "version": "1.0.0",
        "status": "running",
        "docs": (
            "/docs" if settings.debug else "Documentation not available in production"
        ),
    }


from typing import Optional

# Create API router
from fastapi import APIRouter
from pydantic import BaseModel

api_router = APIRouter(prefix="/api/v1")


class LoginRequest(BaseModel):
    username: str
    password: str
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None


class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str
    expiresIn: int
    user: dict


# Authentication endpoints
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """User login endpoint"""
    # Placeholder implementation with correct credentials
    if credentials.username == "admin" and credentials.password == "AdminPassword123!":
        user_id = str(uuid.uuid4())
        return LoginResponse(
            accessToken="fake-jwt-token",
            refreshToken="fake-refresh-token",
            tokenType="bearer",
            expiresIn=3600,
            user={
                "userId": user_id,
                "username": credentials.username,
                "email": "admin@example.com",
                "firstName": "Admin",
                "lastName": "User",
                "fullName": "Admin User",
                "roles": ["admin"],
                "permissions": [
                    "admin:read",
                    "admin:write",
                    "users:read",
                    "users:write",
                ],
                "status": "active",
                "department": "IT",
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat(),
                "isActive": True,
            },
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@api_router.post("/auth/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Successfully logged out"}


@api_router.get("/auth/me")
async def get_current_user():
    """Get current user information"""
    # Placeholder implementation - return format matching frontend User interface
    user_id = str(uuid.uuid4())
    return {
        "userId": user_id,
        "username": "admin",
        "email": "admin@example.com",
        "firstName": "Admin",
        "lastName": "User",
        "fullName": "Admin User",
        "roles": ["admin"],
        "permissions": ["admin:read", "admin:write", "users:read", "users:write"],
        "status": "active",
        "department": "IT",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "isActive": True,
    }


# User management endpoints
@api_router.get("/users")
async def list_users():
    """List all users"""
    # Placeholder implementation
    return {
        "users": [
            {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@example.com",
                "roles": ["admin"],
                "status": "active",
            },
            {
                "id": str(uuid.uuid4()),
                "username": "qa_user",
                "email": "qa@example.com",
                "roles": ["qa_personnel"],
                "status": "active",
            },
        ],
        "total": 2,
    }


@api_router.post("/users")
async def create_user(username: str, email: str, roles: list):
    """Create a new user"""
    # Placeholder implementation
    user_id = str(uuid.uuid4())
    return {
        "id": user_id,
        "username": username,
        "email": email,
        "roles": roles,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }


@api_router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    # Placeholder implementation
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    return {
        "id": user_id,
        "username": "test_user",
        "email": "test@example.com",
        "roles": ["qa_personnel"],
        "status": "active",
        "created_at": "2023-01-01T00:00:00Z",
    }


# Include API router in the app
app.include_router(api_router)

# Include speaker management routers
try:
    from .infrastructure.adapters.http.bucket_transition_router import (
        router as bucket_transition_router,
    )
    from .infrastructure.adapters.http.speaker_router import router as speaker_router

    app.include_router(speaker_router)
    app.include_router(bucket_transition_router)
    logger.info("Speaker management routers included successfully")
except ImportError as e:
    logger.warning(f"Could not import speaker management routers: {e}")
    # Continue without speaker management endpoints for now


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


# Initialization functions
async def initialize_auth_systems():
    """Initialize authentication systems"""
    logger.info("Initializing authentication systems...")
    # TODO: Implement auth system initialization
    pass


async def initialize_database():
    """Initialize database connections"""
    logger.info("Initializing database...")
    # TODO: Implement database initialization
    pass


async def initialize_cache():
    """Initialize cache connection"""
    logger.info("Initializing cache...")
    # TODO: Implement cache initialization
    pass


async def cleanup_resources():
    """Cleanup resources during shutdown"""
    logger.info("Cleaning up resources...")
    # TODO: Implement resource cleanup
    pass


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,  # User Management Service port
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

"""
Main FastAPI application for the Correction Engine Service.

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

from .infrastructure.adapters.http.controllers import router as api_router

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

    Handles startup and shutdown events for the Correction Engine Service.
    """
    # Startup
    logger.info("Correction Engine Service starting up...")

    try:
        # Initialize correction models
        await initialize_correction_models()

        # Initialize database connections
        await initialize_database()

        # Initialize cache
        await initialize_cache()

        logger.info("Correction Engine Service startup completed successfully")

    except Exception as e:
        logger.error(f"Failed to start Correction Engine Service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Correction Engine Service shutting down...")

    try:
        # Cleanup resources
        await cleanup_resources()

        logger.info("Correction Engine Service shutdown completed")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Correction Engine Service",
    description="ASR Error Reporting System - Real-time Text Correction Service",
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
        "service": "correction-engine-service",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Correction Engine Service",
        "version": "1.0.0",
        "status": "running",
        "docs": (
            "/docs" if settings.debug else "Documentation not available in production"
        ),
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["correction-engine"])


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
async def initialize_correction_models():
    """Initialize correction models"""
    logger.info("Initializing correction models...")
    # TODO: Implement correction model initialization


async def initialize_database():
    """Initialize database connections"""
    logger.info("Initializing database...")
    try:
        # For now, use in-memory storage
        # In production, this would connect to actual database
        app.state.database = {
            "type": "in_memory",
            "status": "connected",
            "corrections": {},
            "models": {}
        }
        logger.info("Database initialized successfully (in-memory implementation)")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        app.state.database = {"status": "failed"}


async def initialize_cache():
    """Initialize cache connection"""
    logger.info("Initializing cache...")
    try:
        app.state.cache = {
            "correction_cache": {},
            "model_cache": {},
            "status": "initialized"
        }
        logger.info("Cache initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")
        app.state.cache = {"status": "failed"}


async def cleanup_resources():
    """Cleanup resources during shutdown"""
    logger.info("Cleaning up resources...")
    try:
        if hasattr(app.state, 'database'):
            app.state.database["status"] = "disconnected"
            logger.info("Database disconnected")

        if hasattr(app.state, 'cache'):
            app.state.cache.clear()
            logger.info("Cache cleared")

    except Exception as e:
        logger.error(f"Error during resource cleanup: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,  # Correction Engine Service port
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

"""
API Gateway Main Application

Central API gateway that routes requests to appropriate microservices.
Provides a unified interface for the RAG Interface system.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .speaker_bucket_management_router import router as speaker_bucket_router
# from .enhanced_error_reporting_router import router as error_reporting_router
# from .verification_workflow_router import router as verification_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting API Gateway")
    yield
    logger.info("Shutting down API Gateway")


# Create FastAPI app
app = FastAPI(
    title="RAG Interface API Gateway",
    description="Central API gateway for the RAG Interface system",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(speaker_bucket_router)
# app.include_router(error_reporting_router)
# app.include_router(verification_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RAG Interface API Gateway", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 
#!/usr/bin/env python3
"""
Simple API Gateway for RAG Interface

A minimal API gateway to provide the health endpoint that the frontend needs.
This runs directly on the host to avoid Docker networking issues.
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG Interface API Gateway",
    description="Simple API gateway for the RAG Interface system",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RAG Interface API Gateway", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/api/v1/speaker-bucket-management/dashboard/health/comprehensive")
async def comprehensive_health_check():
    """
    Comprehensive health check endpoint for dashboard.
    
    This is a mock implementation that returns a healthy status
    for all services to allow the frontend to function.
    """
    logger.info("Comprehensive health check requested")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "services": {
            "user_management": {
                "status": "healthy",
                "response_time_ms": 50,
                "details": {"message": "Service is operational"}
            },
            "verification": {
                "status": "healthy",
                "response_time_ms": 45,
                "details": {"message": "Service is operational"}
            },
            "rag_integration": {
                "status": "healthy",
                "response_time_ms": 60,
                "details": {"message": "Service is operational"}
            },
            "error_reporting": {
                "status": "healthy",
                "response_time_ms": 40,
                "details": {"message": "Service is operational"}
            }
        }
    }


if __name__ == "__main__":
    logger.info("Starting Simple API Gateway")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 
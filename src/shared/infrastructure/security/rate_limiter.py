"""
Rate Limiting System

Advanced rate limiting for API endpoints with multiple strategies.
Provides protection against abuse and ensures fair resource usage.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import json

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded."""
    
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)} if retry_after else None
        )


class InMemoryRateLimiter:
    """
    In-memory rate limiter using token bucket algorithm.
    
    Suitable for single-instance deployments or when Redis is not available.
    """

    def __init__(self):
        """Initialize in-memory rate limiter."""
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
        cost: int = 1
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier for rate limiting
            limit: Maximum requests allowed
            window: Time window in seconds
            cost: Cost of this request (default: 1)
            
        Returns:
            Tuple of (allowed, info_dict)
        """
        current_time = time.time()
        
        # Cleanup old buckets periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_buckets()
            self.last_cleanup = current_time
        
        # Get or create bucket
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": limit,
                "last_refill": current_time,
                "limit": limit,
                "window": window
            }
        
        bucket = self.buckets[key]
        
        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = (time_elapsed / window) * limit
        bucket["tokens"] = min(limit, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time
        
        # Check if request is allowed
        if bucket["tokens"] >= cost:
            bucket["tokens"] -= cost
            allowed = True
        else:
            allowed = False
        
        # Calculate retry after
        retry_after = None
        if not allowed:
            tokens_needed = cost - bucket["tokens"]
            retry_after = int((tokens_needed / limit) * window)
        
        info = {
            "limit": limit,
            "remaining": int(bucket["tokens"]),
            "reset_time": int(current_time + window),
            "retry_after": retry_after
        }
        
        return allowed, info

    async def _cleanup_buckets(self):
        """Remove old, unused buckets."""
        current_time = time.time()
        keys_to_remove = []
        
        for key, bucket in self.buckets.items():
            # Remove buckets that haven't been used for 2x their window
            if current_time - bucket["last_refill"] > bucket["window"] * 2:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.buckets[key]
        
        if keys_to_remove:
            logger.debug(f"Cleaned up {len(keys_to_remove)} old rate limit buckets")


class RedisRateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.
    
    Suitable for distributed deployments with multiple service instances.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis rate limiter.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if not self.redis_client:
            self.redis_client = redis.from_url(self.redis_url)

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
        cost: int = 1
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit using Redis.
        
        Args:
            key: Unique identifier for rate limiting
            limit: Maximum requests allowed
            window: Time window in seconds
            cost: Cost of this request
            
        Returns:
            Tuple of (allowed, info_dict)
        """
        if not self.redis_client:
            await self.connect()
        
        current_time = time.time()
        pipeline = self.redis_client.pipeline()
        
        # Sliding window implementation
        window_start = current_time - window
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipeline.expire(key, window + 1)
        
        results = await pipeline.execute()
        current_count = results[1]
        
        # Check if allowed
        allowed = current_count + cost <= limit
        
        if not allowed:
            # Remove the request we just added since it's not allowed
            await self.redis_client.zrem(key, str(current_time))
        
        # Calculate retry after
        retry_after = None
        if not allowed:
            # Get the oldest request time
            oldest_requests = await self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest_requests:
                oldest_time = oldest_requests[0][1]
                retry_after = int(oldest_time + window - current_time)
        
        info = {
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "reset_time": int(current_time + window),
            "retry_after": retry_after
        }
        
        return allowed, info


class RateLimitMiddleware:
    """
    FastAPI middleware for rate limiting.
    
    Applies rate limits to incoming requests based on configurable rules.
    """

    def __init__(
        self,
        limiter: Optional[InMemoryRateLimiter] = None,
        redis_limiter: Optional[RedisRateLimiter] = None,
        default_limit: int = 100,
        default_window: int = 60,
        key_func: Optional[Callable[[Request], str]] = None
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            limiter: In-memory rate limiter
            redis_limiter: Redis rate limiter (preferred if available)
            default_limit: Default request limit
            default_window: Default time window in seconds
            key_func: Function to generate rate limit key from request
        """
        self.limiter = redis_limiter or limiter or InMemoryRateLimiter()
        self.default_limit = default_limit
        self.default_window = default_window
        self.key_func = key_func or self._default_key_func
        
        # Rate limit rules for different endpoints
        self.rules = {
            "/api/v1/embeddings": {"limit": 50, "window": 60},
            "/api/v1/similarity/search": {"limit": 100, "window": 60},
            "/api/v1/error-reports": {"limit": 200, "window": 60},
            "/auth/login": {"limit": 5, "window": 300},  # Stricter for auth
            "/auth/register": {"limit": 3, "window": 3600},  # Very strict for registration
        }

    def _default_key_func(self, request: Request) -> str:
        """
        Default function to generate rate limit key.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Rate limit key
        """
        # Use client IP as default key
        client_ip = request.client.host if request.client else "unknown"
        
        # Include user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}:{request.url.path}"
        
        return f"ip:{client_ip}:{request.url.path}"

    async def __call__(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or rate limit error
        """
        # Generate rate limit key
        key = self.key_func(request)
        
        # Get rate limit rules for this endpoint
        path = request.url.path
        rule = self.rules.get(path, {
            "limit": self.default_limit,
            "window": self.default_window
        })
        
        # Check rate limit
        try:
            allowed, info = await self.limiter.is_allowed(
                key=key,
                limit=rule["limit"],
                window=rule["window"]
            )
            
            if not allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "limit": info["limit"],
                        "remaining": info["remaining"],
                        "reset_time": info["reset_time"]
                    },
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(info["reset_time"]),
                        "Retry-After": str(info["retry_after"]) if info["retry_after"] else "60"
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset_time"])
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if there's an error
            return await call_next(request)


def create_rate_limiter(redis_url: Optional[str] = None) -> RateLimitMiddleware:
    """
    Create rate limiter middleware.
    
    Args:
        redis_url: Redis URL for distributed rate limiting
        
    Returns:
        Rate limit middleware instance
    """
    if redis_url:
        redis_limiter = RedisRateLimiter(redis_url)
        return RateLimitMiddleware(redis_limiter=redis_limiter)
    else:
        return RateLimitMiddleware()


# Decorator for endpoint-specific rate limiting
def rate_limit(limit: int, window: int = 60):
    """
    Decorator for endpoint-specific rate limiting.
    
    Args:
        limit: Request limit
        window: Time window in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func):
        func._rate_limit = {"limit": limit, "window": window}
        return func
    return decorator

"""
Base HTTP Client

Base HTTP client for service-to-service communication.
Provides common functionality for all service clients.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class BaseHTTPClient:
    """
    Base HTTP client for service communication.
    
    Provides common functionality like authentication, retries, and error handling.
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        auth_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize HTTP client.
        
        Args:
            base_url: Base URL for the service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            auth_token: Authentication token
            headers: Additional headers
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.auth_token = auth_token
        
        # Setup default headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "RAG-Interface-Service/1.0"
        }
        
        if headers:
            self.headers.update(headers)
        
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers=self.headers,
            follow_redirects=True
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            
        Returns:
            HTTP response
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        
        if headers:
            request_headers.update(headers)
        
        logger.debug(f"GET {url}")
        
        try:
            response = await self.client.get(
                url,
                params=params,
                headers=request_headers
            )
            
            logger.debug(f"GET {url} -> {response.status_code}")
            return response
            
        except httpx.RequestError as e:
            logger.error(f"GET {url} failed: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Additional headers
            
        Returns:
            HTTP response
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        
        if headers:
            request_headers.update(headers)
        
        logger.debug(f"POST {url}")
        
        try:
            response = await self.client.post(
                url,
                data=data,
                json=json,
                headers=request_headers
            )
            
            logger.debug(f"POST {url} -> {response.status_code}")
            return response
            
        except httpx.RequestError as e:
            logger.error(f"POST {url} failed: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        Make PUT request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Additional headers
            
        Returns:
            HTTP response
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        
        if headers:
            request_headers.update(headers)
        
        logger.debug(f"PUT {url}")
        
        try:
            response = await self.client.put(
                url,
                data=data,
                json=json,
                headers=request_headers
            )
            
            logger.debug(f"PUT {url} -> {response.status_code}")
            return response
            
        except httpx.RequestError as e:
            logger.error(f"PUT {url} failed: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        Make DELETE request.
        
        Args:
            endpoint: API endpoint
            headers: Additional headers
            
        Returns:
            HTTP response
        """
        url = self._build_url(endpoint)
        request_headers = self.headers.copy()
        
        if headers:
            request_headers.update(headers)
        
        logger.debug(f"DELETE {url}")
        
        try:
            response = await self.client.delete(
                url,
                headers=request_headers
            )
            
            logger.debug(f"DELETE {url} -> {response.status_code}")
            return response
            
        except httpx.RequestError as e:
            logger.error(f"DELETE {url} failed: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {self.base_url}: {e}")
            return False

    async def get_json(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request and return JSON response.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            
        Returns:
            JSON response data
            
        Raises:
            httpx.HTTPStatusError: If response status is not successful
        """
        response = await self.get(endpoint, params, headers)
        response.raise_for_status()
        return response.json()

    async def post_json(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request and return JSON response.
        
        Args:
            endpoint: API endpoint
            json: JSON data
            headers: Additional headers
            
        Returns:
            JSON response data
            
        Raises:
            httpx.HTTPStatusError: If response status is not successful
        """
        response = await self.post(endpoint, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    def set_auth_token(self, token: str):
        """Update authentication token."""
        self.auth_token = token
        self.headers["Authorization"] = f"Bearer {token}"
        
        # Update client headers
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    def remove_auth_token(self):
        """Remove authentication token."""
        self.auth_token = None
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
        
        # Update client headers
        if "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]

"""
Unit tests for GetErrorReportUseCase.

Following TDD principles - tests define the expected behavior.
This test suite covers all scenarios for retrieving error reports
including authorization, caching, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from datetime import datetime

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport, SeverityLevel, ErrorStatus
)
from src.error_reporting_service.application.use_cases.get_error_report import (
    GetErrorReportUseCase
)
from src.error_reporting_service.application.dto.requests import (
    GetErrorReportRequest
)
from src.error_reporting_service.application.dto.responses import (
    GetErrorReportResponse
)
from src.error_reporting_service.application.ports.secondary.repository_port import (
    ErrorReportRepository
)
from src.error_reporting_service.application.ports.secondary.cache_port import (
    CachePort
)
from src.error_reporting_service.application.ports.secondary.authorization_port import (
    AuthorizationPort
)
from tests.factories import ErrorReportFactory


class TestGetErrorReportUseCase:
    """Test suite for GetErrorReportUseCase"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_repository = AsyncMock(spec=ErrorReportRepository)
        self.mock_cache = AsyncMock(spec=CachePort)
        self.mock_authorization = AsyncMock(spec=AuthorizationPort)
        
        self.use_case = GetErrorReportUseCase(
            repository=self.mock_repository,
            cache=self.mock_cache,
            authorization=self.mock_authorization
        )
    
    @pytest.mark.asyncio
    async def test_execute_existing_error_report_success(self):
        """Test successful retrieval of existing error report"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        error_report = ErrorReportFactory.create(error_id=uuid4())
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id
        )
        
        # Mock authorization check
        self.mock_authorization.can_access_error_report.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository retrieval
        self.mock_repository.find_by_id.return_value = error_report
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert isinstance(response, GetErrorReportResponse)
        assert response.error_report is not None
        assert response.error_report.error_id == str(error_report.error_id)
        assert response.status == "success"
        
        # Verify interactions
        self.mock_authorization.can_access_error_report.assert_called_once_with(
            user_id, error_id
        )
        self.mock_cache.get.assert_called_once_with(f"error_report:{error_id}")
        self.mock_repository.find_by_id.assert_called_once()
        self.mock_cache.set.assert_called_once()  # Should cache the result
    
    @pytest.mark.asyncio
    async def test_execute_cached_error_report_success(self):
        """Test successful retrieval from cache"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        cached_error_data = {
            "error_id": error_id,
            "original_text": "cached text",
            "corrected_text": "cached corrected text"
        }
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id
        )
        
        # Mock authorization check
        self.mock_authorization.can_access_error_report.return_value = True
        
        # Mock cache hit
        self.mock_cache.get.return_value = cached_error_data
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert response.error_report is not None
        
        # Verify repository was not called due to cache hit
        self.mock_repository.find_by_id.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_unauthorized_access_denied(self):
        """Test access denied for unauthorized user"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id
        )
        
        # Mock authorization check to deny access
        self.mock_authorization.can_access_error_report.return_value = False
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Access denied"):
            await self.use_case.execute(request)
        
        # Verify cache and repository were not accessed
        self.mock_cache.get.assert_not_called()
        self.mock_repository.find_by_id.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_error_report_not_found(self):
        """Test handling of non-existent error report"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id
        )
        
        # Mock authorization check
        self.mock_authorization.can_access_error_report.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository to return None (not found)
        self.mock_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Error report not found"):
            await self.use_case.execute(request)
        
        # Verify cache was not updated for non-existent report
        self.mock_cache.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_invalid_error_id_format(self):
        """Test handling of invalid error ID format"""
        # Arrange
        invalid_error_id = "invalid-uuid-format"
        user_id = str(uuid4())
        
        request = GetErrorReportRequest(
            error_id=invalid_error_id,
            requested_by=user_id
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid error ID format"):
            await self.use_case.execute(request)
        
        # Verify no external services were called
        self.mock_authorization.can_access_error_report.assert_not_called()
        self.mock_cache.get.assert_not_called()
        self.mock_repository.find_by_id.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_repository_error_handling(self):
        """Test handling of repository errors"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id
        )
        
        # Mock authorization check
        self.mock_authorization.can_access_error_report.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository to raise error
        self.mock_repository.find_by_id.side_effect = Exception("Database connection failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            await self.use_case.execute(request)
    
    @pytest.mark.asyncio
    async def test_execute_cache_error_fallback_to_repository(self):
        """Test fallback to repository when cache fails"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        error_report = ErrorReportFactory.create()
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id
        )
        
        # Mock authorization check
        self.mock_authorization.can_access_error_report.return_value = True
        
        # Mock cache to raise error
        self.mock_cache.get.side_effect = Exception("Cache unavailable")
        
        # Mock repository retrieval
        self.mock_repository.find_by_id.return_value = error_report
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert response.error_report is not None
        
        # Verify repository was called despite cache error
        self.mock_repository.find_by_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_with_include_metadata_flag(self):
        """Test retrieval with metadata inclusion flag"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        error_report = ErrorReportFactory.create(
            metadata={"audio_quality": "good", "confidence_score": 0.95}
        )
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id,
            include_metadata=True
        )
        
        # Mock authorization check
        self.mock_authorization.can_access_error_report.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository retrieval
        self.mock_repository.find_by_id.return_value = error_report
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.error_report.metadata is not None
        assert response.error_report.metadata["audio_quality"] == "good"
    
    @pytest.mark.asyncio
    async def test_execute_with_exclude_metadata_flag(self):
        """Test retrieval with metadata exclusion flag"""
        # Arrange
        error_id = str(uuid4())
        user_id = str(uuid4())
        error_report = ErrorReportFactory.create(
            metadata={"audio_quality": "good", "confidence_score": 0.95}
        )
        
        request = GetErrorReportRequest(
            error_id=error_id,
            requested_by=user_id,
            include_metadata=False
        )
        
        # Mock authorization check
        self.mock_authorization.can_access_error_report.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository retrieval
        self.mock_repository.find_by_id.return_value = error_report
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.error_report.metadata == {}  # Metadata should be excluded

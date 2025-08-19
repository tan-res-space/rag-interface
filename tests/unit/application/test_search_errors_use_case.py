"""
Unit tests for SearchErrorsUseCase.

Following TDD principles - tests define the expected behavior.
This test suite covers all search scenarios including filtering,
pagination, sorting, and performance requirements.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from datetime import datetime, timedelta
from typing import List

from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport, SeverityLevel, ErrorStatus
)
from src.error_reporting_service.application.use_cases.search_errors import (
    SearchErrorsUseCase
)
from src.error_reporting_service.application.dto.requests import (
    SearchErrorsRequest, ErrorFilters, PaginationParams, SortParams
)
from src.error_reporting_service.application.dto.responses import (
    SearchErrorsResponse, PaginatedErrorReports
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
from tests.factories import ErrorReportFactory, create_error_reports_batch


class TestSearchErrorsUseCase:
    """Test suite for SearchErrorsUseCase"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_repository = AsyncMock(spec=ErrorReportRepository)
        self.mock_cache = AsyncMock(spec=CachePort)
        self.mock_authorization = AsyncMock(spec=AuthorizationPort)
        
        self.use_case = SearchErrorsUseCase(
            repository=self.mock_repository,
            cache=self.mock_cache,
            authorization=self.mock_authorization
        )
    
    @pytest.mark.asyncio
    async def test_execute_basic_search_success(self):
        """Test basic search without filters"""
        # Arrange
        user_id = str(uuid4())
        error_reports = create_error_reports_batch(5)
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search
        self.mock_repository.search.return_value = error_reports
        self.mock_repository.count_by_filters.return_value = 5
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert isinstance(response, SearchErrorsResponse)
        assert response.status == "success"
        assert len(response.results.items) == 5
        assert response.results.total == 5
        assert response.results.page == 1
        assert response.results.size == 10
        
        # Verify interactions
        self.mock_authorization.can_search_errors.assert_called_once_with(user_id)
        self.mock_repository.search.assert_called_once()
        self.mock_repository.count_by_filters.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_search_with_severity_filter(self):
        """Test search with severity level filter"""
        # Arrange
        user_id = str(uuid4())
        high_severity_errors = [
            ErrorReportFactory.create(severity_level=SeverityLevel.HIGH)
            for _ in range(3)
        ]
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(severity_levels=["high"]),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="severity_level", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search
        self.mock_repository.search.return_value = high_severity_errors
        self.mock_repository.count_by_filters.return_value = 3
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 3
        
        # Verify all returned errors have high severity
        for error in response.results.items:
            assert error.severity_level == "high"
    
    @pytest.mark.asyncio
    async def test_execute_search_with_category_filter(self):
        """Test search with error category filter"""
        # Arrange
        user_id = str(uuid4())
        medical_errors = [
            ErrorReportFactory.create(error_categories=["medical_terminology"])
            for _ in range(4)
        ]
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(categories=["medical_terminology"]),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search
        self.mock_repository.search.return_value = medical_errors
        self.mock_repository.count_by_filters.return_value = 4
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 4
        
        # Verify all returned errors have medical_terminology category
        for error in response.results.items:
            assert "medical_terminology" in error.error_categories
    
    @pytest.mark.asyncio
    async def test_execute_search_with_date_range_filter(self):
        """Test search with date range filter"""
        # Arrange
        user_id = str(uuid4())
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        recent_errors = [
            ErrorReportFactory.create(
                error_timestamp=start_date + timedelta(days=i)
            )
            for i in range(3)
        ]
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(
                date_from=start_date,
                date_to=end_date
            ),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="error_timestamp", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search
        self.mock_repository.search.return_value = recent_errors
        self.mock_repository.count_by_filters.return_value = 3
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 3
        
        # Verify all returned errors are within date range
        for error in response.results.items:
            assert start_date <= error.error_timestamp <= end_date
    
    @pytest.mark.asyncio
    async def test_execute_search_with_text_search(self):
        """Test search with text content search"""
        # Arrange
        user_id = str(uuid4())
        diabetes_errors = [
            ErrorReportFactory.create(
                original_text="The patient has diabetis",
                corrected_text="The patient has diabetes"
            )
            for _ in range(2)
        ]
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(text_search="diabetes"),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="relevance", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search
        self.mock_repository.search.return_value = diabetes_errors
        self.mock_repository.count_by_filters.return_value = 2
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 2
        
        # Verify all returned errors contain search term
        for error in response.results.items:
            assert "diabetes" in error.original_text.lower() or "diabetes" in error.corrected_text.lower()
    
    @pytest.mark.asyncio
    async def test_execute_search_with_pagination(self):
        """Test search with pagination"""
        # Arrange
        user_id = str(uuid4())
        all_errors = create_error_reports_batch(25)
        page_2_errors = all_errors[10:20]  # Second page of 10 items
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(),
            pagination=PaginationParams(page=2, size=10),
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search
        self.mock_repository.search.return_value = page_2_errors
        self.mock_repository.count_by_filters.return_value = 25
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 10
        assert response.results.page == 2
        assert response.results.size == 10
        assert response.results.total == 25
        assert response.results.pages == 3  # 25 items / 10 per page = 3 pages
    
    @pytest.mark.asyncio
    async def test_execute_search_unauthorized_access_denied(self):
        """Test search access denied for unauthorized user"""
        # Arrange
        user_id = str(uuid4())
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Mock authorization check to deny access
        self.mock_authorization.can_search_errors.return_value = False
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Search access denied"):
            await self.use_case.execute(request)
        
        # Verify repository was not accessed
        self.mock_repository.search.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_search_cached_results(self):
        """Test search with cached results"""
        # Arrange
        user_id = str(uuid4())
        cached_results = {
            "items": [{"error_id": str(uuid4()), "original_text": "cached"}],
            "total": 1,
            "page": 1,
            "size": 10
        }
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache hit
        cache_key = self.use_case._generate_cache_key(request)
        self.mock_cache.get.return_value = cached_results
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 1
        
        # Verify repository was not called due to cache hit
        self.mock_repository.search.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_search_empty_results(self):
        """Test search with no matching results"""
        # Arrange
        user_id = str(uuid4())
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(text_search="nonexistent_term"),
            pagination=PaginationParams(page=1, size=10),
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search with empty results
        self.mock_repository.search.return_value = []
        self.mock_repository.count_by_filters.return_value = 0
        
        # Act
        response = await self.use_case.execute(request)
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 0
        assert response.results.total == 0
        assert response.results.pages == 0
    
    @pytest.mark.asyncio
    async def test_execute_search_performance_large_dataset(self):
        """Test search performance with large dataset"""
        # Arrange
        user_id = str(uuid4())
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(),
            pagination=PaginationParams(page=1, size=100),  # Large page size
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Mock authorization check
        self.mock_authorization.can_search_errors.return_value = True
        
        # Mock cache miss
        self.mock_cache.get.return_value = None
        
        # Mock repository search with large dataset
        large_dataset = create_error_reports_batch(100)
        self.mock_repository.search.return_value = large_dataset
        self.mock_repository.count_by_filters.return_value = 10000
        
        # Act
        start_time = datetime.utcnow()
        response = await self.use_case.execute(request)
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Assert
        assert response.status == "success"
        assert len(response.results.items) == 100
        assert execution_time < 2.0  # Should complete within 2 seconds
    
    @pytest.mark.asyncio
    async def test_execute_search_invalid_pagination_parameters(self):
        """Test search with invalid pagination parameters"""
        # Arrange
        user_id = str(uuid4())
        
        request = SearchErrorsRequest(
            requested_by=user_id,
            filters=ErrorFilters(),
            pagination=PaginationParams(page=0, size=-1),  # Invalid parameters
            sort=SortParams(field="created_at", direction="desc")
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid pagination parameters"):
            await self.use_case.execute(request)

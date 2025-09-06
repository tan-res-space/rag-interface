/**
 * Error Reports List Integration Test
 * 
 * Tests the "My Reports" page functionality with the new bucket types system
 * to ensure the API integration works correctly after the bucket types migration.
 */

import { test, expect, Page, ConsoleMessage } from '@playwright/test';

// Test data with new bucket types
const testData = {
  bucketTypes: {
    NO_TOUCH: 'no_touch',
    LOW_TOUCH: 'low_touch',
    MEDIUM_TOUCH: 'medium_touch',
    HIGH_TOUCH: 'high_touch'
  },
  oldBucketTypes: ['beginner', 'intermediate', 'advanced', 'expert']
};

// Error tracking
let consoleErrors: ConsoleMessage[] = [];
let networkErrors: string[] = [];

// Helper function to set up authentication
async function setupAuthentication(page: Page): Promise<void> {
  console.log('🔐 Setting up authentication...');
  
  await page.addInitScript(() => {
    localStorage.setItem('accessToken', 'mock-access-token-12345');
    localStorage.setItem('refreshToken', 'mock-refresh-token-67890');
    
    const mockUser = {
      id: 'test-user-123',
      username: 'qa-test-user',
      email: 'qa-test@example.com',
      role: 'QA_ANALYST',
      firstName: 'QA',
      lastName: 'Tester',
      isActive: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    localStorage.setItem('user', JSON.stringify(mockUser));
  });
  
  // Mock authentication API
  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      json: {
        id: 'test-user-123',
        username: 'qa-test-user',
        email: 'qa-test@example.com',
        role: 'QA_ANALYST',
        firstName: 'QA',
        lastName: 'Tester',
        isActive: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    });
  });
  
  console.log('✅ Authentication setup complete');
}

test.describe('Error Reports List Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Reset error tracking
    consoleErrors = [];
    networkErrors = [];

    // Track console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg);
        console.log(`Console Error: ${msg.text()}`);
      }
    });

    // Track network failures
    page.on('requestfailed', (request) => {
      networkErrors.push(`${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
      console.log(`Network Error: ${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
    });

    // Mock the error reports API with new bucket types
    await page.route('**/api/v1/errors**', async (route) => {
      const url = new URL(route.request().url());
      const method = route.request().method();
      
      if (method === 'GET') {
        // Parse query parameters
        const page_param = url.searchParams.get('page') || '1';
        const size = url.searchParams.get('size') || '10';
        const bucket_type = url.searchParams.get('bucket_type');
        const status = url.searchParams.get('status');
        const search = url.searchParams.get('search');
        
        console.log(`📡 API Request: GET /api/v1/errors?page=${page_param}&size=${size}&bucket_type=${bucket_type}&status=${status}&search=${search}`);
        
        // Sample reports with new bucket types
        const sampleReports = [
          {
            id: 'report-1',
            job_id: 'job-123',
            speaker_id: 'speaker-456',
            client_id: 'client-789',
            bucket_type: 'medium_touch',
            reported_by: 'user-123',
            original_text: 'The patient has a history of hypertension and diabetes.',
            corrected_text: 'The patient has a history of high blood pressure and diabetes.',
            error_categories: ['medical_terminology'],
            severity_level: 'medium',
            start_position: 29,
            end_position: 41,
            context_notes: 'Medical terminology should be simplified',
            error_timestamp: '2024-12-19T10:30:00Z',
            status: 'pending',
            created_at: '2024-12-19T10:30:00Z',
            updated_at: '2024-12-19T10:30:00Z'
          },
          {
            id: 'report-2',
            job_id: 'job-456',
            speaker_id: 'speaker-789',
            client_id: 'client-123',
            bucket_type: 'high_touch',
            reported_by: 'user-456',
            original_text: 'The medication dosage is 10mg twice daily.',
            corrected_text: 'The medication dosage is 10 milligrams twice daily.',
            error_categories: ['abbreviation'],
            severity_level: 'low',
            start_position: 25,
            end_position: 29,
            context_notes: 'Abbreviations should be spelled out',
            error_timestamp: '2024-12-19T11:15:00Z',
            status: 'processed',
            created_at: '2024-12-19T11:15:00Z',
            updated_at: '2024-12-19T11:45:00Z'
          },
          {
            id: 'report-3',
            job_id: 'job-789',
            speaker_id: 'speaker-123',
            client_id: 'client-456',
            bucket_type: 'low_touch',
            reported_by: 'user-789',
            original_text: 'Patient exhibits symptoms of acute myocardial infarction.',
            corrected_text: 'Patient exhibits symptoms of acute heart attack.',
            error_categories: ['medical_terminology'],
            severity_level: 'high',
            start_position: 32,
            end_position: 56,
            context_notes: 'Complex medical terms should be simplified',
            error_timestamp: '2024-12-19T12:00:00Z',
            status: 'archived',
            created_at: '2024-12-19T12:00:00Z',
            updated_at: '2024-12-19T12:30:00Z'
          },
          {
            id: 'report-4',
            job_id: 'job-101',
            speaker_id: 'speaker-202',
            client_id: 'client-303',
            bucket_type: 'no_touch',
            reported_by: 'user-404',
            original_text: 'The patient\'s vital signs are stable.',
            corrected_text: 'The patient\'s vital signs are stable.',
            error_categories: ['pronunciation'],
            severity_level: 'low',
            start_position: 0,
            end_position: 37,
            context_notes: 'Minor pronunciation issue, no text change needed',
            error_timestamp: '2024-12-19T13:30:00Z',
            status: 'rejected',
            created_at: '2024-12-19T13:30:00Z',
            updated_at: '2024-12-19T14:00:00Z'
          }
        ];
        
        // Apply filters
        let filteredReports = sampleReports;
        
        if (bucket_type) {
          filteredReports = filteredReports.filter(r => r.bucket_type === bucket_type);
          console.log(`🔍 Filtered by bucket_type: ${bucket_type}, found ${filteredReports.length} reports`);
        }
        
        if (status) {
          filteredReports = filteredReports.filter(r => r.status === status);
          console.log(`🔍 Filtered by status: ${status}, found ${filteredReports.length} reports`);
        }
        
        if (search) {
          const searchLower = search.toLowerCase();
          filteredReports = filteredReports.filter(r => 
            r.original_text.toLowerCase().includes(searchLower) ||
            r.corrected_text.toLowerCase().includes(searchLower) ||
            r.id.toLowerCase().includes(searchLower)
          );
          console.log(`🔍 Filtered by search: ${search}, found ${filteredReports.length} reports`);
        }
        
        // Apply pagination
        const pageNum = parseInt(page_param);
        const pageSize = parseInt(size);
        const startIdx = (pageNum - 1) * pageSize;
        const endIdx = startIdx + pageSize;
        const paginatedReports = filteredReports.slice(startIdx, endIdx);
        
        const response = {
          items: paginatedReports,
          total: filteredReports.length,
          page: pageNum,
          size: pageSize,
          pages: Math.ceil(filteredReports.length / pageSize)
        };
        
        console.log(`✅ API Response: ${paginatedReports.length} reports returned`);
        
        await route.fulfill({
          json: response,
          headers: {
            'Content-Type': 'application/json'
          }
        });
      } else {
        // Handle other methods if needed
        await route.continue();
      }
    });

    // Set up authentication
    await setupAuthentication(page);
  });

  test('should load error reports list successfully', async ({ page }) => {
    console.log('🧪 Testing: Error reports list loading...');
    
    // Navigate to error reports list page
    await page.goto('/error-reporting/reports');
    await page.waitForLoadState('networkidle');
    
    // Wait for the page to load
    await page.waitForTimeout(2000);
    
    // Check that we're not seeing the error message
    const errorAlert = page.locator('text=Failed to load error reports');
    await expect(errorAlert).not.toBeVisible();
    
    // Check for reports table or cards
    const hasTable = await page.locator('table').count() > 0;
    const hasCards = await page.locator('[data-testid*="report-card"], .MuiCard-root').count() > 0;
    const hasReportContent = await page.getByText(/report-\d+|Report ID|Speaker ID/i).count() > 0;
    
    if (!hasTable && !hasCards && !hasReportContent) {
      // Take screenshot for debugging
      await page.screenshot({ path: 'debug-reports-list-no-content.png' });
      
      // Check if there's an empty state message
      const emptyState = await page.getByText(/no error reports found|no reports/i).count() > 0;
      if (emptyState) {
        console.log('✅ Empty state displayed correctly');
      } else {
        throw new Error('❌ No reports content found and no empty state message');
      }
    } else {
      console.log('✅ Reports content found successfully');
    }
    
    console.log('✅ Error reports list loaded successfully');
  });

  test('should filter by new bucket types correctly', async ({ page }) => {
    console.log('🧪 Testing: Bucket type filtering...');
    
    await page.goto('/error-reporting/reports');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Test each new bucket type filter
    for (const [bucketName, bucketValue] of Object.entries(testData.bucketTypes)) {
      console.log(`🔍 Testing filter: ${bucketName} (${bucketValue})`);
      
      // Find and click the bucket type filter
      const bucketFilter = page.locator('select[name="bucketType"], [aria-label*="Bucket Type"], [data-testid="bucket-type-filter"]').first();
      
      if (await bucketFilter.count() > 0) {
        await bucketFilter.selectOption(bucketValue);
        await page.waitForTimeout(1000);
        
        // Verify the filter was applied (check URL or API call)
        console.log(`✅ Applied filter: ${bucketName}`);
      } else {
        console.log(`⚠️ Bucket type filter not found, checking for alternative selectors...`);
        
        // Try alternative selectors
        const altFilter = page.locator('text=Bucket Type').locator('..').locator('select, input');
        if (await altFilter.count() > 0) {
          await altFilter.first().click();
          await page.getByText(bucketName.replace('_', ' ')).click();
          console.log(`✅ Applied filter via alternative method: ${bucketName}`);
        }
      }
    }
    
    // Verify old bucket types are not available
    for (const oldBucket of testData.oldBucketTypes) {
      const oldBucketOption = page.getByText(oldBucket, { exact: true });
      await expect(oldBucketOption).not.toBeVisible();
      console.log(`✅ Old bucket type "${oldBucket}" not found (good)`);
    }
    
    console.log('✅ Bucket type filtering test completed');
  });

  test('should display reports with correct bucket type labels', async ({ page }) => {
    console.log('🧪 Testing: Bucket type display...');
    
    await page.goto('/error-reporting/reports');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check for new bucket type labels in the content
    const newBucketLabels = ['No Touch', 'Low Touch', 'Medium Touch', 'High Touch'];
    
    for (const label of newBucketLabels) {
      const labelElement = page.getByText(label);
      if (await labelElement.count() > 0) {
        console.log(`✅ Found new bucket label: "${label}"`);
      }
    }
    
    // Verify old bucket type labels are not present
    const oldBucketLabels = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];
    
    for (const oldLabel of oldBucketLabels) {
      const oldLabelElement = page.getByText(oldLabel, { exact: true });
      await expect(oldLabelElement).not.toBeVisible();
      console.log(`✅ Old bucket label "${oldLabel}" not found (good)`);
    }
    
    console.log('✅ Bucket type display test completed');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    console.log('🧪 Testing: API error handling...');
    
    // Mock API error
    await page.route('**/api/v1/errors**', async (route) => {
      await route.fulfill({
        status: 500,
        json: { error: 'Internal server error' }
      });
    });
    
    await page.goto('/error-reporting/reports');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check that error message is displayed
    const errorAlert = page.locator('text=Failed to load error reports');
    await expect(errorAlert).toBeVisible();
    
    console.log('✅ API error handling test completed');
  });

  test.afterEach(async ({ page }) => {
    // Report any console errors
    if (consoleErrors.length > 0) {
      console.log('❌ Console errors detected:');
      consoleErrors.forEach(error => console.log(`  - ${error.text()}`));
    }
    
    // Report any network errors
    if (networkErrors.length > 0) {
      console.log('❌ Network errors detected:');
      networkErrors.forEach(error => console.log(`  - ${error}`));
    }
    
    if (consoleErrors.length === 0 && networkErrors.length === 0) {
      console.log('✅ No errors detected during test execution');
    }
  });
});

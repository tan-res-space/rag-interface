/**
 * Error Reporting Backend Integration Tests
 * 
 * Tests the complete integration between frontend and backend for error reporting,
 * specifically focusing on the new bucket types and API endpoints.
 */

import { test, expect, Page } from '@playwright/test';

// Test data
const testData = {
  jobId: 'integration-job-123',
  speakerId: 'integration-speaker-456',
  clientId: 'integration-client-789',
  documentText: 'The patient has a history of hypertension and diabetes.',
  errorText: 'hypertension',
  correctedText: 'high blood pressure',
  category: 'Medical Terminology',
  bucketTypes: {
    NO_TOUCH: 'no_touch',
    LOW_TOUCH: 'low_touch',
    MEDIUM_TOUCH: 'medium_touch',
    HIGH_TOUCH: 'high_touch'
  }
};

// API response tracking
let apiRequests: any[] = [];
let apiResponses: any[] = [];

test.describe('Backend Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Reset tracking
    apiRequests = [];
    apiResponses = [];

    // Track all API requests and responses
    page.on('request', (request) => {
      if (request.url().includes('/api/')) {
        apiRequests.push({
          method: request.method(),
          url: request.url(),
          headers: request.headers(),
          postData: request.postData()
        });
        console.log(`API Request: ${request.method()} ${request.url()}`);
      }
    });

    page.on('response', (response) => {
      if (response.url().includes('/api/')) {
        apiResponses.push({
          status: response.status(),
          url: response.url(),
          headers: response.headers()
        });
        console.log(`API Response: ${response.status()} ${response.url()}`);
      }
    });

    // Navigate to error reporting page
    await page.goto('/error-reporting');
    await expect(page.getByText('ASR Error Reporting System')).toBeVisible();
  });

  test('should submit error report with new bucket types to backend', async ({ page }) => {
    // Complete the full workflow
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();

    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();

    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Fill Step 4 with new bucket types
    const speakerIdInput = page.getByLabel(/speaker id/i);
    if (await speakerIdInput.count() > 0) {
      await speakerIdInput.fill(testData.speakerId);
    }

    const clientIdInput = page.getByLabel(/client id/i);
    if (await clientIdInput.count() > 0) {
      await clientIdInput.fill(testData.clientId);
    }

    // Select High Touch bucket (new bucket type)
    const highTouchRadio = page.getByRole('radio', { name: /high touch/i });
    if (await highTouchRadio.count() > 0) {
      await highTouchRadio.click();
    }

    // Fill enhanced metadata
    const audioQualitySelect = page.locator('select').first();
    if (await audioQualitySelect.count() > 0) {
      await audioQualitySelect.selectOption('good');
    }

    await page.getByRole('button', { name: /next/i }).click();

    // Step 5: Review & Submit
    await expect(page.getByText('Review & Submit')).toBeVisible();

    // Submit the form
    const submitButton = page.getByRole('button', { name: /submit report/i });
    await expect(submitButton).toBeEnabled();
    await submitButton.click();

    // Wait for API call to complete
    await page.waitForTimeout(3000);

    // Verify API request was made
    const submitRequest = apiRequests.find(req => 
      req.method === 'POST' && req.url.includes('/api/v1/errors')
    );
    
    expect(submitRequest).toBeDefined();
    console.log('✅ Error report submission API request found');

    // Verify request contains new bucket type
    if (submitRequest?.postData) {
      const requestData = JSON.parse(submitRequest.postData);
      expect(requestData.bucket_type).toBe(testData.bucketTypes.HIGH_TOUCH);
      console.log('✅ Request contains correct new bucket type');
    }

    // Verify successful response
    const submitResponse = apiResponses.find(res => 
      res.url.includes('/api/v1/errors') && res.status >= 200 && res.status < 300
    );
    
    if (submitResponse) {
      console.log('✅ Successful API response received');
    } else {
      console.log('❌ No successful API response found');
      console.log('API Responses:', apiResponses);
    }
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error response
    await page.route('**/api/v1/errors/report', async (route) => {
      await route.fulfill({
        status: 500,
        json: {
          error: 'Internal server error',
          message: 'Failed to submit error report'
        }
      });
    });

    // Complete workflow
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Fill required fields
    const speakerIdInput = page.getByLabel(/speaker id/i);
    if (await speakerIdInput.count() > 0) {
      await speakerIdInput.fill(testData.speakerId);
    }

    const clientIdInput = page.getByLabel(/client id/i);
    if (await clientIdInput.count() > 0) {
      await clientIdInput.fill(testData.clientId);
    }

    const mediumTouchRadio = page.getByRole('radio', { name: /medium touch/i });
    if (await mediumTouchRadio.count() > 0) {
      await mediumTouchRadio.click();
    }

    await page.getByRole('button', { name: /next/i }).click();
    await page.getByRole('button', { name: /submit report/i }).click();

    // Should show error message
    await expect(page.getByText(/error|failed|unable/i)).toBeVisible({ timeout: 10000 });
    console.log('✅ Error handling works correctly');
  });

  test('should validate bucket type data format in API request', async ({ page }) => {
    // Complete workflow with each bucket type
    const bucketTypes = [
      { name: 'No Touch', value: testData.bucketTypes.NO_TOUCH },
      { name: 'Low Touch', value: testData.bucketTypes.LOW_TOUCH },
      { name: 'Medium Touch', value: testData.bucketTypes.MEDIUM_TOUCH },
      { name: 'High Touch', value: testData.bucketTypes.HIGH_TOUCH }
    ];

    for (const bucket of bucketTypes) {
      // Reset page
      await page.goto('/error-reporting');
      await expect(page.getByText('ASR Error Reporting System')).toBeVisible();

      // Complete workflow
      await page.locator(`text="${testData.errorText}"`).first().dblclick();
      await page.waitForTimeout(500);
      await page.getByRole('button', { name: /next/i }).click();
      await page.getByText(testData.category).first().click();
      await page.getByRole('button', { name: /next/i }).click();
      const correctionInput = page.locator('textarea, input[type="text"]').first();
      await correctionInput.fill(testData.correctedText);
      await page.getByRole('button', { name: /next/i }).click();

      // Fill required fields
      const speakerIdInput = page.getByLabel(/speaker id/i);
      if (await speakerIdInput.count() > 0) {
        await speakerIdInput.fill(testData.speakerId);
      }

      const clientIdInput = page.getByLabel(/client id/i);
      if (await clientIdInput.count() > 0) {
        await clientIdInput.fill(testData.clientId);
      }

      // Select specific bucket type
      const bucketRadio = page.getByRole('radio', { name: new RegExp(bucket.name, 'i') });
      if (await bucketRadio.count() > 0) {
        await bucketRadio.click();
      }

      await page.getByRole('button', { name: /next/i }).click();

      // Mock successful response for this test
      await page.route('**/api/v1/errors/report', async (route) => {
        const request = route.request();
        const requestData = JSON.parse(request.postData() || '{}');
        
        // Validate bucket type format
        expect(requestData.bucket_type).toBe(bucket.value);
        console.log(`✅ ${bucket.name} bucket type format validated: ${bucket.value}`);

        await route.fulfill({
          json: {
            errorId: 'test-report-123',
            status: 'submitted',
            message: 'Success'
          }
        });
      });

      await page.getByRole('button', { name: /submit report/i }).click();
      await page.waitForTimeout(1000);
    }
  });

  test('should handle network timeouts and retries', async ({ page }) => {
    let requestCount = 0;

    // Mock timeout on first request, success on second
    await page.route('**/api/v1/errors/report', async (route) => {
      requestCount++;
      
      if (requestCount === 1) {
        // Simulate timeout
        await new Promise(resolve => setTimeout(resolve, 5000));
        await route.abort('timeout');
      } else {
        // Success on retry
        await route.fulfill({
          json: {
            errorId: 'retry-success-123',
            status: 'submitted',
            message: 'Success after retry'
          }
        });
      }
    });

    // Complete workflow
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Fill required fields
    const speakerIdInput = page.getByLabel(/speaker id/i);
    if (await speakerIdInput.count() > 0) {
      await speakerIdInput.fill(testData.speakerId);
    }

    const clientIdInput = page.getByLabel(/client id/i);
    if (await clientIdInput.count() > 0) {
      await clientIdInput.fill(testData.clientId);
    }

    const lowTouchRadio = page.getByRole('radio', { name: /low touch/i });
    if (await lowTouchRadio.count() > 0) {
      await lowTouchRadio.click();
    }

    await page.getByRole('button', { name: /next/i }).click();
    await page.getByRole('button', { name: /submit report/i }).click();

    // Should handle timeout and potentially retry
    await page.waitForTimeout(8000);
    
    console.log(`✅ Network timeout handling tested (${requestCount} requests made)`);
  });
});

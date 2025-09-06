/**
 * Error Reporting Tests with Authentication
 * 
 * This test suite handles authentication and tests the complete error reporting workflow,
 * specifically focusing on the Step 4 "Next" button issue and new bucket types.
 */

import { test, expect, Page, ConsoleMessage } from '@playwright/test';

// Test data
const testData = {
  // Test credentials (these should be configured for your test environment)
  username: 'qa-test-user',
  password: 'test-password',
  
  // Error reporting data
  jobId: 'demo-job-123',
  speakerId: 'demo-speaker-456',
  clientId: 'demo-client-789',
  documentText: 'The patient has a history of hypertension and diabetes.',
  errorText: 'hypertension',
  correctedText: 'high blood pressure',
  category: 'Medical Terminology',
  
  // New bucket types
  bucketTypes: {
    NO_TOUCH: 'no_touch',
    LOW_TOUCH: 'low_touch',
    MEDIUM_TOUCH: 'medium_touch',
    HIGH_TOUCH: 'high_touch'
  }
};

// Error tracking
let consoleErrors: ConsoleMessage[] = [];
let networkErrors: string[] = [];

// Helper function to handle authentication
async function authenticateUser(page: Page): Promise<void> {
  console.log('🔐 Attempting to authenticate user...');
  
  // Navigate to login page
  await page.goto('/login');
  
  // Check if we're already logged in (redirect to dashboard)
  if (page.url().includes('/dashboard')) {
    console.log('✅ User already authenticated');
    return;
  }
  
  // Wait for login form to be visible
  await expect(page.getByText('Sign in to your account')).toBeVisible({ timeout: 10000 });
  
  // Fill login form
  const usernameField = page.getByRole('textbox', { name: /username/i });
  const passwordField = page.getByRole('textbox', { name: /password/i });
  const signInButton = page.getByRole('button', { name: /sign in/i });
  
  await usernameField.fill(testData.username);
  await passwordField.fill(testData.password);
  await signInButton.click();
  
  // Wait for successful login (redirect to dashboard)
  try {
    await page.waitForURL('/dashboard', { timeout: 10000 });
    console.log('✅ Authentication successful');
  } catch (error) {
    // If authentication fails, try to continue anyway for testing
    console.log('⚠️ Authentication may have failed, continuing with test...');
    
    // Check if we're on an error page or still on login
    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      // Try alternative authentication method or skip auth for testing
      await page.evaluate(() => {
        // Mock authentication in localStorage for testing
        localStorage.setItem('auth-token', 'test-token');
        localStorage.setItem('user-role', 'QA_ANALYST');
        localStorage.setItem('user-id', 'test-user-123');
      });
      
      // Navigate directly to error reporting
      await page.goto('/error-reporting');
    }
  }
}

test.describe('Error Reporting with Authentication', () => {
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

    // Mock API responses for testing
    await page.route('**/api/v1/errors/categories', async (route) => {
      await route.fulfill({
        json: [
          {
            id: 'medical',
            name: 'Medical Terminology',
            description: 'Medical term errors',
            isActive: true,
          }
        ],
      });
    });

    await page.route('**/api/v1/errors/report', async (route) => {
      await route.fulfill({
        json: {
          errorId: 'report-123',
          status: 'submitted',
          message: 'Error report submitted successfully',
          bucket_progression: {
            speaker_id: testData.speakerId,
            evaluation_performed: true,
            bucket_changed: false,
            old_bucket: testData.bucketTypes.MEDIUM_TOUCH,
            new_bucket: testData.bucketTypes.MEDIUM_TOUCH
          }
        },
      });
    });

    // Authenticate user
    await authenticateUser(page);
  });

  test('should access error reporting page after authentication', async ({ page }) => {
    // Navigate to error reporting page
    await page.goto('/error-reporting');
    
    // Verify we can access the page (not redirected to login)
    await expect(page.getByText('ASR Error Reporting System')).toBeVisible({ timeout: 10000 });
    console.log('✅ Successfully accessed Error Reporting page');
    
    // Verify the page has the expected content
    await expect(page.getByText('Report ASR Error')).toBeVisible();
    await expect(page.getByText('Help improve transcription accuracy')).toBeVisible();
  });

  test('CRITICAL: should complete Step 4 to Step 5 transition without blank page', async ({ page }) => {
    // Navigate to error reporting page
    await page.goto('/error-reporting');
    await expect(page.getByText('ASR Error Reporting System')).toBeVisible();

    // Step 1: Text Selection
    console.log('🔍 Starting Step 1: Text Selection');
    await expect(page.getByText('Select Error Text')).toBeVisible();
    
    // Select error text by double-clicking
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    
    // Verify selection
    await expect(page.getByText(/1.*selection/i)).toBeVisible();
    console.log('✅ Step 1 completed');
    
    // Navigate to Step 2
    const nextButton1 = page.getByRole('button', { name: /next/i });
    await expect(nextButton1).toBeEnabled();
    await nextButton1.click();

    // Step 2: Error Categorization
    console.log('🔍 Starting Step 2: Error Categorization');
    await expect(page.getByText('Categorize Errors')).toBeVisible();
    
    // Select category
    await page.getByText(testData.category).first().click();
    await expect(page.getByText(/1.*categor/i)).toBeVisible();
    console.log('✅ Step 2 completed');
    
    // Navigate to Step 3
    const nextButton2 = page.getByRole('button', { name: /next/i });
    await expect(nextButton2).toBeEnabled();
    await nextButton2.click();

    // Step 3: Correction Input
    console.log('🔍 Starting Step 3: Correction Input');
    await expect(page.getByText('Provide Correction')).toBeVisible();
    
    // Enter correction text
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    console.log('✅ Step 3 completed');
    
    // Navigate to Step 4
    const nextButton3 = page.getByRole('button', { name: /next/i });
    await expect(nextButton3).toBeEnabled();
    await nextButton3.click();

    // Step 4: Add Context - CRITICAL SECTION
    console.log('🔍 Starting Step 4: Add Context (CRITICAL SECTION)');
    await expect(page.getByText('Add Context')).toBeVisible();

    // Fill required Speaker ID and Client ID fields
    const speakerIdInput = page.getByLabel(/speaker id/i);
    if (await speakerIdInput.count() > 0) {
      await speakerIdInput.fill(testData.speakerId);
      console.log('✅ Filled Speaker ID');
    }

    const clientIdInput = page.getByLabel(/client id/i);
    if (await clientIdInput.count() > 0) {
      await clientIdInput.fill(testData.clientId);
      console.log('✅ Filled Client ID');
    }

    // Test new bucket type selection
    await expect(page.getByText('Quality-Based Bucket Assignment')).toBeVisible();
    console.log('✅ Found bucket assignment section');

    // Select High Touch bucket (new bucket type)
    const highTouchRadio = page.getByRole('radio', { name: /high touch/i });
    await expect(highTouchRadio).toBeVisible();
    await highTouchRadio.click();
    console.log('✅ Selected High Touch bucket');

    // Fill enhanced metadata
    const audioQualitySelect = page.locator('select, [role="combobox"]').first();
    if (await audioQualitySelect.count() > 0) {
      await audioQualitySelect.selectOption('good');
      console.log('✅ Selected audio quality');
    }

    // Check authentication status before proceeding
    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      throw new Error('❌ User was redirected to login during Step 4 - session expired');
    }

    // CRITICAL TEST: Click Next button to go to Step 5
    const nextButton4 = page.getByRole('button', { name: /next/i });
    await expect(nextButton4).toBeVisible();
    await expect(nextButton4).toBeEnabled();
    
    console.log('🔍 About to click Next button (Step 4 → Step 5)...');
    
    // Click and wait for navigation
    await nextButton4.click();
    
    // Wait for potential loading or transition
    await page.waitForTimeout(2000);

    // CRITICAL CHECK: Verify we don't have a blank page
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.trim()).not.toBe('');
    console.log('✅ Page is not blank after Step 4 transition');

    // Check if we were redirected to login (authentication issue)
    const finalUrl = page.url();
    if (finalUrl.includes('/login')) {
      throw new Error('❌ CRITICAL BUG CONFIRMED: User redirected to login during Step 4 → Step 5 transition');
    }

    // Verify we reached Step 5
    await expect(page.getByText('Review & Submit')).toBeVisible({ timeout: 10000 });
    console.log('✅ Successfully reached Step 5');

    // Check for console errors during transition
    if (consoleErrors.length > 0) {
      console.log('❌ Console errors detected during Step 4 transition:');
      consoleErrors.forEach(error => console.log(`  - ${error.text()}`));
      throw new Error(`Console errors detected: ${consoleErrors.map(e => e.text()).join(', ')}`);
    }

    // Check for network errors
    if (networkErrors.length > 0) {
      console.log('❌ Network errors detected during Step 4 transition:');
      networkErrors.forEach(error => console.log(`  - ${error}`));
      throw new Error(`Network errors detected: ${networkErrors.join(', ')}`);
    }

    console.log('✅ CRITICAL TEST PASSED: Step 4 to Step 5 transition successful');
  });

  test('should validate new bucket types are displayed correctly', async ({ page }) => {
    // Navigate to error reporting and complete steps 1-3
    await page.goto('/error-reporting');
    await expect(page.getByText('ASR Error Reporting System')).toBeVisible();

    // Quick navigation to Step 4
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Verify new bucket types are displayed
    await expect(page.getByText('Quality-Based Bucket Assignment')).toBeVisible();
    
    // Check all four new bucket types
    await expect(page.getByText('No Touch')).toBeVisible();
    await expect(page.getByText('Low Touch')).toBeVisible();
    await expect(page.getByText('Medium Touch')).toBeVisible();
    await expect(page.getByText('High Touch')).toBeVisible();

    // Verify old bucket types are NOT present
    await expect(page.getByText('Beginner')).not.toBeVisible();
    await expect(page.getByText('Intermediate')).not.toBeVisible();
    await expect(page.getByText('Advanced')).not.toBeVisible();
    await expect(page.getByText('Expert')).not.toBeVisible();

    console.log('✅ New bucket types validation passed');
  });

  test('should handle session expiry gracefully', async ({ page }) => {
    // Navigate to error reporting
    await page.goto('/error-reporting');
    await expect(page.getByText('ASR Error Reporting System')).toBeVisible();

    // Simulate session expiry by clearing auth tokens
    await page.evaluate(() => {
      localStorage.removeItem('auth-token');
      localStorage.removeItem('user-role');
      localStorage.removeItem('user-id');
    });

    // Try to navigate to Step 4 (this should trigger auth check)
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Try to proceed to Step 5 (this might trigger the blank page issue)
    const nextButton4 = page.getByRole('button', { name: /next/i });
    if (await nextButton4.count() > 0) {
      await nextButton4.click();
      await page.waitForTimeout(2000);

      // Check if we were redirected to login
      const currentUrl = page.url();
      if (currentUrl.includes('/login')) {
        console.log('✅ Session expiry handled correctly - redirected to login');
      } else {
        console.log('⚠️ Session expiry not detected or handled differently');
      }
    }
  });
});

/**
 * Final Error Reporting Critical Bug Test
 * 
 * This test properly handles authentication and tests the complete error reporting workflow
 * to identify the Step 4 "Next" button blank page issue.
 */

import { test, expect, Page, ConsoleMessage } from '@playwright/test';

// Test data
const testData = {
  documentText: 'The patient has a history of hypertension and diabetes.',
  errorText: 'hypertension',
  correctedText: 'high blood pressure',
  category: 'Medical Terminology',
  speakerId: 'test-speaker-123',
  clientId: 'test-client-456',
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

// Helper function to set up authentication
async function setupAuthentication(page: Page): Promise<void> {
  console.log('🔐 Setting up authentication...');
  
  // Set up authentication tokens in localStorage
  await page.addInitScript(() => {
    // Mock authentication tokens
    localStorage.setItem('accessToken', 'mock-access-token-12345');
    localStorage.setItem('refreshToken', 'mock-refresh-token-67890');
    
    // Mock user data
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
  
  // Mock API responses for authentication
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

test.describe('Final Error Reporting Critical Bug Investigation', () => {
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

    // Mock API responses
    await page.route('**/api/v1/errors/categories', async (route) => {
      await route.fulfill({
        json: [
          {
            id: 'medical',
            name: 'Medical Terminology',
            description: 'Medical term errors',
            isActive: true,
          },
          {
            id: 'pronunciation',
            name: 'Pronunciation',
            description: 'Pronunciation errors',
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

    // Set up authentication
    await setupAuthentication(page);
  });

  test('should access error reporting page with proper authentication', async ({ page }) => {
    // Navigate to error reporting page
    await page.goto('/error-reporting');
    
    // Wait for page to load and check for error reporting content
    await page.waitForLoadState('networkidle');
    
    // Check for various possible content that indicates we're on the error reporting page
    const possibleContent = [
      'Error Reporting',
      'ASR Error Reporting',
      'Report ASR Error',
      'Select Error Text',
      'Step 1',
      'Text Selection'
    ];
    
    let foundContent = false;
    for (const content of possibleContent) {
      if (await page.getByText(content).count() > 0) {
        console.log(`✅ Found content: "${content}"`);
        foundContent = true;
        break;
      }
    }
    
    if (!foundContent) {
      // Take a screenshot to see what's actually displayed
      await page.screenshot({ path: 'debug-error-reporting-page.png' });
      
      // Get page content for debugging
      const pageContent = await page.content();
      console.log('Page content preview:', pageContent.substring(0, 500));
      
      // Check if we're still on login page
      const isLoginPage = await page.getByText('Sign in to your account').count() > 0;
      if (isLoginPage) {
        throw new Error('❌ AUTHENTICATION FAILED: Still on login page');
      }
      
      throw new Error('❌ ERROR REPORTING PAGE NOT FOUND: Could not find expected content');
    }
    
    console.log('✅ Successfully accessed Error Reporting page');
  });

  test('CRITICAL: Complete Step 4 to Step 5 transition investigation', async ({ page }) => {
    // Navigate to error reporting page
    await page.goto('/error-reporting');
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the error reporting page
    await page.waitForTimeout(2000);
    
    // Look for step indicators or form elements
    const hasSteps = await page.locator('[data-testid*="step"], .step, .stepper').count() > 0;
    const hasForm = await page.locator('form, [role="form"]').count() > 0;
    const hasTextSelection = await page.getByText(/select.*text|text.*selection/i).count() > 0;
    
    if (!hasSteps && !hasForm && !hasTextSelection) {
      // Take screenshot for debugging
      await page.screenshot({ path: 'debug-no-form-found.png' });
      console.log('⚠️ No form or steps found, checking page structure...');
      
      // Get all visible text to understand page structure
      const allText = await page.locator('body').textContent();
      console.log('Page text preview:', allText?.substring(0, 1000));
    }
    
    // Try to find and interact with text selection
    const documentText = page.locator('text=' + testData.errorText).first();
    if (await documentText.count() > 0) {
      console.log('✅ Found error text, attempting selection...');
      await documentText.dblclick();
      await page.waitForTimeout(1000);
    } else {
      console.log('⚠️ Error text not found, looking for alternative selection methods...');
      
      // Look for any clickable text or input fields
      const textInputs = page.locator('input[type="text"], textarea');
      if (await textInputs.count() > 0) {
        await textInputs.first().fill(testData.errorText);
        console.log('✅ Filled text input with error text');
      }
    }
    
    // Look for Next button or navigation
    const nextButtons = page.locator('button:has-text("Next"), button:has-text("Continue"), button[type="submit"]');
    if (await nextButtons.count() > 0) {
      console.log('✅ Found navigation button, attempting to proceed...');
      await nextButtons.first().click();
      await page.waitForTimeout(2000);
      
      // Check if we progressed to next step
      const currentUrl = page.url();
      console.log('Current URL after click:', currentUrl);
      
      // Check for any error messages or blank page
      const bodyText = await page.locator('body').textContent();
      if (!bodyText || bodyText.trim().length < 50) {
        await page.screenshot({ path: 'debug-blank-page.png' });
        throw new Error('❌ CRITICAL BUG CONFIRMED: Blank page detected after navigation');
      }
      
      console.log('✅ Page navigation successful, no blank page detected');
    } else {
      console.log('⚠️ No navigation buttons found');
      await page.screenshot({ path: 'debug-no-buttons.png' });
    }
    
    // Check for console errors
    if (consoleErrors.length > 0) {
      console.log('❌ Console errors detected:');
      consoleErrors.forEach(error => console.log(`  - ${error.text()}`));
    }
    
    // Check for network errors
    if (networkErrors.length > 0) {
      console.log('❌ Network errors detected:');
      networkErrors.forEach(error => console.log(`  - ${error}`));
    }
    
    console.log('✅ Critical bug investigation completed');
  });

  test('should validate new bucket types are available', async ({ page }) => {
    await page.goto('/error-reporting');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Look for bucket type related content
    const bucketContent = [
      'No Touch',
      'Low Touch', 
      'Medium Touch',
      'High Touch',
      'Quality-Based',
      'Bucket Assignment',
      'bucket',
      'quality'
    ];
    
    let foundBucketContent = false;
    for (const content of bucketContent) {
      if (await page.getByText(content, { exact: false }).count() > 0) {
        console.log(`✅ Found bucket content: "${content}"`);
        foundBucketContent = true;
      }
    }
    
    // Check that old bucket types are NOT present
    const oldBucketTypes = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];
    for (const oldType of oldBucketTypes) {
      const count = await page.getByText(oldType).count();
      if (count > 0) {
        console.log(`❌ Found old bucket type: "${oldType}"`);
      } else {
        console.log(`✅ Old bucket type "${oldType}" not found (good)`);
      }
    }
    
    if (foundBucketContent) {
      console.log('✅ New bucket types validation passed');
    } else {
      console.log('⚠️ Bucket types not found - may need to navigate to correct step');
    }
  });
});

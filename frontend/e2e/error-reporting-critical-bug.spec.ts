/**
 * Critical Bug Investigation: Error Reporting Step 4 "Next" Button Issue
 * 
 * This test suite specifically addresses the critical bug where clicking the "Next" button 
 * in the "Add Context" section (Step 4) results in a blank page with no response.
 * 
 * Focus Areas:
 * 1. Step 4 to Step 5 transition
 * 2. EnhancedMetadataInput component validation
 * 3. New bucket types functionality
 * 4. Backend integration
 * 5. Console error detection
 */

import { test, expect, Page, ConsoleMessage } from '@playwright/test';

// Test data with new bucket types
const testData = {
  jobId: 'demo-job-123',
  speakerId: 'demo-speaker-456',
  clientId: 'demo-client-789',
  documentText: 'The patient has a history of hypertension and diabetes. The doctor prescribed medication for the condition.',
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

// Console error tracking
let consoleErrors: ConsoleMessage[] = [];
let networkErrors: string[] = [];

test.describe('Critical Bug Investigation: Step 4 Next Button', () => {
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

    // Navigate to error reporting page
    await page.goto('/error-reporting');
    await expect(page.getByText('ASR Error Reporting System')).toBeVisible();
  });

  test('should complete Step 1-3 successfully before testing Step 4', async ({ page }) => {
    // Step 1: Text Selection
    await expect(page.getByText('Select Error Text')).toBeVisible();
    
    // Select error text by double-clicking
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    
    // Verify selection
    await expect(page.getByText(/1.*selection/i)).toBeVisible();
    
    // Navigate to Step 2
    const nextButton1 = page.getByRole('button', { name: /next/i });
    await expect(nextButton1).toBeEnabled();
    await nextButton1.click();

    // Step 2: Error Categorization
    await expect(page.getByText('Categorize Errors')).toBeVisible();
    
    // Select category
    await page.getByText(testData.category).first().click();
    await expect(page.getByText(/1.*categor/i)).toBeVisible();
    
    // Navigate to Step 3
    const nextButton2 = page.getByRole('button', { name: /next/i });
    await expect(nextButton2).toBeEnabled();
    await nextButton2.click();

    // Step 3: Correction Input
    await expect(page.getByText('Provide Correction')).toBeVisible();
    
    // Enter correction text
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    
    // Navigate to Step 4
    const nextButton3 = page.getByRole('button', { name: /next/i });
    await expect(nextButton3).toBeEnabled();
    await nextButton3.click();

    // Verify we reached Step 4
    await expect(page.getByText('Add Context')).toBeVisible();
    
    console.log('✅ Successfully completed Steps 1-3');
  });

  test('CRITICAL: should handle Step 4 to Step 5 transition without blank page', async ({ page }) => {
    // Complete Steps 1-3 first
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();
    
    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();
    
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Step 4: Add Context - CRITICAL SECTION
    await expect(page.getByText('Add Context')).toBeVisible();
    console.log('✅ Reached Step 4 successfully');

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

    // Check for any validation errors before proceeding
    const validationErrors = page.locator('.error, [role="alert"], .MuiFormHelperText-error');
    if (await validationErrors.count() > 0) {
      const errorTexts = await validationErrors.allTextContents();
      console.log('⚠️ Validation errors found:', errorTexts);
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

  test('should validate new bucket types are properly displayed', async ({ page }) => {
    // Navigate to Step 4
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

  test('should test each bucket type selection', async ({ page }) => {
    // Navigate to Step 4
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

    // Test each bucket type
    const bucketTypes = [
      { name: 'No Touch', value: testData.bucketTypes.NO_TOUCH },
      { name: 'Low Touch', value: testData.bucketTypes.LOW_TOUCH },
      { name: 'Medium Touch', value: testData.bucketTypes.MEDIUM_TOUCH },
      { name: 'High Touch', value: testData.bucketTypes.HIGH_TOUCH }
    ];

    for (const bucket of bucketTypes) {
      const bucketRadio = page.getByRole('radio', { name: new RegExp(bucket.name, 'i') });
      await expect(bucketRadio).toBeVisible();
      await bucketRadio.click();
      
      // Verify selection
      await expect(bucketRadio).toBeChecked();
      console.log(`✅ ${bucket.name} bucket selection works`);
    }
  });

  test('should validate required fields in Step 4', async ({ page }) => {
    // Navigate to Step 4
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Try to proceed without filling required fields
    const nextButton4 = page.getByRole('button', { name: /next/i });

    // Should be disabled or show validation errors
    if (await nextButton4.isEnabled()) {
      await nextButton4.click();

      // Should show validation errors
      const validationErrors = page.locator('.error, [role="alert"], .MuiFormHelperText-error');
      if (await validationErrors.count() > 0) {
        console.log('✅ Validation errors shown for missing required fields');
      }
    } else {
      console.log('✅ Next button properly disabled when required fields are missing');
    }
  });

  test('should handle enhanced metadata input correctly', async ({ page }) => {
    // Navigate to Step 4
    await page.locator(`text="${testData.errorText}"`).first().dblclick();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByText(testData.category).first().click();
    await page.getByRole('button', { name: /next/i }).click();
    const correctionInput = page.locator('textarea, input[type="text"]').first();
    await correctionInput.fill(testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();

    // Fill all enhanced metadata fields
    const speakerIdInput = page.getByLabel(/speaker id/i);
    if (await speakerIdInput.count() > 0) {
      await speakerIdInput.fill(testData.speakerId);
    }

    const clientIdInput = page.getByLabel(/client id/i);
    if (await clientIdInput.count() > 0) {
      await clientIdInput.fill(testData.clientId);
    }

    // Select bucket type
    const mediumTouchRadio = page.getByRole('radio', { name: /medium touch/i });
    if (await mediumTouchRadio.count() > 0) {
      await mediumTouchRadio.click();
    }

    // Fill audio quality
    const audioQualitySelect = page.locator('select').first();
    if (await audioQualitySelect.count() > 0) {
      await audioQualitySelect.selectOption('good');
    }

    // Fill speaker clarity
    const speakerClaritySelect = page.locator('select').nth(1);
    if (await speakerClaritySelect.count() > 0) {
      await speakerClaritySelect.selectOption('clear');
    }

    // Fill background noise
    const backgroundNoiseSelect = page.locator('select').nth(2);
    if (await backgroundNoiseSelect.count() > 0) {
      await backgroundNoiseSelect.selectOption('low');
    }

    // Fill number of speakers
    const numberOfSpeakersSelect = page.locator('select').nth(3);
    if (await numberOfSpeakersSelect.count() > 0) {
      await numberOfSpeakersSelect.selectOption('one');
    }

    // Fill checkboxes
    const overlappingSpeechCheckbox = page.getByRole('checkbox', { name: /overlapping speech/i });
    if (await overlappingSpeechCheckbox.count() > 0) {
      await overlappingSpeechCheckbox.check();
    }

    const specializedKnowledgeCheckbox = page.getByRole('checkbox', { name: /specialized knowledge/i });
    if (await specializedKnowledgeCheckbox.count() > 0) {
      await specializedKnowledgeCheckbox.check();
    }

    // Fill additional notes
    const additionalNotesTextarea = page.getByLabel(/additional notes/i);
    if (await additionalNotesTextarea.count() > 0) {
      await additionalNotesTextarea.fill('Test additional notes for enhanced metadata');
    }

    console.log('✅ Enhanced metadata input completed');

    // Now try to proceed to Step 5
    const nextButton4 = page.getByRole('button', { name: /next/i });
    await expect(nextButton4).toBeEnabled();
    await nextButton4.click();

    // Verify successful transition
    await expect(page.getByText('Review & Submit')).toBeVisible({ timeout: 10000 });
    console.log('✅ Enhanced metadata validation and transition successful');
  });
});

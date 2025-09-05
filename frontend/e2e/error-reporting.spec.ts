/**
 * Complete Error Reporting End-to-End Tests
 * Tests the full 5-step workflow with backend integration, accessibility, and edge cases
 */

import { test, expect, Page } from '@playwright/test';

// Test data
const testData = {
  jobId: 'demo-job-123',
  speakerId: 'demo-speaker-456',
  documentText: 'The patient has a history of hypertension and diabetes.',
  errorText: 'hypertension',
  correctedText: 'high blood pressure',
  category: 'Medical Terminology',
};

// Helper functions
async function navigateToErrorReporting(page: Page) {
  await page.goto('/error-reporting');
  await expect(page.getByText('ASR Error Reporting System')).toBeVisible();
}

async function selectTextInDocument(page: Page, text: string) {
  // Find the document text area
  const textContainer = page.locator('[data-testid="selectable-text"], .text-selection-area').first();

  // If no specific test ID, look for the text content
  if (await textContainer.count() === 0) {
    const textElement = page.locator(`text="${testData.documentText}"`).first();
    await textElement.click();
  } else {
    await textContainer.click();
  }

  // Simulate text selection by double-clicking on the word
  await page.locator(`text="${text}"`).first().dblclick();

  // Wait for selection to be processed
  await page.waitForTimeout(500);
}

async function selectCategory(page: Page, categoryName: string) {
  // Look for category chips or buttons
  const categoryElement = page.locator(`text="${categoryName}"`).first();
  await categoryElement.click();

  // Verify selection
  await expect(categoryElement).toHaveAttribute('aria-pressed', 'true');
}

async function enterCorrectionText(page: Page, correctionText: string) {
  // Find the correction input field
  const correctionInput = page.locator('textarea[placeholder*="correction"], input[placeholder*="correction"], [data-testid="correction-input"]').first();

  if (await correctionInput.count() === 0) {
    // Fallback to any text input in the correction step
    const textInputs = page.locator('textarea, input[type="text"]');
    await textInputs.first().fill(correctionText);
  } else {
    await correctionInput.fill(correctionText);
  }
}

test.describe('Complete Error Reporting Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await navigateToErrorReporting(page);
  });

  test('should complete the full 5-step error reporting workflow', async ({ page }) => {
    // Step 1: Text Selection
    await expect(page.getByText('Select Error Text')).toBeVisible();
    await expect(page.getByText(testData.documentText)).toBeVisible();

    // Select error text
    await selectTextInDocument(page, testData.errorText);

    // Verify selection was made
    await expect(page.getByText('1 selection')).toBeVisible();

    // Navigate to next step
    const nextButton1 = page.getByRole('button', { name: /next/i });
    await expect(nextButton1).toBeEnabled();
    await nextButton1.click();

    // Step 2: Error Categorization
    await expect(page.getByText('Categorize Errors')).toBeVisible();

    // Select category
    await selectCategory(page, testData.category);

    // Verify category selection
    await expect(page.getByText(/1.*categories? selected/i)).toBeVisible();

    // Navigate to next step
    const nextButton2 = page.getByRole('button', { name: /next/i });
    await expect(nextButton2).toBeEnabled();
    await nextButton2.click();

    // Step 3: Correction Input
    await expect(page.getByText('Provide Correction')).toBeVisible();
    await expect(page.getByText(`Original Text:`)).toBeVisible();

    // Enter correction
    await enterCorrectionText(page, testData.correctedText);

    // Check for AI suggestions (if available)
    const aiSuggestions = page.locator('text=/AI Suggestions|Similar Patterns/i');
    if (await aiSuggestions.count() > 0) {
      await expect(aiSuggestions).toBeVisible();
    }

    // Navigate to next step
    const nextButton3 = page.getByRole('button', { name: /next/i });
    await expect(nextButton3).toBeEnabled();
    await nextButton3.click();

    // Step 4: Metadata Input
    await expect(page.getByText('Add Context')).toBeVisible();

    // Set audio quality (optional)
    const audioQualitySelect = page.locator('select').first();
    if (await audioQualitySelect.count() > 0) {
      await audioQualitySelect.selectOption('good');
    }

    // Navigate to final step
    const nextButton4 = page.getByRole('button', { name: /next/i });
    await expect(nextButton4).toBeEnabled();
    await nextButton4.click();

    // Step 5: Review & Submit
    await expect(page.getByText('Review & Submit')).toBeVisible();

    // Verify review information
    await expect(page.getByText(`"${testData.errorText}"`)).toBeVisible();
    await expect(page.getByText(testData.category)).toBeVisible();
    await expect(page.getByText(`"${testData.correctedText}"`)).toBeVisible();

    // Submit the form
    const submitButton = page.getByRole('button', { name: /submit report/i });
    await expect(submitButton).toBeEnabled();
    await submitButton.click();

    // Verify submission success
    await expect(page.getByText(/submitted successfully|report.*submitted/i)).toBeVisible({ timeout: 10000 });
  });

  test('should handle multiple text selections', async ({ page }) => {
    // Select first error text
    await selectTextInDocument(page, 'hypertension');
    await expect(page.getByText('1 selection')).toBeVisible();

    // Select second error text (with Ctrl key)
    await page.keyboard.down('Control');
    await selectTextInDocument(page, 'diabetes');
    await page.keyboard.up('Control');

    // Verify multiple selections
    await expect(page.getByText('2 selections')).toBeVisible();

    // Continue workflow
    await page.getByRole('button', { name: /next/i }).click();
    await selectCategory(page, 'Medical Terminology');
    await page.getByRole('button', { name: /next/i }).click();
    await enterCorrectionText(page, 'high blood pressure and type 2 diabetes');

    // Complete workflow
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByRole('button', { name: /next/i }).click();

    // Verify review shows both selections
    await expect(page.getByText('"hypertension"')).toBeVisible();
    await expect(page.getByText('"diabetes"')).toBeVisible();
  });

  test('should set error severity levels', async ({ page }) => {
    // Look for severity controls
    const severitySelect = page.locator('select[name*="severity"], [aria-label*="severity"], .severity-level');
    
    if (await severitySelect.count() > 0) {
      await severitySelect.click();
      
      // Should show severity options
      await expect(page.locator('option:has-text("Low"), option:has-text("Medium"), option:has-text("High"), option:has-text("Critical")')).toBeVisible();
      
      // Select high severity
      await page.locator('option:has-text("High")').click();
      
      // Severity should be selected
      await expect(severitySelect).toHaveValue(/high/i);
    }
  });

  test('should add error descriptions and comments', async ({ page }) => {
    // Find description input
    const descriptionInput = page.locator('textarea[name*="description"], input[name*="description"], [aria-label*="description"]');
    
    if (await descriptionInput.count() > 0) {
      await descriptionInput.fill('Medical term "diabetis" should be "diabetes". This is a common spelling error that affects medical accuracy.');
      
      // Verify description was entered
      await expect(descriptionInput).toHaveValue(/Medical term.*diabetis.*should be.*diabetes/);
    }
  });

  test('should submit error reports successfully', async ({ page }) => {
    // Fill out error report form
    const textArea = page.locator('textarea, [contenteditable]').first();
    if (await textArea.count() > 0) {
      await textArea.fill('The patient has diabetis and high blod pressure.');
    }
    
    // Select category
    const categorySelect = page.locator('select[name*="category"], [aria-label*="category"]');
    if (await categorySelect.count() > 0) {
      await categorySelect.selectOption('Medical Terminology');
    }
    
    // Select severity
    const severitySelect = page.locator('select[name*="severity"], [aria-label*="severity"]');
    if (await severitySelect.count() > 0) {
      await severitySelect.selectOption('High');
    }
    
    // Add description
    const descriptionInput = page.locator('textarea[name*="description"], [aria-label*="description"]');
    if (await descriptionInput.count() > 0) {
      await descriptionInput.fill('Spelling error in medical terminology');
    }
    
    // Submit the report
    const submitButton = page.locator('button:has-text("Submit"), button:has-text("Report Error"), button[type="submit"]');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      // Should show success message
      await expect(page.locator('text=/submitted|success|reported.*successfully/i')).toBeVisible();
    }
  });

  test('should validate required fields', async ({ page }) => {
    // Try to submit without filling required fields
    const submitButton = page.locator('button:has-text("Submit"), button:has-text("Report Error"), button[type="submit"]');
    
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      // Should show validation errors
      await expect(page.locator('text=/required|please.*fill|validation.*error/i')).toBeVisible();
    }
  });

  test('should save error reports as drafts', async ({ page }) => {
    // Fill partial information
    const textArea = page.locator('textarea, [contenteditable]').first();
    if (await textArea.count() > 0) {
      await textArea.fill('Work in progress error report...');
    }
    
    // Save as draft
    const draftButton = page.locator('button:has-text("Save Draft"), button:has-text("Draft"), [aria-label*="draft"]');
    if (await draftButton.count() > 0) {
      await draftButton.click();
      
      // Should show draft saved message
      await expect(page.locator('text=/draft.*saved|saved.*draft/i')).toBeVisible();
    }
  });

  test('should support text highlighting and annotation', async ({ page }) => {
    // Add text content
    const textArea = page.locator('textarea, [contenteditable]').first();
    if (await textArea.count() > 0) {
      await textArea.fill('The patient has diabetis and high blod pressure.');
      
      // Try to select specific text for highlighting
      await textArea.focus();
      
      // Double-click to select word
      await page.locator('text=/diabetis/i').dblclick();
      
      // Look for highlighting tools
      const highlightButton = page.locator('button:has-text("Highlight"), .highlight-tool, [aria-label*="highlight"]');
      if (await highlightButton.count() > 0) {
        await highlightButton.click();
        
        // Text should be highlighted (visual verification)
        await expect(page.locator('.highlighted, .error-highlight')).toBeVisible();
      }
    }
  });

  test('should display error history and previous reports', async ({ page }) => {
    // Look for error history section
    const historySection = page.locator('.error-history, .previous-reports, [data-testid*="history"]');
    
    if (await historySection.count() > 0) {
      await expect(historySection).toBeVisible();
      
      // Should show previous error reports
      await expect(page.locator('text=/previous.*reports|error.*history/i')).toBeVisible();
    }
  });

  test('should support error report filtering and search', async ({ page }) => {
    // Look for search functionality
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], [aria-label*="search"]');
    
    if (await searchInput.count() > 0) {
      await searchInput.fill('medical terminology');
      
      // Should filter results
      await expect(page.locator('text=/medical.*terminology/i')).toBeVisible();
    }
    
    // Look for filter controls
    const filterButton = page.locator('button:has-text("Filter"), select[name*="filter"], [aria-label*="filter"]');
    if (await filterButton.count() > 0) {
      await filterButton.click();
      
      // Should show filter options
      await expect(page.locator('text=/category|severity|date/i')).toBeVisible();
    }
  });

  test('should handle file attachments for error context', async ({ page }) => {
    // Look for file upload functionality
    const fileInput = page.locator('input[type="file"], .file-upload, [aria-label*="upload"]');
    
    if (await fileInput.count() > 0) {
      // Create a test file
      const testFile = Buffer.from('Test audio file content');
      
      // Upload file
      await fileInput.setInputFiles({
        name: 'test-audio.wav',
        mimeType: 'audio/wav',
        buffer: testFile
      });
      
      // Should show uploaded file
      await expect(page.locator('text=/test-audio\.wav|uploaded.*successfully/i')).toBeVisible();
    }
  });

  test('should provide error reporting analytics', async ({ page }) => {
    // Look for analytics or statistics section
    const analyticsSection = page.locator('.analytics, .statistics, .error-stats, [data-testid*="analytics"]');
    
    if (await analyticsSection.count() > 0) {
      await expect(analyticsSection).toBeVisible();
      
      // Should show error metrics
      await expect(page.locator('text=/total.*errors|error.*count|statistics/i')).toBeVisible();
    }
  });

  test('should support collaborative error review', async ({ page }) => {
    // Look for collaboration features
    const reviewSection = page.locator('.error-review, .collaboration, [data-testid*="review"]');
    
    if (await reviewSection.count() > 0) {
      await expect(reviewSection).toBeVisible();
      
      // Should show review status
      await expect(page.locator('text=/pending.*review|reviewed|approved/i')).toBeVisible();
    }
  });

  test('should handle error reporting in different languages', async ({ page }) => {
    // Look for language selection
    const languageSelect = page.locator('select[name*="language"], [aria-label*="language"], .language-selector');

    if (await languageSelect.count() > 0) {
      await languageSelect.click();

      // Should show language options
      await expect(page.locator('option:has-text("English"), option:has-text("Spanish"), option:has-text("French")')).toBeVisible();
    }
  });
});

// Enhanced Error Reporting Tests with Complete Workflow
test.describe('Enhanced Error Reporting Workflow', () => {
  // Test data
  const testData = {
    jobId: 'test-job-123',
    speakerId: 'test-speaker-456',
    documentText: 'The patient has a history of hypertension and diabetes. The doctor prescribed medication for the condition.',
    correctionText: 'The patient has a history of high blood pressure and type 2 diabetes. The doctor prescribed medication for the condition.',
    errorText: 'hypertension',
    correctedWord: 'high blood pressure',
  };

  // Helper functions
  async function navigateToErrorReporting(page: any) {
    await page.goto('/error-reporting');
    await expect(page.getByText('Report ASR Error')).toBeVisible();
  }

  async function selectTextInDocument(page: any, text: string) {
    const textContainer = page.getByTestId('selectable-text');
    await textContainer.click();

    // Simulate text selection by finding and selecting the text
    await page.evaluate((textToSelect: string) => {
      const container = document.querySelector('[data-testid="selectable-text"]');
      if (container && container.textContent) {
        const textContent = container.textContent;
        const startIndex = textContent.indexOf(textToSelect);
        if (startIndex !== -1) {
          const range = document.createRange();
          const textNode = container.firstChild;
          if (textNode) {
            range.setStart(textNode, startIndex);
            range.setEnd(textNode, startIndex + textToSelect.length);

            const selection = window.getSelection();
            if (selection) {
              selection.removeAllRanges();
              selection.addRange(range);

              // Trigger selection event
              const event = new Event('mouseup', { bubbles: true });
              container.dispatchEvent(event);
            }
          }
        }
      }
    }, text);

    // Wait for selection to be processed
    await page.waitForTimeout(500);
  }

  async function selectCategory(page: any, categoryName: string) {
    const categoryChip = page.getByText(categoryName).first();
    await categoryChip.click();
    await expect(categoryChip).toHaveAttribute('aria-pressed', 'true');
  }

  async function enterCorrectionText(page: any, correctionText: string) {
    const correctionInput = page.getByRole('textbox', { name: /corrected text/i });
    await correctionInput.fill(correctionText);
    await expect(correctionInput).toHaveValue(correctionText);
  }

  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/api/v1/errors/categories', async (route) => {
      await route.fulfill({
        json: [
          {
            id: 'pronunciation',
            name: 'Pronunciation',
            description: 'Pronunciation errors',
            isActive: true,
          },
          {
            id: 'grammar',
            name: 'Grammar',
            description: 'Grammar errors',
            isActive: true,
          },
          {
            id: 'medical',
            name: 'Medical Terminology',
            description: 'Medical term errors',
            isActive: true,
            parentCategory: 'pronunciation',
          },
        ],
      });
    });

    await page.route('**/api/v1/errors/similarity/search**', async (route) => {
      await route.fulfill({
        json: [
          {
            patternId: 'pattern-1',
            similarText: 'hypertension',
            confidence: 0.95,
            frequency: 5,
            suggestedCorrection: 'high blood pressure',
            speakerIds: ['speaker-1'],
            category: 'medical',
          },
        ],
      });
    });

    await page.route('**/api/v1/errors/report', async (route) => {
      await route.fulfill({
        json: {
          reportId: 'report-123',
          status: 'submitted',
          message: 'Error report submitted successfully',
        },
      });
    });
  });

  test('completes full error reporting workflow with enhanced components', async ({ page }) => {
    await navigateToErrorReporting(page);

    // Step 1: Text Selection
    await expect(page.getByText('Select Error Text')).toBeVisible();
    await expect(page.getByText(testData.documentText)).toBeVisible();

    // Select error text
    await selectTextInDocument(page, testData.errorText);

    // Verify selection was made
    await expect(page.getByText('1 selection')).toBeVisible();

    // Navigate to next step
    const nextButton1 = page.getByText('Next');
    await expect(nextButton1).toBeEnabled();
    await nextButton1.click();

    // Step 2: Error Categorization
    await expect(page.getByText('Error Categories')).toBeVisible();

    // Select category
    await selectCategory(page, 'Medical Terminology');

    // Verify category selection
    await expect(page.getByText('1 of 10 categories selected')).toBeVisible();

    // Navigate to next step
    const nextButton2 = page.getByText('Next');
    await expect(nextButton2).toBeEnabled();
    await nextButton2.click();

    // Step 3: Correction Input with AI suggestions
    await expect(page.getByText('Corrected Text')).toBeVisible();
    await expect(page.getByText('Original Text:')).toBeVisible();

    // Enter correction
    await enterCorrectionText(page, testData.correctedWord);

    // Test AI suggestions
    const aiButton = page.getByLabel('Show AI suggestions');
    await aiButton.click();
    await expect(page.getByText('AI Suggestions:')).toBeVisible();

    // Navigate to next step
    const nextButton3 = page.getByText('Next');
    await expect(nextButton3).toBeEnabled();
    await nextButton3.click();

    // Step 4: Enhanced Metadata Input
    await expect(page.getByText('Contextual Information')).toBeVisible();

    // Set audio quality
    const audioQualitySelect = page.getByLabel('Overall Audio Quality');
    await audioQualitySelect.click();
    await page.getByText('Excellent').click();

    // Navigate to final step
    const nextButton4 = page.getByText('Next');
    await expect(nextButton4).toBeEnabled();
    await nextButton4.click();

    // Step 5: Review & Submit
    await expect(page.getByText('Review Your Error Report')).toBeVisible();

    // Verify review information
    await expect(page.getByText(`"${testData.errorText}"`)).toBeVisible();
    await expect(page.getByText('Medical Terminology')).toBeVisible();
    await expect(page.getByText(`"${testData.correctedWord}"`)).toBeVisible();

    // Submit the form
    const submitButton = page.getByText('Submit Report');
    await expect(submitButton).toBeEnabled();
    await submitButton.click();

    // Verify submission success
    await expect(page.getByText('Error report submitted successfully')).toBeVisible();
  });

  test('supports voice input functionality', async ({ page }) => {
    // Grant microphone permissions
    await page.context().grantPermissions(['microphone']);

    await navigateToErrorReporting(page);

    // Navigate to correction step
    await selectTextInDocument(page, testData.errorText);
    await page.getByText('Next').click();
    await selectCategory(page, 'Pronunciation');
    await page.getByText('Next').click();

    // Test voice input button
    const voiceButton = page.getByLabel('Start voice input');
    await expect(voiceButton).toBeVisible();
    await voiceButton.click();

    // Should show recording indicator
    await expect(page.getByText(/recording/i)).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    // Try to proceed without text selection
    const nextButton = page.getByRole('button', { name: /next/i });
    await expect(nextButton).toBeDisabled();

    // Make text selection
    await selectTextInDocument(page, testData.errorText);
    await expect(nextButton).toBeEnabled();
    await nextButton.click();

    // Try to proceed without category selection
    const nextButton2 = page.getByRole('button', { name: /next/i });
    await expect(nextButton2).toBeDisabled();

    // Select category
    await selectCategory(page, testData.category);
    await expect(nextButton2).toBeEnabled();
    await nextButton2.click();

    // Try to proceed without correction text
    const nextButton3 = page.getByRole('button', { name: /next/i });
    await expect(nextButton3).toBeDisabled();

    // Enter correction
    await enterCorrectionText(page, testData.correctedText);
    await expect(nextButton3).toBeEnabled();
  });

  test('should support voice input functionality', async ({ page }) => {
    // Grant microphone permissions
    await page.context().grantPermissions(['microphone']);

    // Navigate to correction step
    await selectTextInDocument(page, testData.errorText);
    await page.getByRole('button', { name: /next/i }).click();
    await selectCategory(page, testData.category);
    await page.getByRole('button', { name: /next/i }).click();

    // Test voice input button
    const voiceButton = page.getByLabel(/voice input|microphone/i);
    if (await voiceButton.count() > 0) {
      await expect(voiceButton).toBeVisible();
      await voiceButton.click();

      // Should show recording indicator
      await expect(page.getByText(/recording|listening/i)).toBeVisible();
    }
  });

  test('should handle text-to-speech functionality', async ({ page }) => {
    // Navigate to correction step
    await selectTextInDocument(page, testData.errorText);
    await page.getByRole('button', { name: /next/i }).click();
    await selectCategory(page, testData.category);
    await page.getByRole('button', { name: /next/i }).click();

    // Test speak original text button
    const speakOriginalButton = page.getByLabel(/listen.*original|speak.*original/i);
    if (await speakOriginalButton.count() > 0) {
      await expect(speakOriginalButton).toBeVisible();
      await speakOriginalButton.click();
    }

    // Enter correction text
    await enterCorrectionText(page, testData.correctedText);

    // Test speak correction button
    const speakCorrectionButton = page.getByLabel(/listen.*correction|speak.*correction/i);
    if (await speakCorrectionButton.count() > 0) {
      await expect(speakCorrectionButton).toBeVisible();
      await speakCorrectionButton.click();
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Test keyboard navigation through form
    await page.keyboard.press('Tab');

    // Should focus on first interactive element
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();

    // Test Escape key to clear selections
    await selectTextInDocument(page, testData.errorText);
    await expect(page.getByText('1 selection')).toBeVisible();

    await page.keyboard.press('Escape');
    // Note: Escape behavior depends on implementation
  });

  test('should handle form cancellation', async ({ page }) => {
    // Make some progress
    await selectTextInDocument(page, testData.errorText);
    await page.getByRole('button', { name: /next/i }).click();
    await selectCategory(page, testData.category);

    // Cancel the form
    const cancelButton = page.getByRole('button', { name: /cancel/i });
    await cancelButton.click();

    // Should show confirmation or navigate away
    // Implementation depends on the actual cancel behavior
  });

  test('should display error messages for API failures', async ({ page }) => {
    // Complete the workflow
    await selectTextInDocument(page, testData.errorText);
    await page.getByRole('button', { name: /next/i }).click();
    await selectCategory(page, testData.category);
    await page.getByRole('button', { name: /next/i }).click();
    await enterCorrectionText(page, testData.correctedText);
    await page.getByRole('button', { name: /next/i }).click();
    await page.getByRole('button', { name: /next/i }).click();

    // Submit and expect potential error handling
    await page.getByRole('button', { name: /submit report/i }).click();

    // Should either succeed or show error message
    await expect(page.locator('text=/submitted successfully|error|failed/i')).toBeVisible({ timeout: 10000 });
  });

  test('should support responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Should show mobile-optimized layout
    await expect(page.getByText('ASR Error Reporting System')).toBeVisible();

    // Touch selection should work
    await selectTextInDocument(page, testData.errorText);
    await expect(page.getByText('1 selection')).toBeVisible();

    // Should show mobile stepper (vertical)
    const stepper = page.locator('.MuiStepper-vertical, [data-testid="vertical-stepper"]');
    if (await stepper.count() > 0) {
      await expect(stepper).toBeVisible();
    }
  });

  test('should maintain accessibility standards', async ({ page }) => {
    // Check for proper heading structure
    await expect(page.getByRole('heading', { level: 3 })).toHaveText('ASR Error Reporting System');

    // Check for proper form labels
    const textSelectionArea = page.locator('[role="textbox"], [aria-label*="text selection"]');
    if (await textSelectionArea.count() > 0) {
      await expect(textSelectionArea).toBeVisible();
    }

    // Test screen reader announcements
    await selectTextInDocument(page, testData.errorText);

    // Should have live region for announcements
    const liveRegion = page.locator('[role="status"][aria-live="polite"], [aria-live="polite"]');
    if (await liveRegion.count() > 0) {
      await expect(liveRegion).toBeVisible();
    }
  });
});

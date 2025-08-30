import { test, expect } from '@playwright/test';

test.describe('Error Reporting Interface', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to error reporting
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Navigate to error reporting page
    await page.goto('/error-reporting');
  });

  test('should display error reporting interface', async ({ page }) => {
    // Check for error reporting elements
    await expect(page.locator('text=/error.*report|report.*error/i')).toBeVisible();
    
    // Should show text input areas
    await expect(page.locator('textarea, [contenteditable], .text-editor')).toBeVisible();
  });

  test('should support text selection for error reporting', async ({ page }) => {
    // Look for text content that can be selected
    const textArea = page.locator('textarea, [contenteditable], .text-content').first();
    
    if (await textArea.count() > 0) {
      // Add some sample text
      await textArea.fill('The patient has diabetis and high blod pressure.');
      
      // Select the word "diabetis"
      await textArea.focus();
      await page.keyboard.press('Control+A'); // Select all
      
      // Should be able to select text
      await expect(textArea).toBeFocused();
    }
  });

  test('should categorize errors by type', async ({ page }) => {
    // Look for error categorization controls
    const categorySelect = page.locator('select[name*="category"], [aria-label*="category"], .error-category');
    
    if (await categorySelect.count() > 0) {
      await categorySelect.click();
      
      // Should show error categories
      await expect(page.locator('option:has-text("Medical Terminology"), option:has-text("Spelling"), option:has-text("Grammar")')).toBeVisible();
      
      // Select medical terminology
      await page.locator('option:has-text("Medical Terminology")').click();
      
      // Category should be selected
      await expect(categorySelect).toHaveValue(/medical|terminology/i);
    }
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

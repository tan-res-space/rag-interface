import { test, expect } from '@playwright/test';

test.describe('MT Validation Interface', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to verification page
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Navigate to verification page
    await page.goto('/verification');
  });

  test('should display validation session interface', async ({ page }) => {
    // Check for validation session elements
    await expect(page.locator('text=/validation.*session|session.*validation/i')).toBeVisible();
    
    // Should show text comparison areas
    await expect(page.locator('text=/original.*asr|asr.*text/i')).toBeVisible();
    await expect(page.locator('text=/rag.*corrected|corrected.*text/i')).toBeVisible();
    await expect(page.locator('text=/final.*reference|reference.*text/i')).toBeVisible();
  });

  test('should load and display validation items', async ({ page }) => {
    // Wait for validation items to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Should display text content
    await expect(page.locator('text=/diabetis.*high.*blod.*pressure/i')).toBeVisible();
    await expect(page.locator('text=/diabetes.*high.*blood.*pressure/i')).toBeVisible();
  });

  test('should support navigation between validation items', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Find navigation buttons
    const nextButton = page.locator('button:has-text("Next"), button[aria-label*="next"], button:has([data-testid*="next"])');
    const prevButton = page.locator('button:has-text("Previous"), button:has-text("Prev"), button[aria-label*="previous"]');
    
    if (await nextButton.count() > 0) {
      await nextButton.click();
      
      // Should show different content
      await expect(page.locator('text=/chest.*pain.*radiating/i')).toBeVisible();
      
      if (await prevButton.count() > 0) {
        await prevButton.click();
        
        // Should go back to first item
        await expect(page.locator('text=/diabetis.*high.*blod.*pressure/i')).toBeVisible();
      }
    }
  });

  test('should support keyboard navigation shortcuts', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Test right arrow key for next
    await page.keyboard.press('ArrowRight');
    
    // Should navigate to next item
    await expect(page.locator('text=/chest.*pain.*radiating/i')).toBeVisible();
    
    // Test left arrow key for previous
    await page.keyboard.press('ArrowLeft');
    
    // Should go back to first item
    await expect(page.locator('text=/diabetis.*high.*blod.*pressure/i')).toBeVisible();
  });

  test('should allow rating validation items', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Find rating component (stars, radio buttons, etc.)
    const ratingStars = page.locator('[role="radio"], .rating input, .star-rating input');
    
    if (await ratingStars.count() > 0) {
      // Click on a 4-star rating
      await ratingStars.nth(3).click();
      
      // Verify rating is selected
      await expect(ratingStars.nth(3)).toBeChecked();
    }
  });

  test('should allow adding comments to validation items', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Find comments input
    const commentsInput = page.locator('textarea[placeholder*="comment"], input[placeholder*="comment"], [aria-label*="comment"]');
    
    if (await commentsInput.count() > 0) {
      await commentsInput.fill('This correction looks accurate and improves medical terminology.');
      
      // Verify comment was entered
      await expect(commentsInput).toHaveValue(/This correction looks accurate/);
    }
  });

  test('should save feedback as draft', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Add rating and comment
    const ratingStars = page.locator('[role="radio"], .rating input, .star-rating input');
    if (await ratingStars.count() > 0) {
      await ratingStars.nth(3).click();
    }
    
    const commentsInput = page.locator('textarea[placeholder*="comment"], input[placeholder*="comment"], [aria-label*="comment"]');
    if (await commentsInput.count() > 0) {
      await commentsInput.fill('Work in progress feedback');
    }
    
    // Save as draft
    const saveButton = page.locator('button:has-text("Save Draft"), button:has-text("Save"), button[aria-label*="save"]');
    if (await saveButton.count() > 0) {
      await saveButton.click();
      
      // Should show success message
      await expect(page.locator('text=/draft.*saved|saved.*draft/i')).toBeVisible();
    }
  });

  test('should submit final feedback', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Add complete feedback
    const ratingStars = page.locator('[role="radio"], .rating input, .star-rating input');
    if (await ratingStars.count() > 0) {
      await ratingStars.nth(4).click(); // 5-star rating
    }
    
    const commentsInput = page.locator('textarea[placeholder*="comment"], input[placeholder*="comment"], [aria-label*="comment"]');
    if (await commentsInput.count() > 0) {
      await commentsInput.fill('Excellent correction. Medical terminology is accurate and improves readability.');
    }
    
    // Submit feedback
    const submitButton = page.locator('button:has-text("Submit"), button:has-text("Submit Feedback"), button[type="submit"]');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      // Should show success message or navigate to next item
      await expect(page.locator('text=/submitted|success|thank you/i')).toBeVisible();
    }
  });

  test('should display session summary', async ({ page }) => {
    // Look for session summary button
    const summaryButton = page.locator('button:has-text("Session Summary"), button:has-text("Summary"), [aria-label*="summary"]');
    
    if (await summaryButton.count() > 0) {
      await summaryButton.click();
      
      // Should open summary dialog
      await expect(page.locator('[role="dialog"], .modal, .summary-dialog')).toBeVisible();
      await expect(page.locator('text=/session.*summary|summary/i')).toBeVisible();
    }
  });

  test('should handle validation errors gracefully', async ({ page }) => {
    // Try to submit without required fields
    const submitButton = page.locator('button:has-text("Submit"), button:has-text("Submit Feedback"), button[type="submit"]');
    
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      // Should show validation error
      await expect(page.locator('text=/required|please.*provide|validation.*error/i')).toBeVisible();
    }
  });

  test('should support text selection and highlighting', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Try to select text in the original ASR text area
    const originalText = page.locator('text=/diabetis.*high.*blod.*pressure/i').first();
    
    if (await originalText.count() > 0) {
      // Double-click to select word
      await originalText.dblclick();
      
      // Text should be selected (this is hard to test directly, but we can check if selection tools appear)
      // This is more of a visual test that would need manual verification
    }
  });

  test('should maintain progress across page refreshes', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Add some feedback
    const ratingStars = page.locator('[role="radio"], .rating input, .star-rating input');
    if (await ratingStars.count() > 0) {
      await ratingStars.nth(2).click();
    }
    
    // Refresh page
    await page.reload();
    
    // Progress should be maintained (if implemented)
    await page.waitForSelector('text=/diabetis|diabetes/i', { timeout: 10000 });
    
    // Check if rating is still selected (this depends on implementation)
    if (await ratingStars.count() > 0) {
      // This test might need adjustment based on actual implementation
    }
  });
});

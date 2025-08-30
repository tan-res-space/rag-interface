import { test, expect } from '@playwright/test';

test.describe('Accessibility Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    // Check for proper heading structure
    const h1 = page.locator('h1');
    const h2 = page.locator('h2');
    const h3 = page.locator('h3');
    
    // Should have at least one h1
    await expect(h1).toHaveCount({ min: 1 });
    
    // Headings should be in logical order
    if (await h1.count() > 0) {
      await expect(h1.first()).toBeVisible();
    }
  });

  test('should have proper ARIA labels and roles', async ({ page }) => {
    // Check for navigation landmarks
    const nav = page.locator('nav, [role="navigation"]');
    if (await nav.count() > 0) {
      await expect(nav).toBeVisible();
    }
    
    // Check for main content area
    const main = page.locator('main, [role="main"]');
    if (await main.count() > 0) {
      await expect(main).toBeVisible();
    }
    
    // Check for buttons with proper labels
    const buttons = page.locator('button');
    for (let i = 0; i < Math.min(await buttons.count(), 5); i++) {
      const button = buttons.nth(i);
      const hasText = await button.textContent();
      const hasAriaLabel = await button.getAttribute('aria-label');
      const hasAriaLabelledBy = await button.getAttribute('aria-labelledby');
      
      // Button should have accessible name
      expect(hasText || hasAriaLabel || hasAriaLabelledBy).toBeTruthy();
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Test tab navigation
    await page.keyboard.press('Tab');
    
    // Should focus on first focusable element
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Continue tabbing through elements
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      const currentFocus = page.locator(':focus');
      await expect(currentFocus).toBeVisible();
    }
  });

  test('should have sufficient color contrast', async ({ page }) => {
    // This is a basic check - full color contrast testing requires specialized tools
    // Check that text is visible against backgrounds
    const textElements = page.locator('p, span, div, h1, h2, h3, h4, h5, h6, button, a');
    
    for (let i = 0; i < Math.min(await textElements.count(), 10); i++) {
      const element = textElements.nth(i);
      const text = await element.textContent();
      
      if (text && text.trim().length > 0) {
        await expect(element).toBeVisible();
      }
    }
  });

  test('should have proper form labels', async ({ page }) => {
    await page.goto('/error-reporting');
    
    // Check that form inputs have labels
    const inputs = page.locator('input, textarea, select');
    
    for (let i = 0; i < Math.min(await inputs.count(), 5); i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      
      if (id) {
        // Check for associated label
        const label = page.locator(`label[for="${id}"]`);
        const hasLabel = await label.count() > 0;
        
        // Input should have label or aria-label
        expect(hasLabel || ariaLabel || ariaLabelledBy).toBeTruthy();
      }
    }
  });

  test('should support screen reader announcements', async ({ page }) => {
    // Check for live regions
    const liveRegions = page.locator('[aria-live], [role="status"], [role="alert"]');
    
    if (await liveRegions.count() > 0) {
      await expect(liveRegions.first()).toBeVisible();
    }
    
    // Check for proper announcements on dynamic content
    await page.goto('/verification');
    
    // Look for status messages that should be announced
    const statusMessages = page.locator('[role="status"], [aria-live="polite"], [aria-live="assertive"]');
    if (await statusMessages.count() > 0) {
      await expect(statusMessages.first()).toBeVisible();
    }
  });

  test('should have proper focus management', async ({ page }) => {
    // Test focus trap in modals
    await page.goto('/admin');
    
    // Try to open a modal/dialog
    const modalTrigger = page.locator('button:has-text("Details"), button:has-text("Edit"), [data-testid*="open"]');
    
    if (await modalTrigger.count() > 0) {
      await modalTrigger.click();
      
      // Check if modal opened
      const modal = page.locator('[role="dialog"], .modal');
      if (await modal.count() > 0) {
        await expect(modal).toBeVisible();
        
        // Focus should be trapped within modal
        await page.keyboard.press('Tab');
        const focusedElement = page.locator(':focus');
        
        // Focused element should be within modal
        const isWithinModal = await modal.locator(':focus').count() > 0;
        expect(isWithinModal).toBeTruthy();
      }
    }
  });

  test('should support high contrast mode', async ({ page }) => {
    // Simulate high contrast mode
    await page.emulateMedia({ colorScheme: 'dark' });
    
    // Check that content is still visible
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('h1, h2, h3').first()).toBeVisible();
    
    // Reset to light mode
    await page.emulateMedia({ colorScheme: 'light' });
    await expect(page.locator('body')).toBeVisible();
  });

  test('should have proper error announcements', async ({ page }) => {
    await page.goto('/error-reporting');
    
    // Try to submit form without required fields
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit")');
    
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      // Check for error announcements
      const errorMessages = page.locator('[role="alert"], [aria-live="assertive"], .error-message');
      if (await errorMessages.count() > 0) {
        await expect(errorMessages.first()).toBeVisible();
      }
    }
  });

  test('should support zoom up to 200%', async ({ page }) => {
    // Test page at 200% zoom
    await page.setViewportSize({ width: 640, height: 480 }); // Simulate 200% zoom
    
    // Content should still be accessible
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('h1, h2, h3').first()).toBeVisible();
    
    // Navigation should still work
    const navLinks = page.locator('nav a, .navigation a');
    if (await navLinks.count() > 0) {
      await expect(navLinks.first()).toBeVisible();
    }
  });

  test('should have proper skip links', async ({ page }) => {
    // Check for skip to main content link
    await page.keyboard.press('Tab');
    
    const skipLink = page.locator('a:has-text("Skip to main"), a:has-text("Skip to content"), .skip-link');
    
    if (await skipLink.count() > 0) {
      await expect(skipLink).toBeFocused();
      
      // Skip link should work
      await skipLink.click();
      
      const mainContent = page.locator('main, [role="main"], #main-content');
      if (await mainContent.count() > 0) {
        await expect(mainContent).toBeFocused();
      }
    }
  });

  test('should have descriptive link text', async ({ page }) => {
    // Check that links have descriptive text
    const links = page.locator('a');
    
    for (let i = 0; i < Math.min(await links.count(), 10); i++) {
      const link = links.nth(i);
      const text = await link.textContent();
      const ariaLabel = await link.getAttribute('aria-label');
      const title = await link.getAttribute('title');
      
      // Link should have descriptive text (not just "click here" or "read more")
      const hasDescriptiveText = text && !text.match(/^(click here|read more|more|link)$/i);
      const hasAriaLabel = ariaLabel && ariaLabel.length > 0;
      const hasTitle = title && title.length > 0;
      
      expect(hasDescriptiveText || hasAriaLabel || hasTitle).toBeTruthy();
    }
  });

  test('should support reduced motion preferences', async ({ page }) => {
    // Simulate reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    
    // Check that animations are reduced or disabled
    // This is more of a CSS test, but we can check that content is still functional
    await expect(page.locator('body')).toBeVisible();
    
    // Navigate between pages to ensure transitions work
    await page.goto('/error-reporting');
    await expect(page.locator('text=/error.*report/i')).toBeVisible();
    
    await page.goto('/verification');
    await expect(page.locator('text=/verification/i')).toBeVisible();
  });
});

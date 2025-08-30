import { test, expect } from '@playwright/test';

test.describe('Navigation and Routing', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('should navigate to dashboard from root', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.locator('text=/dashboard/i')).toBeVisible();
  });

  test('should navigate to error reporting page', async ({ page }) => {
    // Find and click error reporting navigation link
    await page.locator('a[href*="error-reporting"], button:has-text("Error Reporting"), nav a:has-text("Error")').click();
    
    await expect(page).toHaveURL(/.*\/error-reporting/);
    await expect(page.locator('text=/error.*report/i')).toBeVisible();
  });

  test('should navigate to verification page', async ({ page }) => {
    // Find and click verification navigation link
    await page.locator('a[href*="verification"], button:has-text("Verification"), nav a:has-text("Verification")').click();
    
    await expect(page).toHaveURL(/.*\/verification/);
    await expect(page.locator('text=/verification/i')).toBeVisible();
  });

  test('should navigate to admin page (role-based)', async ({ page }) => {
    // Find and click admin navigation link
    await page.locator('a[href*="admin"], button:has-text("Admin"), nav a:has-text("Admin")').click();
    
    await expect(page).toHaveURL(/.*\/admin/);
    await expect(page.locator('text=/admin/i')).toBeVisible();
  });

  test('should show 404 page for invalid routes', async ({ page }) => {
    await page.goto('/invalid-route-that-does-not-exist');
    
    // Should show 404 page or redirect
    await expect(page.locator('text=/404|not found|page not found/i')).toBeVisible();
  });

  test('should have working breadcrumb navigation', async ({ page }) => {
    // Navigate to a nested page
    await page.goto('/error-reporting');
    
    // Check if breadcrumbs exist and are functional
    const breadcrumbs = page.locator('[aria-label*="breadcrumb"], .breadcrumb, nav ol, nav ul');
    if (await breadcrumbs.count() > 0) {
      await expect(breadcrumbs).toBeVisible();
      
      // Click on a breadcrumb link if available
      const homeLink = breadcrumbs.locator('a:has-text("Home"), a:has-text("Dashboard")').first();
      if (await homeLink.count() > 0) {
        await homeLink.click();
        await expect(page).toHaveURL(/.*\/dashboard/);
      }
    }
  });

  test('should have responsive navigation menu', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Look for mobile menu toggle
    const menuToggle = page.locator('button[aria-label*="menu"], button:has-text("☰"), .menu-toggle, [data-testid*="menu"]');
    
    if (await menuToggle.count() > 0) {
      await expect(menuToggle).toBeVisible();
      
      // Click to open menu
      await menuToggle.click();
      
      // Navigation should be visible
      await expect(page.locator('nav, .navigation, .menu')).toBeVisible();
    }
  });

  test('should highlight active navigation item', async ({ page }) => {
    // Navigate to error reporting
    await page.goto('/error-reporting');
    
    // Check if the error reporting nav item is highlighted/active
    const activeNavItem = page.locator('nav a[href*="error-reporting"], .nav-item.active, .active');
    if (await activeNavItem.count() > 0) {
      await expect(activeNavItem).toHaveClass(/active|current|selected/);
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Focus on the first navigation item
    await page.keyboard.press('Tab');
    
    // Navigate using arrow keys if supported
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    
    // Should navigate to a different page
    await expect(page).not.toHaveURL(/.*\/dashboard$/);
  });

  test('should handle back/forward browser navigation', async ({ page }) => {
    // Navigate to error reporting
    await page.goto('/error-reporting');
    await expect(page).toHaveURL(/.*\/error-reporting/);
    
    // Navigate to verification
    await page.goto('/verification');
    await expect(page).toHaveURL(/.*\/verification/);
    
    // Use browser back button
    await page.goBack();
    await expect(page).toHaveURL(/.*\/error-reporting/);
    
    // Use browser forward button
    await page.goForward();
    await expect(page).toHaveURL(/.*\/verification/);
  });

  test('should load pages within reasonable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/error-reporting');
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
    
    // Page should be interactive
    await expect(page.locator('body')).toBeVisible();
  });
});

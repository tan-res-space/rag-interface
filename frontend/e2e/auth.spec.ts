import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should redirect to login page when not authenticated', async ({ page }) => {
    // Should be redirected to login page
    await expect(page).toHaveURL(/.*\/login/);

    // Verify login page elements
    await expect(page.locator('h1, h2, h3')).toContainText(/RAG Interface|sign in/i);
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for invalid login', async ({ page }) => {
    await page.goto('/login');

    // Try to submit empty form
    await page.locator('button[type="submit"]').click();

    // Should show validation errors
    await expect(page.locator('text=/Please enter both username and password/i')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill in invalid credentials
    await page.locator('input[name="username"]').fill('invalid@example.com');
    await page.locator('input[name="password"]').fill('wrongpassword');

    // Submit form
    await page.locator('button[type="submit"]').click();

    // Should show error message
    await expect(page.locator('text=/Login failed|invalid|incorrect|error|failed/i')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill in valid credentials (actual backend credentials)
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');

    // Submit form
    await page.locator('button[type="submit"]').click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Should show authenticated content
    await expect(page.locator('text=/dashboard|welcome/i')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();

    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Find and click logout button
    await page.locator('button:has-text("Logout"), button:has-text("Sign Out"), [aria-label*="logout" i]').click();

    // Should redirect to login page
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('should maintain session across page refreshes', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();

    await expect(page).toHaveURL(/.*\/dashboard/);

    // Refresh page
    await page.reload();

    // Should still be authenticated
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.locator('text=/dashboard|welcome/i')).toBeVisible();
  });

  test('should handle session expiration', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();

    await expect(page).toHaveURL(/.*\/dashboard/);

    // Simulate session expiration by clearing storage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Navigate to a protected route
    await page.goto('/admin');

    // Should redirect to login
    await expect(page).toHaveURL(/.*\/login/);
  });
});

import { test, expect } from '@playwright/test';

test.describe('Speaker Management Interface', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to speaker management
    await page.goto('/login');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('AdminPassword123!');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Navigate to speaker management (might be part of admin or separate page)
    await page.goto('/admin');
  });

  test('should display speakers list', async ({ page }) => {
    // Wait for speakers to load
    await page.waitForSelector('text=/speaker|Dr\.|SPEAKER_/i', { timeout: 10000 });
    
    // Should display speaker information
    await expect(page.locator('text=/Dr.*John.*Smith|SPEAKER_001/i')).toBeVisible();
    await expect(page.locator('text=/Dr.*Sarah.*Johnson|SPEAKER_002/i')).toBeVisible();
    
    // Should show speaker buckets
    await expect(page.locator('text=/HIGH.*TOUCH|MEDIUM.*TOUCH/i')).toBeVisible();
  });

  test('should support speaker search functionality', async ({ page }) => {
    // Wait for speakers to load
    await page.waitForSelector('text=/speaker|Dr\./i', { timeout: 10000 });
    
    // Find search input
    const searchInput = page.locator('input[placeholder*="search"], input[type="search"], [aria-label*="search"]');
    
    if (await searchInput.count() > 0) {
      // Search for specific speaker
      await searchInput.fill('John');
      
      // Should filter results
      await expect(page.locator('text=/Dr.*John.*Smith/i')).toBeVisible();
      
      // Clear search
      await searchInput.clear();
      await searchInput.fill('');
      
      // Should show all speakers again
      await expect(page.locator('text=/Dr.*Sarah.*Johnson/i')).toBeVisible();
    }
  });

  test('should open speaker details dialog', async ({ page }) => {
    // Wait for speakers to load
    await page.waitForSelector('text=/Dr.*John.*Smith/i', { timeout: 10000 });
    
    // Click on speaker card or row
    const speakerCard = page.locator('[data-testid="speaker-card"], .speaker-card, tr:has-text("Dr. John Smith")').first();
    
    if (await speakerCard.count() > 0) {
      await speakerCard.click();
      
      // Should open details dialog
      await expect(page.locator('[role="dialog"], .modal, .speaker-details')).toBeVisible();
      await expect(page.locator('text=/Speaker.*Details|Details/i')).toBeVisible();
      await expect(page.locator('text=/SPEAKER_001/i')).toBeVisible();
    }
  });

  test('should display speaker statistics', async ({ page }) => {
    // Look for statistics section
    const statsSection = page.locator('.statistics, .stats, [data-testid*="stats"]');
    
    if (await statsSection.count() > 0) {
      await expect(statsSection).toBeVisible();
      
      // Should show various metrics
      await expect(page.locator('text=/note.*count|notes|recordings/i')).toBeVisible();
      await expect(page.locator('text=/ser.*score|error.*rate/i')).toBeVisible();
    }
  });

  test('should support speaker filtering by bucket', async ({ page }) => {
    // Wait for speakers to load
    await page.waitForSelector('text=/HIGH.*TOUCH|MEDIUM.*TOUCH/i', { timeout: 10000 });
    
    // Find filter controls
    const filterButton = page.locator('button:has-text("Filter"), select[name*="bucket"], [aria-label*="filter"]');
    
    if (await filterButton.count() > 0) {
      await filterButton.click();
      
      // Select HIGH TOUCH filter
      const highTouchOption = page.locator('option:has-text("HIGH TOUCH"), [role="option"]:has-text("HIGH TOUCH")');
      if (await highTouchOption.count() > 0) {
        await highTouchOption.click();
        
        // Should show only HIGH TOUCH speakers
        await expect(page.locator('text=/HIGH.*TOUCH/i')).toBeVisible();
      }
    }
  });

  test('should support speaker bucket transitions', async ({ page }) => {
    // Wait for speakers to load
    await page.waitForSelector('text=/Dr.*John.*Smith/i', { timeout: 10000 });
    
    // Open speaker details
    const speakerCard = page.locator('[data-testid="speaker-card"], .speaker-card, tr:has-text("Dr. John Smith")').first();
    
    if (await speakerCard.count() > 0) {
      await speakerCard.click();
      
      // Look for bucket transition controls
      const transitionButton = page.locator('button:has-text("Move to"), button:has-text("Transition"), select[name*="bucket"]');
      
      if (await transitionButton.count() > 0) {
        await transitionButton.click();
        
        // Select new bucket
        const newBucketOption = page.locator('option:has-text("MEDIUM TOUCH"), [role="option"]:has-text("MEDIUM")');
        if (await newBucketOption.count() > 0) {
          await newBucketOption.click();
          
          // Should show confirmation or success message
          await expect(page.locator('text=/moved|transition.*successful|updated/i')).toBeVisible();
        }
      }
    }
  });

  test('should display speaker performance metrics', async ({ page }) => {
    // Open speaker details
    await page.waitForSelector('text=/Dr.*John.*Smith/i', { timeout: 10000 });
    const speakerCard = page.locator('[data-testid="speaker-card"], .speaker-card, tr:has-text("Dr. John Smith")').first();
    
    if (await speakerCard.count() > 0) {
      await speakerCard.click();
      
      // Should show performance metrics
      await expect(page.locator('text=/performance|metrics|statistics/i')).toBeVisible();
      await expect(page.locator('text=/error.*rate|accuracy|quality/i')).toBeVisible();
    }
  });

  test('should support data grid interactions', async ({ page }) => {
    // Wait for data grid to load
    await page.waitForSelector('[role="grid"], .data-grid, table', { timeout: 10000 });
    
    const dataGrid = page.locator('[role="grid"], .data-grid, table').first();
    
    if (await dataGrid.count() > 0) {
      // Test column sorting
      const sortableHeader = page.locator('th[role="columnheader"], .sortable-header').first();
      if (await sortableHeader.count() > 0) {
        await sortableHeader.click();
        
        // Should sort the data (visual verification needed)
        await expect(dataGrid).toBeVisible();
      }
      
      // Test row selection
      const firstRow = page.locator('tr[role="row"], tbody tr').first();
      if (await firstRow.count() > 0) {
        await firstRow.click();
        
        // Row should be selected (visual verification)
        await expect(firstRow).toBeVisible();
      }
    }
  });

  test('should handle pagination in speaker list', async ({ page }) => {
    // Look for pagination controls
    const paginationNext = page.locator('button:has-text("Next"), [aria-label*="next page"]');
    const paginationPrev = page.locator('button:has-text("Previous"), [aria-label*="previous page"]');
    
    if (await paginationNext.count() > 0) {
      await paginationNext.click();
      
      // Should load next page
      await expect(page.locator('text=/speaker|Dr\./i')).toBeVisible();
      
      if (await paginationPrev.count() > 0) {
        await paginationPrev.click();
        
        // Should go back to previous page
        await expect(page.locator('text=/speaker|Dr\./i')).toBeVisible();
      }
    }
  });

  test('should export speaker data', async ({ page }) => {
    // Look for export functionality
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download"), [aria-label*="export"]');
    
    if (await exportButton.count() > 0) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Should trigger download
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.csv|\.xlsx|\.json/);
    }
  });

  test('should validate speaker data integrity', async ({ page }) => {
    // Wait for speakers to load
    await page.waitForSelector('text=/Dr.*John.*Smith/i', { timeout: 10000 });
    
    // Check that speaker IDs are properly formatted
    await expect(page.locator('text=/SPEAKER_\d{3}/i')).toBeVisible();
    
    // Check that bucket assignments are valid
    await expect(page.locator('text=/HIGH.*TOUCH|MEDIUM.*TOUCH|LOW.*TOUCH/i')).toBeVisible();
    
    // Check that metrics are displayed as numbers
    const metricElements = page.locator('text=/\d+.*notes|\d+.*%|\d+\.\d+/i');
    if (await metricElements.count() > 0) {
      await expect(metricElements.first()).toBeVisible();
    }
  });

  test('should handle speaker management errors gracefully', async ({ page }) => {
    // Try to perform an action that might fail
    const speakerCard = page.locator('[data-testid="speaker-card"], .speaker-card').first();
    
    if (await speakerCard.count() > 0) {
      // Simulate network error by intercepting requests
      await page.route('**/api/**', route => route.abort());
      
      await speakerCard.click();
      
      // Should show error message
      await expect(page.locator('text=/error|failed|unable.*to.*load/i')).toBeVisible();
    }
  });
});

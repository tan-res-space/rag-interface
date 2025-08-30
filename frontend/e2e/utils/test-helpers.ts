import { Page, expect } from '@playwright/test';

/**
 * Common test utilities for Playwright E2E tests
 */

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Login with provided credentials
   */
  async login(username: string = 'admin', password: string = 'AdminPassword123!') {
    await this.page.goto('/login');
    await this.page.locator('input[name="username"]').fill(username);
    await this.page.locator('input[name="password"]').fill(password);
    await this.page.locator('button[type="submit"]').click();
    await expect(this.page).toHaveURL(/.*\/dashboard/);
  }

  /**
   * Wait for loading to complete
   */
  async waitForLoading() {
    // Wait for loading spinners to disappear
    await this.page.waitForSelector('.loading, [data-testid="loading"]', { state: 'hidden', timeout: 10000 });
  }

  /**
   * Navigate to a specific page and wait for it to load
   */
  async navigateAndWait(path: string) {
    await this.page.goto(path);
    await this.waitForLoading();
  }

  /**
   * Fill form field by various selectors
   */
  async fillField(fieldName: string, value: string) {
    const selectors = [
      `input[name="${fieldName}"]`,
      `textarea[name="${fieldName}"]`,
      `select[name="${fieldName}"]`,
      `[aria-label*="${fieldName}" i]`,
      `[placeholder*="${fieldName}" i]`
    ];

    for (const selector of selectors) {
      const element = this.page.locator(selector);
      if (await element.count() > 0) {
        await element.fill(value);
        return;
      }
    }
    
    throw new Error(`Could not find field: ${fieldName}`);
  }

  /**
   * Click button by text or aria-label
   */
  async clickButton(buttonText: string) {
    const selectors = [
      `button:has-text("${buttonText}")`,
      `[role="button"]:has-text("${buttonText}")`,
      `button[aria-label*="${buttonText}" i]`,
      `[aria-label*="${buttonText}" i][role="button"]`
    ];

    for (const selector of selectors) {
      const element = this.page.locator(selector);
      if (await element.count() > 0) {
        await element.click();
        return;
      }
    }
    
    throw new Error(`Could not find button: ${buttonText}`);
  }

  /**
   * Wait for and verify success message
   */
  async expectSuccessMessage(message?: string) {
    const successSelectors = [
      'text=/success|successful|saved|submitted/i',
      '[role="alert"]:has-text(/success/i)',
      '.success-message, .alert-success'
    ];

    if (message) {
      await expect(this.page.locator(`text=/${message}/i`)).toBeVisible();
    } else {
      for (const selector of successSelectors) {
        const element = this.page.locator(selector);
        if (await element.count() > 0) {
          await expect(element).toBeVisible();
          return;
        }
      }
    }
  }

  /**
   * Wait for and verify error message
   */
  async expectErrorMessage(message?: string) {
    const errorSelectors = [
      'text=/error|failed|invalid|required/i',
      '[role="alert"]:has-text(/error/i)',
      '.error-message, .alert-error'
    ];

    if (message) {
      await expect(this.page.locator(`text=/${message}/i`)).toBeVisible();
    } else {
      for (const selector of errorSelectors) {
        const element = this.page.locator(selector);
        if (await element.count() > 0) {
          await expect(element).toBeVisible();
          return;
        }
      }
    }
  }

  /**
   * Select option from dropdown
   */
  async selectOption(selectName: string, optionValue: string) {
    const selectors = [
      `select[name="${selectName}"]`,
      `[aria-label*="${selectName}" i]`,
      `[data-testid*="${selectName}"]`
    ];

    for (const selector of selectors) {
      const element = this.page.locator(selector);
      if (await element.count() > 0) {
        await element.selectOption(optionValue);
        return;
      }
    }
    
    throw new Error(`Could not find select: ${selectName}`);
  }

  /**
   * Upload file to file input
   */
  async uploadFile(fileName: string, content: Buffer, mimeType: string) {
    const fileInput = this.page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: fileName,
      mimeType: mimeType,
      buffer: content
    });
  }

  /**
   * Take screenshot with timestamp
   */
  async takeScreenshot(name: string) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await this.page.screenshot({ 
      path: `screenshots/${name}-${timestamp}.png`,
      fullPage: true 
    });
  }

  /**
   * Check if element exists without throwing
   */
  async elementExists(selector: string): Promise<boolean> {
    return await this.page.locator(selector).count() > 0;
  }

  /**
   * Wait for network requests to complete
   */
  async waitForNetworkIdle() {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Simulate keyboard shortcuts
   */
  async pressShortcut(shortcut: string) {
    await this.page.keyboard.press(shortcut);
  }

  /**
   * Verify page accessibility basics
   */
  async checkBasicAccessibility() {
    // Check for h1
    await expect(this.page.locator('h1')).toHaveCount({ min: 1 });
    
    // Check for main landmark
    const main = this.page.locator('main, [role="main"]');
    if (await main.count() > 0) {
      await expect(main).toBeVisible();
    }
    
    // Check for navigation
    const nav = this.page.locator('nav, [role="navigation"]');
    if (await nav.count() > 0) {
      await expect(nav).toBeVisible();
    }
  }

  /**
   * Mock API responses for testing
   */
  async mockApiResponse(url: string, response: any) {
    await this.page.route(url, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  /**
   * Simulate network error
   */
  async simulateNetworkError(urlPattern: string) {
    await this.page.route(urlPattern, route => route.abort());
  }
}

/**
 * Test data generators
 */
export class TestData {
  static generateSpeaker(id: string = 'TEST_001') {
    return {
      speaker_id: id,
      name: `Test Speaker ${id}`,
      bucket: 'HIGH_TOUCH',
      note_count: 25,
      average_ser_score: 15.5,
      has_sufficient_data: true
    };
  }

  static generateValidationItem(id: string = '1') {
    return {
      id,
      original_asr_text: 'The patient has diabetis and high blod pressure.',
      rag_corrected_text: 'The patient has diabetes and high blood pressure.',
      final_reference_text: 'The patient has diabetes and high blood pressure.',
      confidence_score: 0.95
    };
  }

  static generateErrorReport() {
    return {
      text: 'The patient has diabetis and high blod pressure.',
      category: 'Medical Terminology',
      severity: 'High',
      description: 'Spelling error in medical terminology'
    };
  }
}

/**
 * Page Object Models
 */
export class LoginPage {
  constructor(private page: Page) {}

  async login(username: string, password: string) {
    await this.page.goto('/login');
    await this.page.locator('input[name="username"]').fill(username);
    await this.page.locator('input[name="password"]').fill(password);
    await this.page.locator('button[type="submit"]').click();
  }
}

export class DashboardPage {
  constructor(private page: Page) {}

  async navigateToErrorReporting() {
    await this.page.locator('a[href*="error-reporting"]').click();
  }

  async navigateToVerification() {
    await this.page.locator('a[href*="verification"]').click();
  }

  async navigateToAdmin() {
    await this.page.locator('a[href*="admin"]').click();
  }
}

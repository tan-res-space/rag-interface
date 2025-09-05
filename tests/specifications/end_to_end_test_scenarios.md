# End-to-End Test Scenarios
## Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**Version:** 2.0  
**Framework:** Playwright with TypeScript  
**Coverage:** Complete user workflows and business scenarios

---

## Test Suite Overview

This document specifies comprehensive end-to-end test scenarios covering complete user workflows for the quality-based speaker bucket management system.

---

## 1. Enhanced Error Reporting Workflow Tests

### 1.1 Complete Error Reporting Journey

#### Test Scenario: `E2E-ER-001: QA Personnel Complete Error Reporting with Enhanced Metadata`

**User Story:** As a QA personnel, I want to report a speaker-specific error with comprehensive metadata so that the error can be corrected in future drafts.

**Test Steps:**
```typescript
test('Complete error reporting workflow with enhanced metadata', async ({ page }) => {
  // Step 1: Navigate to Error Reporting
  await page.goto('/error-reporting');
  await expect(page.locator('h3')).toContainText('ASR Error Reporting System');
  
  // Step 2: Select Error Text
  await page.locator('[data-testid="selectable-text"]').dblclick();
  await expect(page.locator('text=1 selection')).toBeVisible();
  await page.click('button:has-text("Next")');
  
  // Step 3: Categorize Error
  await page.click('button:has-text("Medical Terminology")');
  await expect(page.locator('text=1 of 5 categories selected')).toBeVisible();
  await page.click('button:has-text("Next")');
  
  // Step 4: Provide Correction
  await page.fill('[placeholder="Enter the corrected text..."]', 'high blood pressure');
  await page.click('button:has-text("Next")');
  
  // Step 5: Enhanced Metadata Input
  // Core metadata
  await page.fill('[placeholder="e.g., speaker-456"]', 'demo-speaker-456');
  await page.fill('[placeholder="e.g., client-789"]', 'client-medical-center-789');
  
  // Quality-based bucket selection
  await page.click('[data-testid="bucket-type-selector"]');
  await page.click('text=Medium Touch');
  await expect(page.locator('text=⚙️ Medium Touch')).toBeVisible();
  
  // Audio quality assessment
  await page.selectOption('[data-testid="audio-quality"]', 'good');
  await page.selectOption('[data-testid="speaker-clarity"]', 'clear');
  await page.selectOption('[data-testid="background-noise"]', 'low');
  
  // Enhanced metadata fields
  await page.selectOption('[data-testid="number-of-speakers"]', 'one');
  await page.check('[data-testid="overlapping-speech-no"]');
  await page.check('[data-testid="requires-specialized-knowledge-yes"]');
  await page.fill('[data-testid="additional-notes"]', 
    'Complex medical terminology used throughout the transcript');
  
  await page.click('button:has-text("Next")');
  
  // Step 6: Review and Submit
  await expect(page.locator('text=Review & Submit')).toBeVisible();
  await expect(page.locator('text=demo-speaker-456')).toBeVisible();
  await expect(page.locator('text=Medium Touch')).toBeVisible();
  await expect(page.locator('text=Complex medical terminology')).toBeVisible();
  
  await page.click('button:has-text("Submit Error Report")');
  
  // Verify submission success
  await expect(page.locator('text=Error report submitted successfully')).toBeVisible();
  await expect(page.locator('[data-testid="error-id"]')).toBeVisible();
});
```

#### Test Scenario: `E2E-ER-002: Copy-Paste Restriction Validation`

**User Story:** As a system administrator, I want to ensure that QA personnel cannot copy and paste draft text to maintain security compliance.

**Test Steps:**
```typescript
test('Verify copy-paste restrictions are enforced', async ({ page }) => {
  await page.goto('/error-reporting');
  
  // Attempt to copy text from selectable area
  await page.locator('[data-testid="selectable-text"]').selectText();
  
  // Try to copy using keyboard shortcut
  await page.keyboard.press('Control+C');
  
  // Verify warning message appears
  await expect(page.locator('[data-testid="copy-warning"]')).toContainText(
    'Copy operation is not allowed for security compliance'
  );
  
  // Try to paste in correction field
  await page.fill('[placeholder="Enter the corrected text..."]', '');
  await page.keyboard.press('Control+V');
  
  // Verify paste is blocked
  await expect(page.locator('[placeholder="Enter the corrected text..."]')).toHaveValue('');
  await expect(page.locator('[data-testid="paste-warning"]')).toContainText(
    'Paste operation is not allowed'
  );
});
```

### 1.2 Bucket Type Selection and Validation

#### Test Scenario: `E2E-BT-001: Quality-Based Bucket Type Selection`

**Test Steps:**
```typescript
test('Quality-based bucket type selection and validation', async ({ page }) => {
  await page.goto('/error-reporting');
  
  // Navigate to metadata input step
  await completeErrorSelectionSteps(page);
  
  // Test bucket type dropdown
  await page.click('[data-testid="bucket-type-selector"]');
  
  // Verify all quality-based options are available
  await expect(page.locator('text=🎯 No Touch')).toBeVisible();
  await expect(page.locator('text=🔧 Low Touch')).toBeVisible();
  await expect(page.locator('text=⚙️ Medium Touch')).toBeVisible();
  await expect(page.locator('text=🛠️ High Touch')).toBeVisible();
  
  // Verify old progression-based options are not available
  await expect(page.locator('text=Beginner')).not.toBeVisible();
  await expect(page.locator('text=Intermediate')).not.toBeVisible();
  await expect(page.locator('text=Advanced')).not.toBeVisible();
  await expect(page.locator('text=Expert')).not.toBeVisible();
  
  // Select High Touch bucket
  await page.click('text=🛠️ High Touch');
  await expect(page.locator('[data-testid="bucket-description"]')).toContainText(
    'ASR draft is of low quality and significant corrections are required'
  );
});
```

---

## 2. Speaker History and Performance Tracking Tests

### 2.1 Speaker History Dashboard

#### Test Scenario: `E2E-SH-001: Complete Speaker History Viewing Workflow`

**User Story:** As a QA personnel, I want to view complete error history for a specific speaker to track their performance improvements.

**Test Steps:**
```typescript
test('Complete speaker history viewing workflow', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Navigate to speaker history section
  await page.click('[data-testid="speaker-history-tab"]');
  
  // Search for speaker
  await page.fill('[data-testid="speaker-search"]', 'speaker-123');
  await page.click('[data-testid="search-button"]');
  
  // Verify speaker profile loads
  await expect(page.locator('[data-testid="speaker-profile"]')).toBeVisible();
  await expect(page.locator('text=speaker-123')).toBeVisible();
  
  // Verify current bucket status
  await expect(page.locator('[data-testid="current-bucket"]')).toContainText('Medium Touch');
  
  // Verify performance metrics
  await expect(page.locator('[data-testid="total-errors"]')).toBeVisible();
  await expect(page.locator('[data-testid="rectification-rate"]')).toBeVisible();
  await expect(page.locator('[data-testid="quality-trend"]')).toBeVisible();
  
  // Verify bucket history timeline
  await expect(page.locator('[data-testid="bucket-history"]')).toBeVisible();
  await expect(page.locator('text=High Touch → Medium Touch')).toBeVisible();
  
  // Verify error history
  await expect(page.locator('[data-testid="error-history"]')).toBeVisible();
  await expect(page.locator('text=Medical Terminology')).toBeVisible();
  await expect(page.locator('text=Rectified')).toBeVisible();
  
  // Test date range filtering
  await page.fill('[data-testid="start-date"]', '2024-12-01');
  await page.fill('[data-testid="end-date"]', '2024-12-19');
  await page.click('[data-testid="apply-filter"]');
  
  // Verify filtered results
  await expect(page.locator('[data-testid="filtered-results"]')).toBeVisible();
});
```

### 2.2 Performance Trend Analysis

#### Test Scenario: `E2E-PT-001: Performance Trend Visualization`

**Test Steps:**
```typescript
test('Performance trend visualization and analysis', async ({ page }) => {
  await page.goto('/speakers/speaker-123/performance');
  
  // Verify performance charts load
  await expect(page.locator('[data-testid="error-count-chart"]')).toBeVisible();
  await expect(page.locator('[data-testid="bucket-progression-chart"]')).toBeVisible();
  await expect(page.locator('[data-testid="rectification-rate-chart"]')).toBeVisible();
  
  // Verify chart data points
  await expect(page.locator('[data-testid="chart-data-points"]')).toHaveCount(6); // 6 months
  
  // Test chart interactions
  await page.hover('[data-testid="chart-data-point-0"]');
  await expect(page.locator('[data-testid="chart-tooltip"]')).toBeVisible();
  await expect(page.locator('[data-testid="chart-tooltip"]')).toContainText('Error Count: 8');
  
  // Verify improvement indicators
  await expect(page.locator('[data-testid="improvement-rate"]')).toContainText('75%');
  await expect(page.locator('[data-testid="quality-consistency"]')).toContainText('85%');
  await expect(page.locator('[data-testid="confidence-score"]')).toContainText('78%');
});
```

---

## 3. Verification Workflow Tests

### 3.1 Job Retrieval and Verification

#### Test Scenario: `E2E-VF-001: Complete Verification Workflow`

**User Story:** As a QA personnel, I want to verify that reported errors have been rectified in subsequent drafts.

**Test Steps:**
```typescript
test('Complete verification workflow from job retrieval to completion', async ({ page }) => {
  await page.goto('/verification');
  
  // Step 1: Job Retrieval Criteria
  await page.fill('[data-testid="speaker-id"]', 'speaker-123');
  await page.fill('[data-testid="start-date"]', '2024-12-01');
  await page.fill('[data-testid="end-date"]', '2024-12-19');
  
  // Select error types to verify
  await page.check('[data-testid="medical-terminology"]');
  await page.check('[data-testid="pronunciation"]');
  
  await page.selectOption('[data-testid="max-jobs"]', '10');
  await page.click('[data-testid="pull-jobs-button"]');
  
  // Step 2: Verify jobs are retrieved
  await expect(page.locator('[data-testid="jobs-found"]')).toContainText('5 found');
  await expect(page.locator('[data-testid="job-list"]')).toBeVisible();
  
  // Step 3: Select jobs for verification
  await page.check('[data-testid="job-checkbox-0"]');
  await page.check('[data-testid="job-checkbox-1"]');
  await page.click('[data-testid="verify-selected-jobs"]');
  
  // Step 4: Side-by-side verification interface
  await expect(page.locator('[data-testid="original-draft"]')).toBeVisible();
  await expect(page.locator('[data-testid="corrected-draft"]')).toBeVisible();
  
  // Verify corrections are highlighted
  await expect(page.locator('[data-testid="correction-highlight"]')).toBeVisible();
  await expect(page.locator('text=hypertension → high blood pressure')).toBeVisible();
  
  // Step 5: Mark corrections as verified
  await page.check('[data-testid="correction-rectified"]');
  await page.fill('[data-testid="qa-comments"]', 
    'Medical terminology correction applied correctly');
  
  await page.click('[data-testid="mark-as-verified"]');
  
  // Step 6: Verify submission success
  await expect(page.locator('[data-testid="verification-success"]')).toBeVisible();
  await expect(page.locator('text=Verification completed successfully')).toBeVisible();
  
  // Step 7: Verify next job loads automatically
  await expect(page.locator('[data-testid="next-job-loaded"]')).toBeVisible();
});
```

### 3.2 Batch Verification Operations

#### Test Scenario: `E2E-BV-001: Batch Verification Workflow`

**Test Steps:**
```typescript
test('Batch verification of multiple corrections', async ({ page }) => {
  await page.goto('/verification');
  
  // Retrieve multiple jobs
  await setupJobRetrieval(page, 'speaker-123');
  
  // Select all jobs for batch verification
  await page.click('[data-testid="select-all-jobs"]');
  await expect(page.locator('[data-testid="selected-count"]')).toContainText('5 jobs selected');
  
  // Open batch verification interface
  await page.click('[data-testid="batch-verify-button"]');
  
  // Verify batch interface loads
  await expect(page.locator('[data-testid="batch-verification-interface"]')).toBeVisible();
  
  // Mark all corrections as rectified
  await page.click('[data-testid="mark-all-rectified"]');
  
  // Add batch comments
  await page.fill('[data-testid="batch-comments"]', 
    'All medical terminology corrections verified as rectified');
  
  // Submit batch verification
  await page.click('[data-testid="submit-batch-verification"]');
  
  // Verify batch completion
  await expect(page.locator('[data-testid="batch-success"]')).toBeVisible();
  await expect(page.locator('text=5 verifications completed')).toBeVisible();
});
```

---

## 4. Dashboard Analytics Tests

### 4.1 Bucket Distribution Dashboard

#### Test Scenario: `E2E-DA-001: Dashboard Analytics and Reporting`

**User Story:** As a system administrator, I want to monitor speaker distribution across quality buckets and system performance metrics.

**Test Steps:**
```typescript
test('Complete dashboard analytics and reporting workflow', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Verify bucket distribution chart loads
  await expect(page.locator('[data-testid="bucket-distribution-chart"]')).toBeVisible();
  
  // Verify all bucket types are represented
  await expect(page.locator('text=🎯 No Touch')).toBeVisible();
  await expect(page.locator('text=🔧 Low Touch')).toBeVisible();
  await expect(page.locator('text=⚙️ Medium Touch')).toBeVisible();
  await expect(page.locator('text=🛠️ High Touch')).toBeVisible();
  
  // Verify percentage calculations
  await expect(page.locator('[data-testid="no-touch-percentage"]')).toContainText('10%');
  await expect(page.locator('[data-testid="low-touch-percentage"]')).toContainText('30%');
  await expect(page.locator('[data-testid="medium-touch-percentage"]')).toContainText('40%');
  await expect(page.locator('[data-testid="high-touch-percentage"]')).toContainText('20%');
  
  // Verify performance metrics
  await expect(page.locator('[data-testid="total-errors"]')).toContainText('1,847');
  await expect(page.locator('[data-testid="rectification-rate"]')).toContainText('82%');
  await expect(page.locator('[data-testid="avg-time-to-fix"]')).toContainText('3.8 days');
  
  // Verify resource allocation metrics
  await expect(page.locator('[data-testid="mt-workload-distribution"]')).toBeVisible();
  await expect(page.locator('[data-testid="time-saved"]')).toContainText('127 hrs');
  
  // Test chart interactions
  await page.hover('[data-testid="bucket-chart-segment-medium"]');
  await expect(page.locator('[data-testid="chart-tooltip"]')).toContainText('Medium Touch: 500 speakers');
});
```

### 4.2 Enhanced Metadata Analytics

#### Test Scenario: `E2E-MA-001: Enhanced Metadata Analytics Dashboard`

**Test Steps:**
```typescript
test('Enhanced metadata analytics and insights', async ({ page }) => {
  await page.goto('/dashboard/metadata-analytics');
  
  // Verify enhanced metadata insights
  await expect(page.locator('[data-testid="specialized-knowledge-percentage"]')).toContainText('65%');
  await expect(page.locator('[data-testid="overlapping-speech-percentage"]')).toContainText('23%');
  await expect(page.locator('[data-testid="multi-speaker-percentage"]')).toContainText('18%');
  
  // Verify speaker count distribution
  await expect(page.locator('[data-testid="speaker-count-chart"]')).toBeVisible();
  await expect(page.locator('text=One Speaker')).toBeVisible();
  await expect(page.locator('text=Two Speakers')).toBeVisible();
  
  // Test filtering by enhanced metadata
  await page.selectOption('[data-testid="filter-specialized-knowledge"]', 'yes');
  await page.click('[data-testid="apply-filter"]');
  
  // Verify filtered results
  await expect(page.locator('[data-testid="filtered-results"]')).toBeVisible();
  await expect(page.locator('[data-testid="filter-count"]')).toContainText('specialized knowledge required');
});
```

---

## 5. Mobile Responsive Tests

### 5.1 Mobile Error Reporting

#### Test Scenario: `E2E-MR-001: Mobile Error Reporting Workflow`

**Test Steps:**
```typescript
test('Mobile error reporting workflow', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/error-reporting');
  
  // Verify mobile-optimized interface
  await expect(page.locator('[data-testid="mobile-stepper"]')).toBeVisible();
  await expect(page.locator('[data-testid="mobile-progress"]')).toBeVisible();
  
  // Test touch-optimized text selection
  await page.locator('[data-testid="selectable-text"]').tap();
  await page.touchscreen.tap(100, 200); // Start selection
  await page.touchscreen.tap(200, 200); // End selection
  
  await expect(page.locator('[data-testid="selection-info"]')).toBeVisible();
  
  // Test mobile form interactions
  await page.tap('button:has-text("Next")');
  await page.tap('button:has-text("Medical Terminology")');
  await page.tap('button:has-text("Next")');
  
  // Test mobile metadata input
  await page.fill('[data-testid="mobile-speaker-id"]', 'speaker-123');
  await page.selectOption('[data-testid="mobile-bucket-selector"]', 'medium_touch');
  
  // Verify mobile-optimized bucket display
  await expect(page.locator('[data-testid="mobile-bucket-status"]')).toBeVisible();
  await expect(page.locator('text=⚙️ Medium Touch')).toBeVisible();
});
```

---

## 6. Accessibility Tests

### 6.1 Screen Reader Compatibility

#### Test Scenario: `E2E-A11Y-001: Screen Reader Navigation`

**Test Steps:**
```typescript
test('Screen reader compatibility and keyboard navigation', async ({ page }) => {
  await page.goto('/error-reporting');
  
  // Test keyboard navigation
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'selectable-text');
  
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'next-button');
  
  // Test ARIA labels and descriptions
  await expect(page.locator('[data-testid="bucket-selector"]')).toHaveAttribute('aria-label');
  await expect(page.locator('[data-testid="metadata-form"]')).toHaveAttribute('aria-describedby');
  
  // Test form validation announcements
  await page.click('button:has-text("Submit")'); // Submit without required fields
  await expect(page.locator('[role="alert"]')).toBeVisible();
  await expect(page.locator('[role="alert"]')).toHaveAttribute('aria-live', 'polite');
});
```

---

## Test Configuration and Utilities

### Test Setup and Teardown
```typescript
// test-setup.ts
import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  // Setup test data before each test
  testData: async ({ page }, use) => {
    await setupTestDatabase();
    await seedTestData();
    await use({});
    await cleanupTestData();
  },
  
  // Authenticated page for QA user
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('[data-testid="username"]', 'qa-test-user');
    await page.fill('[data-testid="password"]', 'test-password');
    await page.click('[data-testid="login-button"]');
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    await use(page);
  }
});
```

### Helper Functions
```typescript
// test-helpers.ts
export async function completeErrorSelectionSteps(page: Page) {
  await page.locator('[data-testid="selectable-text"]').dblclick();
  await page.click('button:has-text("Next")');
  await page.click('button:has-text("Medical Terminology")');
  await page.click('button:has-text("Next")');
  await page.fill('[placeholder="Enter the corrected text..."]', 'corrected text');
  await page.click('button:has-text("Next")');
}

export async function setupJobRetrieval(page: Page, speakerId: string) {
  await page.fill('[data-testid="speaker-id"]', speakerId);
  await page.fill('[data-testid="start-date"]', '2024-12-01');
  await page.fill('[data-testid="end-date"]', '2024-12-19');
  await page.click('[data-testid="pull-jobs-button"]');
  await expect(page.locator('[data-testid="jobs-found"]')).toBeVisible();
}
```

### Test Execution
```bash
# Run all E2E tests
npx playwright test tests/e2e/

# Run specific test suites
npx playwright test tests/e2e/error-reporting.spec.ts
npx playwright test tests/e2e/speaker-history.spec.ts
npx playwright test tests/e2e/verification-workflow.spec.ts

# Run tests in different browsers
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Run mobile tests
npx playwright test --project=mobile-chrome
npx playwright test --project=mobile-safari

# Generate test report
npx playwright show-report
```

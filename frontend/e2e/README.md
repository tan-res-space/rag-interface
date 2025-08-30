# E2E Testing Framework with Playwright

This directory contains comprehensive end-to-end tests for the RAG Interface frontend application using Playwright.

## Overview

The test suite covers:
- **Authentication flows** - Login, logout, session management
- **Navigation and routing** - Page navigation, breadcrumbs, responsive design
- **MT Validation interface** - Text validation, rating, comments, keyboard shortcuts
- **Speaker Management** - CRUD operations, filtering, data grid interactions
- **Error Reporting** - Form submission, categorization, file uploads
- **Accessibility** - WCAG compliance, keyboard navigation, screen readers

## Test Structure

```
e2e/
├── auth.spec.ts              # Authentication and session tests
├── navigation.spec.ts        # Navigation and routing tests
├── mt-validation.spec.ts     # MT validation interface tests
├── speaker-management.spec.ts # Speaker management tests
├── error-reporting.spec.ts   # Error reporting interface tests
├── accessibility.spec.ts     # Accessibility compliance tests
├── utils/
│   └── test-helpers.ts       # Common utilities and page objects
└── README.md                 # This file
```

## Test Coverage

### 🔐 Authentication Tests (7 tests)
- Login page redirection for unauthenticated users
- Form validation for invalid credentials
- Successful login with valid credentials
- Logout functionality
- Session persistence across page refreshes
- Session expiration handling

### 🧭 Navigation Tests (12 tests)
- Dashboard navigation from root
- Navigation to all main pages (error reporting, verification, admin)
- 404 page handling for invalid routes
- Breadcrumb navigation
- Responsive mobile menu
- Active navigation highlighting
- Keyboard navigation support
- Browser back/forward navigation
- Page load performance

### ✅ MT Validation Tests (12 tests)
- Validation session interface display
- Loading and displaying validation items
- Navigation between validation items
- Keyboard shortcuts (arrow keys)
- Rating system interaction
- Comment submission
- Draft saving functionality
- Final feedback submission
- Session summary display
- Error handling
- Text selection and highlighting
- Progress persistence

### 👥 Speaker Management Tests (11 tests)
- Speaker list display
- Search functionality
- Speaker details dialog
- Statistics display
- Filtering by bucket
- Bucket transitions
- Performance metrics
- Data grid interactions (sorting, selection)
- Pagination
- Data export
- Error handling

### 📝 Error Reporting Tests (13 tests)
- Error reporting interface display
- Text selection for error reporting
- Error categorization by type
- Severity level setting
- Description and comment addition
- Form submission
- Required field validation
- Draft saving
- Text highlighting and annotation
- Error history display
- Filtering and search
- File attachments
- Multi-language support

### ♿ Accessibility Tests (13 tests)
- Proper heading hierarchy
- ARIA labels and roles
- Keyboard navigation
- Color contrast
- Form labels
- Screen reader announcements
- Focus management
- High contrast mode support
- Error announcements
- Zoom support (200%)
- Skip links
- Descriptive link text
- Reduced motion preferences

## Cross-Browser Testing

Tests run on multiple browsers and devices:
- **Desktop**: Chromium, Firefox, WebKit (Safari)
- **Mobile**: Chrome (Pixel 5), Safari (iPhone 12)

**Total: 350 tests across 6 browsers/devices**

## Running Tests

### Prerequisites
1. Node.js 20.19+ or 22.12+ (current limitation due to Vite)
2. Playwright browsers installed: `npx playwright install`

### Commands

```bash
# Run all tests
npm run test:e2e

# Run tests with UI mode (interactive)
npm run test:e2e:ui

# Run tests in headed mode (visible browser)
npm run test:e2e:headed

# Debug tests
npm run test:e2e:debug

# View test report
npm run test:e2e:report

# Run specific test file
npx playwright test auth.spec.ts

# Run specific test
npx playwright test --grep "should login successfully"

# Run tests on specific browser
npx playwright test --project=chromium
```

## Test Configuration

Key configuration in `playwright.config.ts`:
- **Parallel execution** for faster test runs
- **Retry on failure** (2 retries on CI)
- **Multiple reporters**: HTML, JSON, JUnit
- **Screenshots** on failure
- **Video recording** on failure
- **Trace collection** for debugging

## Test Utilities

The `utils/test-helpers.ts` file provides:
- **TestHelpers class**: Common actions like login, navigation, form filling
- **TestData class**: Test data generators for speakers, validation items
- **Page Object Models**: Reusable page interaction patterns

## Best Practices

1. **Robust Selectors**: Uses multiple selector strategies for reliability
2. **Wait Strategies**: Proper waiting for elements and network requests
3. **Error Handling**: Graceful handling of missing elements
4. **Accessibility**: Built-in accessibility checks
5. **Cross-Browser**: Tests work across different browsers
6. **Mobile Support**: Responsive design testing
7. **Performance**: Load time validation
8. **Maintainability**: Reusable utilities and page objects

## CI/CD Integration

The test suite is designed for CI/CD pipelines:
- **JUnit XML** output for test reporting
- **JSON results** for programmatic analysis
- **Screenshots and videos** for failure investigation
- **Parallel execution** for faster feedback
- **Retry logic** for flaky test handling

## Troubleshooting

### Common Issues

1. **Node.js Version**: Ensure Node.js 20.19+ for Vite compatibility
2. **Browser Installation**: Run `npx playwright install` if browsers missing
3. **System Dependencies**: Install system dependencies with `npx playwright install-deps`
4. **Port Conflicts**: Ensure port 5173 is available for dev server

### Debug Mode

Use debug mode for test development:
```bash
npm run test:e2e:debug
```

This opens Playwright Inspector for step-by-step debugging.

## Future Enhancements

- **Visual regression testing** with screenshot comparison
- **Performance testing** with Lighthouse integration
- **API mocking** for isolated frontend testing
- **Test data management** with fixtures
- **Custom assertions** for domain-specific validations

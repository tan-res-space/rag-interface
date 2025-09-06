# Comprehensive Error Handling System

This document describes the comprehensive error handling system implemented in the frontend application. The system provides user-friendly error messages with detailed technical information available on demand, covering all types of errors that can occur in the application.

## Overview

The error handling system consists of several interconnected components that work together to provide a seamless error experience:

1. **Global Error Handler** - Captures all types of errors
2. **Error Display Components** - Shows user-friendly messages and detailed information
3. **Redux State Management** - Manages error state and preferences
4. **Custom Hooks** - Provides easy access to error handling functionality
5. **Middleware** - Intercepts API and Redux errors
6. **Enhanced Error Boundary** - Handles React component errors

## Key Features

- ✅ **User-friendly error messages** with "Show Details" button
- ✅ **Collapsible error details panel** at bottom of screen
- ✅ **Comprehensive error context** (stack traces, user actions, environment)
- ✅ **Multiple error type support** (API, network, runtime, component, validation)
- ✅ **Copyable error details** for bug reporting
- ✅ **Auto-dismissal** for low-severity errors
- ✅ **Error severity levels** (low, medium, high, critical)
- ✅ **Development vs production** appropriate detail levels
- ✅ **Error logging** and debugging support

## Architecture

### Error Types

```typescript
type ErrorType = 'api' | 'runtime' | 'component' | 'validation' | 'network';
type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';
```

### Core Components

#### 1. GlobalErrorHandler Service
- Captures window errors and unhandled promise rejections
- Collects comprehensive error context
- Transforms errors into standardized AppError objects
- Integrates with Redux state management

#### 2. ErrorDisplay Component
- Shows user-friendly error messages
- Provides "Show Details" button
- Displays error type and severity
- Includes action buttons (dismiss, refresh, etc.)

#### 3. ErrorDetailsPanel Component
- Bottom-positioned collapsible panel
- Shows complete error information
- Includes stack traces, context, and debugging data
- Provides copy functionality

#### 4. ErrorProvider Component
- Orchestrates error display
- Manages error queue and active errors
- Handles auto-dismissal logic
- Integrates all error components

## Usage

### Basic Error Reporting

```typescript
import { useErrorHandler } from '@shared/hooks/useErrorHandler';

const MyComponent = () => {
  const { reportError, trackUserAction } = useErrorHandler();

  const handleSomething = () => {
    try {
      // Some operation that might fail
      riskyOperation();
    } catch (error) {
      trackUserAction('Failed to perform operation');
      reportError(error, 'runtime');
    }
  };
};
```

### API Error Handling

```typescript
import { useApiErrorHandler } from '@shared/hooks/useErrorHandler';

const MyComponent = () => {
  const { handleApiError } = useApiErrorHandler();

  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      handleApiError(error, '/api/data', 'GET');
    }
  };
};
```

### Validation Error Handling

```typescript
import { useValidationErrorHandler } from '@shared/hooks/useErrorHandler';

const MyForm = () => {
  const { handleValidationError } = useValidationErrorHandler();

  const validateForm = (formData) => {
    const errors = {};
    if (!formData.email) errors.email = 'Email is required';
    if (!formData.password) errors.password = 'Password is required';

    if (Object.keys(errors).length > 0) {
      handleValidationError(errors, 'loginForm', formData);
      return false;
    }
    return true;
  };
};
```

## Error Context

Each error includes comprehensive context information:

```typescript
interface ErrorContext {
  url: string;                    // Current page URL
  userAgent: string;              // Browser information
  userId?: string;                // Current user ID
  componentStack?: string;        // React component stack
  apiEndpoint?: string;           // Failed API endpoint
  statusCode?: number;            // HTTP status code
  userActions?: string[];         // Recent user actions
  environment?: {                 // Browser environment
    viewport: { width: number; height: number };
    platform: string;
    language: string;
    cookieEnabled: boolean;
    onLine: boolean;
  };
  additionalData?: Record<string, any>; // Custom context data
}
```

## Error Severity and Behavior

### Low Severity
- Validation errors
- Auto-dismissed after timeout
- Shown as notifications

### Medium Severity
- API errors
- Network errors
- Shown as dismissible alerts

### High Severity
- Runtime errors
- Component errors
- Persistent display until acknowledged

### Critical Severity
- System failures
- Cannot be dismissed
- Includes refresh button

## Configuration

### Error Display Preferences

```typescript
interface ErrorDisplayPreferences {
  showTechnicalDetailsInProduction: boolean;
  autoDismissLowSeverity: boolean;
  autoDismissTimeout: number;
}
```

### Global Error Handler Config

```typescript
interface ErrorHandlerConfig {
  captureWindowErrors: boolean;
  captureUnhandledRejections: boolean;
  captureConsoleErrors: boolean;
  maxErrorQueueSize: number;
  logToConsole: boolean;
  transformError?: (error: Error, context: Partial<ErrorContext>) => Partial<AppError>;
  filterError?: (error: Error) => boolean;
}
```

## Integration Points

### 1. App.tsx Integration
```typescript
function App() {
  return (
    <Provider store={store}>
      <ErrorBoundary>
        <ErrorProvider>
          <NotificationProvider>
            {/* Your app components */}
          </NotificationProvider>
        </ErrorProvider>
      </ErrorBoundary>
    </Provider>
  );
}
```

### 2. Redux Store Integration
```typescript
export const store = configureStore({
  // ... other config
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(errorHandlingMiddleware),
});
```

### 3. RTK Query Integration
The error handling middleware automatically intercepts RTK Query errors and reports them to the global error handler.

## Development Tools

### Error Test Component
A development-only component for testing different error scenarios:

```typescript
import ErrorTestComponent from '@shared/components/ErrorTestComponent';

// Use in development to test error handling
<ErrorTestComponent />
```

### Error Debugging
- All errors are logged to console in development
- Error details include complete stack traces
- User action history is tracked
- Error context is comprehensive

## Best Practices

1. **Always track user actions** before operations that might fail
2. **Use appropriate error types** for different scenarios
3. **Provide meaningful error messages** for users
4. **Include relevant context** in error reports
5. **Test error scenarios** during development
6. **Monitor error patterns** in production

## Error Recovery

The system provides several error recovery mechanisms:

- **Refresh button** for critical errors
- **Retry functionality** for API errors
- **Error dismissal** for non-critical errors
- **Automatic error clearing** on navigation
- **Error boundary fallbacks** for component errors

## Accessibility

- Error messages use appropriate ARIA labels
- Color coding follows accessibility guidelines
- Keyboard navigation is supported
- Screen reader compatible error announcements

/**
 * Test Utilities for Error Reporting Components
 * Provides common test setup, mocks, and helper functions
 */

import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import { configureStore, PreloadedState } from '@reduxjs/toolkit';
import type { 
  TextSelection, 
  ErrorCategory, 
  SimilarityResult, 
  ErrorMetadata, 
  ValidationError,
  SubmitErrorReportRequest 
} from '@domain/types';

// Mock store setup
export const createMockStore = (preloadedState?: PreloadedState<any>) => {
  return configureStore({
    reducer: {
      errorReporting: (state = {}, action) => state,
      auth: (state = { token: 'mock-token' }, action) => state,
    },
    preloadedState,
  });
};

// Theme setup
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      contrastText: '#ffffff',
    },
    success: {
      main: '#2e7d32',
    },
    warning: {
      main: '#ed6c02',
    },
    error: {
      main: '#d32f2f',
    },
  },
});

// Custom render function with providers
interface ExtendedRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  preloadedState?: PreloadedState<any>;
  store?: ReturnType<typeof createMockStore>;
}

export const renderWithProviders = (
  ui: React.ReactElement,
  {
    preloadedState = {},
    store = createMockStore(preloadedState),
    ...renderOptions
  }: ExtendedRenderOptions = {}
) => {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <BrowserRouter>
            {children}
          </BrowserRouter>
        </ThemeProvider>
      </Provider>
    );
  }
  
  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
};

// Mock data factories
export const createMockTextSelection = (overrides?: Partial<TextSelection>): TextSelection => ({
  selectionId: `selection-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  text: 'sample error text',
  startPosition: 10,
  endPosition: 27,
  confidence: 0.95,
  timestamp: Date.now(),
  ...overrides,
});

export const createMockErrorCategory = (overrides?: Partial<ErrorCategory>): ErrorCategory => ({
  id: 'test-category',
  name: 'Test Category',
  description: 'Test category description',
  isActive: true,
  ...overrides,
});

export const createMockSimilarityResult = (overrides?: Partial<SimilarityResult>): SimilarityResult => ({
  patternId: `pattern-${Date.now()}`,
  similarText: 'original error text',
  confidence: 0.95,
  frequency: 5,
  suggestedCorrection: 'corrected text',
  speakerIds: ['speaker-1'],
  category: 'pronunciation',
  ...overrides,
});

export const createMockErrorMetadata = (overrides?: Partial<ErrorMetadata>): ErrorMetadata => ({
  audioQuality: 'good',
  backgroundNoise: 'low',
  speakerClarity: 'clear',
  contextualNotes: 'Test notes',
  urgencyLevel: 'medium',
  speechRate: 5,
  confidenceRating: 3,
  contextualTags: [],
  hasMultipleSpeakers: false,
  hasOverlappingSpeech: false,
  requiresSpecializedKnowledge: false,
  ...overrides,
});

export const createMockValidationError = (overrides?: Partial<ValidationError>): ValidationError => ({
  field: 'testField',
  message: 'Test validation error',
  code: 'REQUIRED',
  ...overrides,
});

export const createMockErrorReport = (overrides?: Partial<SubmitErrorReportRequest>): SubmitErrorReportRequest => ({
  jobId: 'test-job-123',
  speakerId: 'test-speaker-456',
  textSelections: [createMockTextSelection()],
  selectedCategories: [createMockErrorCategory()],
  correctionText: 'corrected text',
  metadata: createMockErrorMetadata(),
  ...overrides,
});

// Mock API responses
export const mockApiResponses = {
  submitErrorReport: {
    success: {
      reportId: 'report-123',
      status: 'submitted',
      message: 'Error report submitted successfully',
    },
    error: {
      error: 'Validation failed',
      message: 'Please fix the validation errors',
      validationErrors: [
        createMockValidationError({ field: 'textSelections', message: 'At least one text selection is required' }),
      ],
    },
  },
  
  searchSimilarPatterns: {
    success: [
      createMockSimilarityResult(),
      createMockSimilarityResult({
        patternId: 'pattern-2',
        confidence: 0.87,
        suggestedCorrection: 'another correction',
      }),
    ],
    empty: [],
  },
  
  getErrorCategories: {
    success: [
      createMockErrorCategory({ id: 'pronunciation', name: 'Pronunciation' }),
      createMockErrorCategory({ id: 'grammar', name: 'Grammar' }),
      createMockErrorCategory({ 
        id: 'medical', 
        name: 'Medical Terminology', 
        parentCategory: 'pronunciation' 
      }),
    ],
  },
};

// Mock browser APIs
export const setupBrowserMocks = () => {
  // Mock speech recognition
  const mockSpeechRecognition = {
    start: jest.fn(),
    stop: jest.fn(),
    abort: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    continuous: false,
    interimResults: false,
    lang: 'en-US',
    onstart: null,
    onresult: null,
    onerror: null,
    onend: null,
  };

  global.webkitSpeechRecognition = jest.fn(() => mockSpeechRecognition);
  global.SpeechRecognition = jest.fn(() => mockSpeechRecognition);

  // Mock speech synthesis
  const mockSpeechSynthesis = {
    speak: jest.fn(),
    cancel: jest.fn(),
    pause: jest.fn(),
    resume: jest.fn(),
    getVoices: jest.fn(() => []),
  };

  global.speechSynthesis = mockSpeechSynthesis;
  global.SpeechSynthesisUtterance = jest.fn();

  // Mock clipboard
  const mockClipboard = {
    writeText: jest.fn(() => Promise.resolve()),
    readText: jest.fn(() => Promise.resolve('mock clipboard text')),
  };

  Object.assign(navigator, {
    clipboard: mockClipboard,
  });

  // Mock window.getSelection
  const mockSelection = {
    toString: jest.fn(() => ''),
    rangeCount: 0,
    getRangeAt: jest.fn(),
    removeAllRanges: jest.fn(),
    addRange: jest.fn(),
  };

  Object.defineProperty(window, 'getSelection', {
    writable: true,
    value: jest.fn(() => mockSelection),
  });

  // Mock matchMedia for responsive design tests
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });

  return {
    speechRecognition: mockSpeechRecognition,
    speechSynthesis: mockSpeechSynthesis,
    clipboard: mockClipboard,
    selection: mockSelection,
  };
};

// Test helpers for text selection simulation
export const simulateTextSelection = (text: string, startOffset: number, endOffset: number) => {
  const mockSelection = {
    toString: () => text.slice(startOffset, endOffset),
    rangeCount: 1,
    getRangeAt: () => ({
      startOffset,
      endOffset,
    }),
    removeAllRanges: jest.fn(),
  };

  (window.getSelection as jest.Mock).mockReturnValue(mockSelection);
  return mockSelection;
};

// Test helpers for form validation
export const expectFormValidation = {
  toBeValid: (form: HTMLElement) => {
    const submitButton = form.querySelector('button[type="submit"]') as HTMLButtonElement;
    expect(submitButton).not.toBeDisabled();
  },
  
  toBeInvalid: (form: HTMLElement) => {
    const submitButton = form.querySelector('button[type="submit"]') as HTMLButtonElement;
    expect(submitButton).toBeDisabled();
  },
  
  toShowError: (form: HTMLElement, errorMessage: string) => {
    expect(form).toHaveTextContent(errorMessage);
  },
};

// Test helpers for accessibility
export const expectAccessibility = {
  toHaveProperLabels: (element: HTMLElement) => {
    const inputs = element.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      const label = element.querySelector(`label[for="${input.id}"]`) ||
                   input.getAttribute('aria-label') ||
                   input.getAttribute('aria-labelledby');
      expect(label).toBeTruthy();
    });
  },
  
  toSupportKeyboardNavigation: async (element: HTMLElement, userEvent: any) => {
    await userEvent.tab();
    const focusedElement = document.activeElement;
    expect(element.contains(focusedElement)).toBe(true);
  },
  
  toHaveProperRoles: (element: HTMLElement) => {
    const interactiveElements = element.querySelectorAll('button, input, select, textarea, [role]');
    interactiveElements.forEach(el => {
      const role = el.getAttribute('role') || el.tagName.toLowerCase();
      expect(['button', 'textbox', 'combobox', 'checkbox', 'radio', 'slider'].some(validRole => 
        role.includes(validRole)
      )).toBe(true);
    });
  },
};

// Performance testing helpers
export const measurePerformance = {
  renderTime: async (renderFn: () => void) => {
    const start = performance.now();
    renderFn();
    const end = performance.now();
    return end - start;
  },
  
  interactionTime: async (interactionFn: () => Promise<void>) => {
    const start = performance.now();
    await interactionFn();
    const end = performance.now();
    return end - start;
  },
};

// Cleanup helpers
export const cleanup = {
  browserMocks: () => {
    jest.restoreAllMocks();
  },
  
  timers: () => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  },
  
  all: () => {
    cleanup.browserMocks();
    cleanup.timers();
  },
};

// Export commonly used test constants
export const TEST_CONSTANTS = {
  SAMPLE_DOCUMENT_TEXT: 'The patient has a history of hypertension and diabetes. The doctor prescribed medication for the condition.',
  SAMPLE_ERROR_TEXT: 'hypertension',
  SAMPLE_CORRECTION: 'high blood pressure',
  SAMPLE_CATEGORIES: ['pronunciation', 'grammar', 'medical'],
  DEBOUNCE_DELAY: 500,
  ANIMATION_DELAY: 300,
};

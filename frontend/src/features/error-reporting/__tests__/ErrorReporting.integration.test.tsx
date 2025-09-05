/**
 * Error Reporting Integration Tests
 * Tests the complete error reporting workflow from start to finish
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import { ErrorReportingForm } from '../components/ErrorReportingForm';
import type { ErrorCategory, SimilarityResult, SubmitErrorReportRequest } from '@domain/types';

const theme = createTheme();

// Mock store setup
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      errorReporting: (state = initialState, action) => state,
    },
    preloadedState: {
      errorReporting: initialState,
    },
  });
};

const renderWithProviders = (
  component: React.ReactElement,
  { store = createMockStore(), ...renderOptions } = {}
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
  
  return { store, ...render(component, { wrapper: Wrapper, ...renderOptions }) };
};

// Mock data
const mockCategories: ErrorCategory[] = [
  {
    id: 'pronunciation',
    name: 'Pronunciation',
    description: 'Pronunciation errors',
    isActive: true,
  },
  {
    id: 'grammar',
    name: 'Grammar',
    description: 'Grammar errors',
    isActive: true,
  },
  {
    id: 'medical',
    name: 'Medical Terminology',
    description: 'Medical term errors',
    isActive: true,
    parentCategory: 'pronunciation',
  },
];

const mockSimilarPatterns: SimilarityResult[] = [
  {
    patternId: 'pattern-1',
    similarText: 'original error text',
    confidence: 0.95,
    frequency: 5,
    suggestedCorrection: 'corrected text suggestion',
    speakerIds: ['speaker-1'],
    category: 'pronunciation',
  },
];

const documentText = 'The patient has a history of hypertension and diabetes. The doctor prescribed medication for the condition.';

// Mock APIs
beforeAll(() => {
  // Mock speech recognition
  global.webkitSpeechRecognition = jest.fn(() => ({
    start: jest.fn(),
    stop: jest.fn(),
    abort: jest.fn(),
    continuous: false,
    interimResults: false,
    lang: 'en-US',
    onstart: null,
    onresult: null,
    onerror: null,
    onend: null,
  }));

  // Mock speech synthesis
  global.speechSynthesis = {
    speak: jest.fn(),
    cancel: jest.fn(),
    pause: jest.fn(),
    resume: jest.fn(),
    getVoices: jest.fn(() => []),
  };
  global.SpeechSynthesisUtterance = jest.fn();

  // Mock clipboard
  Object.assign(navigator, {
    clipboard: {
      writeText: jest.fn(() => Promise.resolve()),
    },
  });

  // Mock window.getSelection
  Object.defineProperty(window, 'getSelection', {
    writable: true,
    value: jest.fn(),
  });
});

describe('Error Reporting Integration', () => {
  const defaultProps = {
    jobId: 'job-123',
    speakerId: 'speaker-456',
    documentText,
    onSubmit: jest.fn(),
    onCancel: jest.fn(),
    categories: mockCategories,
    similarPatterns: mockSimilarPatterns,
    onSimilaritySearch: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Complete Error Reporting Workflow', () => {
    it('completes the full error reporting workflow', async () => {
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      
      renderWithProviders(
        <ErrorReportingForm 
          {...defaultProps}
          onSubmit={onSubmit}
        />
      );

      // Step 1: Text Selection
      expect(screen.getByText('Select Error Text')).toBeInTheDocument();
      expect(screen.getByText(documentText)).toBeInTheDocument();

      // Simulate text selection
      const textContainer = screen.getByTestId('selectable-text');
      
      const mockSelection = {
        toString: () => 'hypertension',
        rangeCount: 1,
        getRangeAt: () => ({
          startOffset: 32,
          endOffset: 44,
        }),
        removeAllRanges: jest.fn(),
      };
      
      (window.getSelection as jest.Mock).mockReturnValue(mockSelection);
      
      fireEvent.mouseDown(textContainer);
      fireEvent.mouseUp(textContainer);

      // Wait for selection to be processed and Next button to be enabled
      await waitFor(() => {
        const nextButton = screen.getByText('Next');
        expect(nextButton).not.toBeDisabled();
      });

      // Navigate to Step 2: Categorization
      const nextButton1 = screen.getByText('Next');
      await user.click(nextButton1);

      // Step 2: Error Categorization
      expect(screen.getByText('Error Categories')).toBeInTheDocument();
      
      // Select a category
      const pronunciationCategory = screen.getByText('Pronunciation');
      await user.click(pronunciationCategory);

      // Wait for category selection and Next button to be enabled
      await waitFor(() => {
        const nextButton = screen.getByText('Next');
        expect(nextButton).not.toBeDisabled();
      });

      // Navigate to Step 3: Correction
      const nextButton2 = screen.getByText('Next');
      await user.click(nextButton2);

      // Step 3: Correction Input
      expect(screen.getByLabelText(/corrected text/i)).toBeInTheDocument();
      
      // Enter correction text
      const correctionInput = screen.getByRole('textbox', { name: /corrected text/i });
      await user.type(correctionInput, 'high blood pressure');

      // Wait for correction text and Next button to be enabled
      await waitFor(() => {
        const nextButton = screen.getByText('Next');
        expect(nextButton).not.toBeDisabled();
      });

      // Navigate to Step 4: Metadata
      const nextButton3 = screen.getByText('Next');
      await user.click(nextButton3);

      // Step 4: Metadata Input
      expect(screen.getByText('Contextual Information')).toBeInTheDocument();
      
      // Metadata is optional, so Next should be enabled
      await waitFor(() => {
        const nextButton = screen.getByText('Next');
        expect(nextButton).not.toBeDisabled();
      });

      // Navigate to Step 5: Review
      const nextButton4 = screen.getByText('Next');
      await user.click(nextButton4);

      // Step 5: Review & Submit
      expect(screen.getByText('Review Your Error Report')).toBeInTheDocument();
      expect(screen.getByText('"hypertension"')).toBeInTheDocument();
      expect(screen.getByText('Pronunciation')).toBeInTheDocument();
      expect(screen.getByText('"high blood pressure"')).toBeInTheDocument();

      // Submit the form
      const submitButton = screen.getByText('Submit Report');
      expect(submitButton).not.toBeDisabled();
      await user.click(submitButton);

      // Verify onSubmit was called with correct data
      expect(onSubmit).toHaveBeenCalledWith({
        jobId: 'job-123',
        speakerId: 'speaker-456',
        textSelections: expect.arrayContaining([
          expect.objectContaining({
            text: 'hypertension',
            startPosition: 32,
            endPosition: 44,
          }),
        ]),
        selectedCategories: expect.arrayContaining([
          expect.objectContaining({
            id: 'pronunciation',
            name: 'Pronunciation',
          }),
        ]),
        correctionText: 'high blood pressure',
        metadata: expect.objectContaining({
          audioQuality: 'good',
          backgroundNoise: 'low',
          speakerClarity: 'clear',
          urgencyLevel: 'medium',
        }),
      });
    });

    it('handles workflow with multiple text selections', async () => {
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      
      renderWithProviders(
        <ErrorReportingForm 
          {...defaultProps}
          onSubmit={onSubmit}
        />
      );

      // Make first text selection
      const textContainer = screen.getByTestId('selectable-text');
      
      const mockSelection1 = {
        toString: () => 'hypertension',
        rangeCount: 1,
        getRangeAt: () => ({
          startOffset: 32,
          endOffset: 44,
        }),
        removeAllRanges: jest.fn(),
      };
      
      (window.getSelection as jest.Mock).mockReturnValue(mockSelection1);
      
      fireEvent.mouseDown(textContainer);
      fireEvent.mouseUp(textContainer);

      // Make second text selection with Ctrl key
      const mockSelection2 = {
        toString: () => 'diabetes',
        rangeCount: 1,
        getRangeAt: () => ({
          startOffset: 49,
          endOffset: 57,
        }),
        removeAllRanges: jest.fn(),
      };
      
      (window.getSelection as jest.Mock).mockReturnValue(mockSelection2);
      
      fireEvent.mouseDown(textContainer, { ctrlKey: true });
      fireEvent.mouseUp(textContainer, { ctrlKey: true });

      // Should have multiple selections
      await waitFor(() => {
        expect(screen.getByText('2 selections')).toBeInTheDocument();
      });

      // Continue through workflow...
      const nextButton = screen.getByText('Next');
      await user.click(nextButton);

      // Select categories
      const pronunciationCategory = screen.getByText('Pronunciation');
      await user.click(pronunciationCategory);

      const grammarCategory = screen.getByText('Grammar');
      await user.click(grammarCategory);

      // Continue to correction
      await waitFor(async () => {
        const nextButton = screen.getByText('Next');
        if (!nextButton.disabled) {
          await user.click(nextButton);
        }
      });

      // Enter correction
      const correctionInput = screen.getByRole('textbox', { name: /corrected text/i });
      await user.type(correctionInput, 'high blood pressure and type 2 diabetes');

      // Complete workflow
      await waitFor(async () => {
        const nextButton = screen.getByText('Next');
        if (!nextButton.disabled) {
          await user.click(nextButton);
        }
      });

      await waitFor(async () => {
        const nextButton = screen.getByText('Next');
        if (!nextButton.disabled) {
          await user.click(nextButton);
        }
      });

      // Submit
      const submitButton = screen.getByText('Submit Report');
      await user.click(submitButton);

      // Verify multiple selections were submitted
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          textSelections: expect.arrayContaining([
            expect.objectContaining({ text: 'hypertension' }),
            expect.objectContaining({ text: 'diabetes' }),
          ]),
          selectedCategories: expect.arrayContaining([
            expect.objectContaining({ name: 'Pronunciation' }),
            expect.objectContaining({ name: 'Grammar' }),
          ]),
        })
      );
    });

    it('handles workflow with AI suggestions', async () => {
      const user = userEvent.setup();
      const onSimilaritySearch = jest.fn();
      
      renderWithProviders(
        <ErrorReportingForm 
          {...defaultProps}
          onSimilaritySearch={onSimilaritySearch}
          similarPatterns={mockSimilarPatterns}
        />
      );

      // Navigate to correction step
      const textContainer = screen.getByTestId('selectable-text');
      
      const mockSelection = {
        toString: () => 'hypertension',
        rangeCount: 1,
        getRangeAt: () => ({
          startOffset: 32,
          endOffset: 44,
        }),
        removeAllRanges: jest.fn(),
      };
      
      (window.getSelection as jest.Mock).mockReturnValue(mockSelection);
      
      fireEvent.mouseDown(textContainer);
      fireEvent.mouseUp(textContainer);

      await waitFor(async () => {
        const nextButton = screen.getByText('Next');
        if (!nextButton.disabled) {
          await user.click(nextButton);
        }
      });

      // Select category
      const pronunciationCategory = screen.getByText('Pronunciation');
      await user.click(pronunciationCategory);

      await waitFor(async () => {
        const nextButton = screen.getByText('Next');
        if (!nextButton.disabled) {
          await user.click(nextButton);
        }
      });

      // On correction step, type text to trigger similarity search
      const correctionInput = screen.getByRole('textbox', { name: /corrected text/i });
      await user.type(correctionInput, 'high blood');

      // Wait for similarity search to be triggered
      await waitFor(() => {
        expect(onSimilaritySearch).toHaveBeenCalledWith('high blood');
      }, { timeout: 1000 });

      // Show AI suggestions
      const aiButton = screen.getByLabelText(/show ai suggestions/i);
      await user.click(aiButton);

      // Should show similarity results
      expect(screen.getByText('AI Suggestions:')).toBeInTheDocument();
      expect(screen.getByText('corrected text suggestion')).toBeInTheDocument();

      // Click on suggestion
      const suggestion = screen.getByText('corrected text suggestion');
      await user.click(suggestion);

      // Should apply the suggestion
      expect(correctionInput).toHaveValue('corrected text suggestion');
    });

    it('handles workflow cancellation', async () => {
      const user = userEvent.setup();
      const onCancel = jest.fn();
      
      renderWithProviders(
        <ErrorReportingForm 
          {...defaultProps}
          onCancel={onCancel}
        />
      );

      // Make some progress in the form
      const textContainer = screen.getByTestId('selectable-text');
      
      const mockSelection = {
        toString: () => 'hypertension',
        rangeCount: 1,
        getRangeAt: () => ({
          startOffset: 32,
          endOffset: 44,
        }),
        removeAllRanges: jest.fn(),
      };
      
      (window.getSelection as jest.Mock).mockReturnValue(mockSelection);
      
      fireEvent.mouseDown(textContainer);
      fireEvent.mouseUp(textContainer);

      // Cancel the form
      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      expect(onCancel).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('handles submission errors gracefully', async () => {
      const user = userEvent.setup();
      const onSubmit = jest.fn().mockRejectedValue(new Error('Submission failed'));
      
      renderWithProviders(
        <ErrorReportingForm 
          {...defaultProps}
          onSubmit={onSubmit}
        />
      );

      // Complete a minimal workflow
      const textContainer = screen.getByTestId('selectable-text');
      
      const mockSelection = {
        toString: () => 'test',
        rangeCount: 1,
        getRangeAt: () => ({
          startOffset: 0,
          endOffset: 4,
        }),
        removeAllRanges: jest.fn(),
      };
      
      (window.getSelection as jest.Mock).mockReturnValue(mockSelection);
      
      fireEvent.mouseDown(textContainer);
      fireEvent.mouseUp(textContainer);

      // Navigate through steps quickly
      for (let i = 0; i < 4; i++) {
        await waitFor(async () => {
          const nextButton = screen.getByText('Next');
          if (!nextButton.disabled) {
            await user.click(nextButton);
          }
        });

        if (i === 0) {
          // Select category on step 2
          const pronunciationCategory = screen.getByText('Pronunciation');
          await user.click(pronunciationCategory);
        } else if (i === 1) {
          // Enter correction on step 3
          const correctionInput = screen.getByRole('textbox', { name: /corrected text/i });
          await user.type(correctionInput, 'corrected');
        }
      }

      // Try to submit
      const submitButton = screen.getByText('Submit Report');
      await user.click(submitButton);

      // Should handle error gracefully (not crash)
      expect(onSubmit).toHaveBeenCalled();
    });

    it('shows validation errors when form is invalid', () => {
      const validationErrors = [
        {
          field: 'textSelections',
          message: 'At least one text selection is required',
          code: 'REQUIRED',
        },
        {
          field: 'correctionText',
          message: 'Correction text cannot be empty',
          code: 'REQUIRED',
        },
      ];

      renderWithProviders(
        <ErrorReportingForm 
          {...defaultProps}
          errors={validationErrors}
        />
      );

      expect(screen.getByText('Please fix the following errors:')).toBeInTheDocument();
      expect(screen.getByText('At least one text selection is required')).toBeInTheDocument();
      expect(screen.getByText('Correction text cannot be empty')).toBeInTheDocument();
    });
  });

  describe('Accessibility Integration', () => {
    it('maintains focus management throughout workflow', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<ErrorReportingForm {...defaultProps} />);

      // Tab through the form
      await user.tab();
      
      // Should focus on first interactive element
      const focusedElement = document.activeElement;
      expect(focusedElement).toBeInTheDocument();
      expect(focusedElement?.tagName).toBe('DIV'); // Text selection container
    });

    it('provides proper ARIA announcements', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<ErrorReportingForm {...defaultProps} />);

      // Make text selection
      const textContainer = screen.getByTestId('selectable-text');
      
      const mockSelection = {
        toString: () => 'test',
        rangeCount: 1,
        getRangeAt: () => ({
          startOffset: 0,
          endOffset: 4,
        }),
        removeAllRanges: jest.fn(),
      };
      
      (window.getSelection as jest.Mock).mockReturnValue(mockSelection);
      
      fireEvent.mouseDown(textContainer);
      fireEvent.mouseUp(textContainer);

      // Should have proper ARIA labels
      expect(screen.getByRole('textbox', { name: /text selection area/i })).toBeInTheDocument();
    });
  });
});

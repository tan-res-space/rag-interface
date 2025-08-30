/**
 * Enhanced tests for BeforeAfterComparison component with fixes for failing tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '@/shared/theme/theme';
import { BeforeAfterComparison } from '@/features/verification/components/BeforeAfterComparison';
import { TextComparison, ChangeType } from '@/domain/types/verification';

// Mock useMediaQuery for responsive testing
const mockUseMediaQuery = jest.fn();
jest.mock('@mui/material/useMediaQuery', () => mockUseMediaQuery);

// Test wrapper
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('BeforeAfterComparison - Enhanced Tests', () => {
  const mockComparison: TextComparison = {
    originalText: 'This is a test sentence with some errors.',
    correctedText: 'This is a test sentence with some corrections.',
    changes: [
      {
        type: ChangeType.SUBSTITUTION,
        originalStart: 35,
        originalEnd: 41,
        correctedStart: 35,
        correctedEnd: 47,
        originalText: 'errors',
        correctedText: 'corrections',
        confidence: 0.95
      }
    ]
  };

  const mockComparisonWithMultipleChanges: TextComparison = {
    originalText: 'This are a test sentence with some errors.',
    correctedText: 'This is a test sentence with some corrections.',
    changes: [
      {
        type: ChangeType.SUBSTITUTION,
        originalStart: 5,
        originalEnd: 8,
        correctedStart: 5,
        correctedEnd: 7,
        originalText: 'are',
        correctedText: 'is',
        confidence: 0.98
      },
      {
        type: ChangeType.SUBSTITUTION,
        originalStart: 35,
        originalEnd: 41,
        correctedStart: 35,
        correctedEnd: 47,
        originalText: 'errors',
        correctedText: 'corrections',
        confidence: 0.95
      }
    ]
  };

  const mockComparisonWithDifferentChangeTypes: TextComparison = {
    originalText: 'This old text has some content.',
    correctedText: 'New text has some additional content.',
    changes: [
      {
        type: ChangeType.DELETION,
        originalStart: 5,
        originalEnd: 9,
        correctedStart: 0,
        correctedEnd: 0,
        originalText: 'old ',
        correctedText: '',
        confidence: 0.90
      },
      {
        type: ChangeType.INSERTION,
        originalStart: 0,
        originalEnd: 0,
        correctedStart: 0,
        correctedEnd: 4,
        originalText: '',
        correctedText: 'New ',
        confidence: 0.92
      },
      {
        type: ChangeType.INSERTION,
        originalStart: 22,
        originalEnd: 22,
        correctedStart: 22,
        correctedEnd: 32,
        originalText: '',
        correctedText: 'additional ',
        confidence: 0.88
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Default to desktop view
    mockUseMediaQuery.mockReturnValue(false);
  });

  describe('Basic Rendering - Fixed', () => {
    test('should render both original and corrected text with proper text matching', async () => {
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparison}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Original Text')).toBeInTheDocument();
      expect(screen.getByText('Corrected Text')).toBeInTheDocument();
      
      // Use more flexible text matching for text that might be split by elements
      expect(screen.getByText((content, element) => {
        return element?.textContent === mockComparison.originalText;
      })).toBeInTheDocument();
      
      expect(screen.getByText((content, element) => {
        return element?.textContent === mockComparison.correctedText;
      })).toBeInTheDocument();
    });

    test('should show comparison statistics', async () => {
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparisonWithMultipleChanges}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      expect(screen.getByText('2 changes')).toBeInTheDocument();
      expect(screen.getByText('2 substitutions')).toBeInTheDocument();
    });
  });

  describe('Diff Highlighting - Fixed', () => {
    test('should show different colors for different change types', async () => {
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparisonWithDifferentChangeTypes}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      // Wait for component to render
      await waitFor(() => {
        expect(screen.getByText('Original Text')).toBeInTheDocument();
      });

      // Check for insertion element (should be in corrected text)
      const insertionElement = screen.getByTestId('diff-corrected-0');
      expect(insertionElement).toHaveClass('diff-insertion');

      // Check for deletion element (should be in original text)
      const deletionElement = screen.getByTestId('diff-original-0');
      expect(deletionElement).toHaveClass('diff-deletion');
    });

    test('should handle cases where not all changes have corresponding elements', async () => {
      const comparisonWithLimitedChanges: TextComparison = {
        originalText: 'This old text.',
        correctedText: 'New text.',
        changes: [
          {
            type: ChangeType.DELETION,
            originalStart: 5,
            originalEnd: 9,
            correctedStart: 0,
            correctedEnd: 0,
            originalText: 'old ',
            correctedText: '',
            confidence: 0.90
          },
          {
            type: ChangeType.INSERTION,
            originalStart: 0,
            originalEnd: 0,
            correctedStart: 0,
            correctedEnd: 4,
            originalText: '',
            correctedText: 'New ',
            confidence: 0.92
          }
        ]
      };

      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={comparisonWithLimitedChanges}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      // Should only have elements that actually exist
      expect(screen.getByTestId('diff-original-0')).toBeInTheDocument();
      expect(screen.getByTestId('diff-corrected-0')).toBeInTheDocument();
      
      // Should not try to access non-existent elements
      expect(screen.queryByTestId('diff-original-1')).not.toBeInTheDocument();
      expect(screen.queryByTestId('diff-corrected-1')).not.toBeInTheDocument();
    });
  });

  describe('Responsive Design - Fixed', () => {
    test('should stack vertically on mobile', async () => {
      // Mock mobile view
      mockUseMediaQuery.mockReturnValue(true);
      
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparison}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      const container = screen.getByTestId('comparison-container');
      expect(container).toHaveClass('mobile-layout');
    });

    test('should show side-by-side on desktop', async () => {
      // Mock desktop view
      mockUseMediaQuery.mockReturnValue(false);
      
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparison}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      const container = screen.getByTestId('comparison-container');
      expect(container).toHaveClass('desktop-layout');
    });
  });

  describe('Change Navigation - Enhanced', () => {
    test('should navigate between changes correctly', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparisonWithMultipleChanges}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      // Should start at first change
      expect(screen.getByText('1 of 2')).toBeInTheDocument();
      
      // Navigate to next change
      const nextButton = screen.getByLabelText('Next change');
      await user.click(nextButton);
      
      expect(screen.getByText('2 of 2')).toBeInTheDocument();
      
      // Navigate back to previous change
      const prevButton = screen.getByLabelText('Previous change');
      await user.click(prevButton);
      
      expect(screen.getByText('1 of 2')).toBeInTheDocument();
    });

    test('should disable navigation buttons appropriately', async () => {
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparisonWithMultipleChanges}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      // Previous button should be disabled at start
      const prevButton = screen.getByLabelText('Previous change');
      expect(prevButton).toBeDisabled();
      
      // Next button should be enabled
      const nextButton = screen.getByLabelText('Next change');
      expect(nextButton).not.toBeDisabled();
    });
  });

  describe('Action Buttons', () => {
    test('should call onApprove when approve button is clicked', async () => {
      const user = userEvent.setup();
      const onApprove = jest.fn();
      
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparison}
            onApprove={onApprove}
            showActions={true}
          />
        </TestWrapper>
      );

      const approveButton = screen.getByRole('button', { name: /approve/i });
      await user.click(approveButton);
      
      expect(onApprove).toHaveBeenCalledWith(mockComparison);
    });

    test('should call onReject when reject button is clicked', async () => {
      const user = userEvent.setup();
      const onReject = jest.fn();
      
      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={mockComparison}
            onReject={onReject}
            showActions={true}
          />
        </TestWrapper>
      );

      const rejectButton = screen.getByRole('button', { name: /reject/i });
      await user.click(rejectButton);
      
      expect(onReject).toHaveBeenCalledWith(mockComparison);
    });
  });

  describe('Error Handling', () => {
    test('should handle empty text gracefully', async () => {
      const emptyComparison: TextComparison = {
        originalText: '',
        correctedText: '',
        changes: []
      };

      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={emptyComparison}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Original Text')).toBeInTheDocument();
      expect(screen.getByText('Corrected Text')).toBeInTheDocument();
      expect(screen.getByText('0 changes')).toBeInTheDocument();
    });

    test('should handle invalid change positions', async () => {
      const invalidComparison: TextComparison = {
        originalText: 'Short text',
        correctedText: 'Short text',
        changes: [
          {
            type: ChangeType.SUBSTITUTION,
            originalStart: 100, // Invalid position
            originalEnd: 110,
            correctedStart: 100,
            correctedEnd: 110,
            originalText: 'invalid',
            correctedText: 'invalid',
            confidence: 0.5
          }
        ]
      };

      render(
        <TestWrapper>
          <BeforeAfterComparison 
            comparison={invalidComparison}
            highlightDifferences={true}
          />
        </TestWrapper>
      );

      // Should render without crashing
      expect(screen.getByText('Original Text')).toBeInTheDocument();
      expect(screen.getByText('Corrected Text')).toBeInTheDocument();
    });
  });
});

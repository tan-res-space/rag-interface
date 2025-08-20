/**
 * BeforeAfterComparison component tests
 * Following TDD methodology - tests written first
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';
import { lightTheme } from '@shared/theme/theme';
import { BeforeAfterComparison } from './BeforeAfterComparison';
import type { BeforeAfterComparisonProps } from './BeforeAfterComparison';

// Wrapper component with theme
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={lightTheme}>{children}</ThemeProvider>
);

// Mock comparison data
const mockComparison = {
  id: 'comparison-1',
  originalText: 'This are a test sentence with some errors.',
  correctedText: 'This is a test sentence with some corrections.',
  changes: [
    {
      type: 'substitution' as const,
      originalStart: 5,
      originalEnd: 8,
      correctedStart: 5,
      correctedEnd: 7,
      originalText: 'are',
      correctedText: 'is',
    },
    {
      type: 'substitution' as const,
      originalStart: 32,
      originalEnd: 38,
      correctedStart: 32,
      correctedEnd: 43,
      originalText: 'errors',
      correctedText: 'corrections',
    },
  ],
};

const defaultProps: BeforeAfterComparisonProps = {
  originalText: mockComparison.originalText,
  correctedText: mockComparison.correctedText,
  changes: mockComparison.changes,
  onApprove: vi.fn(),
  onReject: vi.fn(),
  showActions: true,
  highlightDifferences: true,
};

describe('BeforeAfterComparison Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render both original and corrected text', () => {
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      expect(screen.getByText('Original Text')).toBeInTheDocument();
      expect(screen.getByText('Corrected Text')).toBeInTheDocument();
      expect(screen.getByText(mockComparison.originalText)).toBeInTheDocument();
      expect(screen.getByText(mockComparison.correctedText)).toBeInTheDocument();
    });

    it('should show comparison statistics', () => {
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      expect(screen.getByText('2 changes')).toBeInTheDocument();
      expect(screen.getByText('2 substitutions')).toBeInTheDocument();
    });

    it('should render without actions when showActions is false', () => {
      render(<BeforeAfterComparison {...defaultProps} showActions={false} />, { wrapper: TestWrapper });
      
      expect(screen.queryByRole('button', { name: /approve/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /reject/i })).not.toBeInTheDocument();
    });
  });

  describe('Diff Highlighting', () => {
    it('should highlight differences when highlightDifferences is true', () => {
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      // Check for highlighted text segments
      expect(screen.getByTestId('diff-original-0')).toBeInTheDocument();
      expect(screen.getByTestId('diff-corrected-0')).toBeInTheDocument();
      expect(screen.getByTestId('diff-original-1')).toBeInTheDocument();
      expect(screen.getByTestId('diff-corrected-1')).toBeInTheDocument();
    });

    it('should not highlight differences when highlightDifferences is false', () => {
      render(<BeforeAfterComparison {...defaultProps} highlightDifferences={false} />, { wrapper: TestWrapper });
      
      expect(screen.queryByTestId('diff-original-0')).not.toBeInTheDocument();
      expect(screen.queryByTestId('diff-corrected-0')).not.toBeInTheDocument();
    });

    it('should show different colors for different change types', () => {
      const changesWithDifferentTypes = [
        {
          type: 'insertion' as const,
          originalStart: 0,
          originalEnd: 0,
          correctedStart: 0,
          correctedEnd: 4,
          originalText: '',
          correctedText: 'New ',
        },
        {
          type: 'deletion' as const,
          originalStart: 5,
          originalEnd: 8,
          correctedStart: 5,
          correctedEnd: 5,
          originalText: 'old',
          correctedText: '',
        },
      ];

      render(
        <BeforeAfterComparison 
          {...defaultProps} 
          changes={changesWithDifferentTypes}
        />, 
        { wrapper: TestWrapper }
      );
      
      const insertionElement = screen.getByTestId('diff-corrected-0');
      const deletionElement = screen.getByTestId('diff-original-1');
      
      expect(insertionElement).toHaveClass('diff-insertion');
      expect(deletionElement).toHaveClass('diff-deletion');
    });
  });

  describe('Action Buttons', () => {
    it('should call onApprove when approve button is clicked', async () => {
      const user = userEvent.setup();
      const onApprove = vi.fn();
      
      render(<BeforeAfterComparison {...defaultProps} onApprove={onApprove} />, { wrapper: TestWrapper });
      
      const approveButton = screen.getByRole('button', { name: /approve/i });
      await user.click(approveButton);
      
      expect(onApprove).toHaveBeenCalledTimes(1);
    });

    it('should call onReject when reject button is clicked', async () => {
      const user = userEvent.setup();
      const onReject = vi.fn();
      
      render(<BeforeAfterComparison {...defaultProps} onReject={onReject} />, { wrapper: TestWrapper });
      
      const rejectButton = screen.getByRole('button', { name: /reject/i });
      await user.click(rejectButton);
      
      expect(onReject).toHaveBeenCalledTimes(1);
    });

    it('should disable buttons when disabled prop is true', () => {
      render(<BeforeAfterComparison {...defaultProps} disabled={true} />, { wrapper: TestWrapper });
      
      const approveButton = screen.getByRole('button', { name: /approve/i });
      const rejectButton = screen.getByRole('button', { name: /reject/i });
      
      expect(approveButton).toBeDisabled();
      expect(rejectButton).toBeDisabled();
    });
  });

  describe('Change Navigation', () => {
    it('should show navigation controls when multiple changes exist', () => {
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      expect(screen.getByRole('button', { name: /previous change/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /next change/i })).toBeInTheDocument();
      expect(screen.getByText('1 of 2')).toBeInTheDocument();
    });

    it('should navigate between changes', async () => {
      const user = userEvent.setup();
      
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      const nextButton = screen.getByRole('button', { name: /next change/i });
      await user.click(nextButton);
      
      expect(screen.getByText('2 of 2')).toBeInTheDocument();
    });

    it('should highlight current change differently', async () => {
      const user = userEvent.setup();
      
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      const firstChange = screen.getByTestId('diff-original-0');
      expect(firstChange).toHaveClass('diff-current');
      
      const nextButton = screen.getByRole('button', { name: /next change/i });
      await user.click(nextButton);
      
      const secondChange = screen.getByTestId('diff-original-1');
      expect(secondChange).toHaveClass('diff-current');
    });
  });

  describe('Responsive Design', () => {
    it('should stack vertically on mobile', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      const container = screen.getByTestId('comparison-container');
      expect(container).toHaveClass('mobile-layout');
    });

    it('should show side-by-side on desktop', () => {
      // Mock desktop viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      });
      
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      const container = screen.getByTestId('comparison-container');
      expect(container).toHaveClass('desktop-layout');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      const originalSection = screen.getByRole('region', { name: /original text/i });
      const correctedSection = screen.getByRole('region', { name: /corrected text/i });
      
      expect(originalSection).toBeInTheDocument();
      expect(correctedSection).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      const nextButton = screen.getByRole('button', { name: /next change/i });
      
      await user.tab();
      expect(nextButton).toHaveFocus();
      
      await user.keyboard('{Enter}');
      expect(screen.getByText('2 of 2')).toBeInTheDocument();
    });

    it('should announce changes to screen readers', () => {
      render(<BeforeAfterComparison {...defaultProps} />, { wrapper: TestWrapper });
      
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveTextContent('Showing change 1 of 2');
    });
  });

  describe('Error Handling', () => {
    it('should handle empty text gracefully', () => {
      render(
        <BeforeAfterComparison 
          {...defaultProps} 
          originalText="" 
          correctedText="" 
          changes={[]}
        />, 
        { wrapper: TestWrapper }
      );
      
      expect(screen.getByText('No changes to display')).toBeInTheDocument();
    });

    it('should handle invalid change positions', () => {
      const invalidChanges = [
        {
          type: 'substitution' as const,
          originalStart: -1,
          originalEnd: 1000,
          correctedStart: -1,
          correctedEnd: 1000,
          originalText: 'invalid',
          correctedText: 'invalid',
        },
      ];

      render(
        <BeforeAfterComparison 
          {...defaultProps} 
          changes={invalidChanges}
        />, 
        { wrapper: TestWrapper }
      );
      
      // Should not crash and should handle gracefully
      const container = screen.getByTestId('comparison-container');
      expect(container).toBeInTheDocument();
    });
  });
});

/**
 * TextSelection component tests
 * Following TDD methodology - tests written first
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { lightTheme } from '@shared/theme/theme';
import { TextSelection } from './TextSelection';
import type { TextSelectionProps } from './TextSelection';

// Mock useMediaQuery
vi.mock('@mui/material', async () => {
  const actual = await vi.importActual('@mui/material');
  return {
    ...actual,
    useMediaQuery: vi.fn(() => false), // Default to desktop
  };
});

// Wrapper component with theme
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={lightTheme}>{children}</ThemeProvider>
);

// Mock data
const mockText = "This is a sample text for testing text selection functionality.";

const defaultProps: TextSelectionProps = {
  text: mockText,
  onSelectionChange: vi.fn(),
  selections: [],
  disabled: false,
};

describe('TextSelection Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render text content correctly', () => {
      render(<TextSelection {...defaultProps} />, { wrapper: TestWrapper });
      expect(screen.getByText(mockText)).toBeInTheDocument();
    });

    it('should render container with correct attributes', () => {
      render(<TextSelection {...defaultProps} />, { wrapper: TestWrapper });
      const container = screen.getByTestId('text-selection-container');
      expect(container).toBeInTheDocument();
      expect(container).toHaveAttribute('role', 'textbox');
      expect(container).toHaveAttribute('aria-label', 'Text selection area');
    });

    it('should be disabled when disabled prop is true', () => {
      render(<TextSelection {...defaultProps} disabled={true} />, { wrapper: TestWrapper });
      const container = screen.getByTestId('text-selection-container');
      expect(container).toHaveAttribute('tabindex', '-1');
    });
  });

  describe('Selection Display', () => {
    it('should show selection count when selections exist', () => {
      const selections = [
        {
          selectionId: 'selection-1',
          text: 'first',
          startPosition: 0,
          endPosition: 5,
        },
        {
          selectionId: 'selection-2',
          text: 'second',
          startPosition: 10,
          endPosition: 16,
        },
      ];

      render(<TextSelection {...defaultProps} selections={selections} />, { wrapper: TestWrapper });

      expect(screen.getByText('2 selections')).toBeInTheDocument();
    });

    it('should show clear button when selections exist', () => {
      const selections = [
        {
          selectionId: 'selection-1',
          text: 'selected text',
          startPosition: 0,
          endPosition: 13,
        },
      ];

      render(<TextSelection {...defaultProps} selections={selections} />, { wrapper: TestWrapper });

      const clearButton = screen.getByRole('button', { name: /clear selections/i });
      expect(clearButton).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle empty text gracefully', () => {
      render(<TextSelection {...defaultProps} text="" />, { wrapper: TestWrapper });

      const container = screen.getByTestId('text-selection-container');
      expect(container).toBeInTheDocument();
    });

    it('should handle invalid selection ranges', () => {
      const invalidSelections = [
        {
          selectionId: 'invalid',
          text: 'invalid',
          startPosition: -1,
          endPosition: 1000,
        },
      ];

      render(<TextSelection {...defaultProps} selections={invalidSelections} />, { wrapper: TestWrapper });

      // Should not crash and should handle gracefully
      const container = screen.getByTestId('text-selection-container');
      expect(container).toBeInTheDocument();
    });
  });
});

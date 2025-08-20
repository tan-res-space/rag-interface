/**
 * ErrorCategorization component tests
 * Following TDD methodology - tests written first
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';
import { lightTheme } from '@shared/theme/theme';
import { ErrorCategorization } from './ErrorCategorization';
import type { ErrorCategorizationProps } from './ErrorCategorization';

// Wrapper component with theme
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={lightTheme}>{children}</ThemeProvider>
);

// Mock error categories
const mockCategories = [
  {
    id: 'grammar',
    name: 'Grammar',
    description: 'Grammatical errors and issues',
    parentCategory: undefined,
    isActive: true,
  },
  {
    id: 'spelling',
    name: 'Spelling',
    description: 'Spelling mistakes and typos',
    parentCategory: undefined,
    isActive: true,
  },
  {
    id: 'punctuation',
    name: 'Punctuation',
    description: 'Punctuation errors',
    parentCategory: 'grammar',
    isActive: true,
  },
  {
    id: 'syntax',
    name: 'Syntax',
    description: 'Syntax errors',
    parentCategory: 'grammar',
    isActive: true,
  },
];

const defaultProps: ErrorCategorizationProps = {
  categories: mockCategories,
  selectedCategories: [],
  onCategoriesChange: vi.fn(),
  disabled: false,
  maxSelections: 5,
};

describe('ErrorCategorization Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render all available categories', () => {
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });
      
      expect(screen.getByText('Grammar')).toBeInTheDocument();
      expect(screen.getByText('Spelling')).toBeInTheDocument();
      expect(screen.getByText('Punctuation')).toBeInTheDocument();
      expect(screen.getByText('Syntax')).toBeInTheDocument();
    });

    it('should show category descriptions on hover', async () => {
      const user = userEvent.setup();
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });
      
      const grammarChip = screen.getByText('Grammar');
      await user.hover(grammarChip);
      
      expect(screen.getByText('Grammatical errors and issues')).toBeInTheDocument();
    });

    it('should be disabled when disabled prop is true', () => {
      render(<ErrorCategorization {...defaultProps} disabled={true} />, { wrapper: TestWrapper });
      
      const grammarChip = screen.getByText('Grammar').closest('div');
      expect(grammarChip).toHaveClass('Mui-disabled');
    });
  });

  describe('Category Selection', () => {
    it('should handle single category selection', async () => {
      const user = userEvent.setup();
      const onCategoriesChange = vi.fn();
      
      render(
        <ErrorCategorization {...defaultProps} onCategoriesChange={onCategoriesChange} />,
        { wrapper: TestWrapper }
      );
      
      const grammarChip = screen.getByText('Grammar');
      await user.click(grammarChip);
      
      expect(onCategoriesChange).toHaveBeenCalledWith(['grammar']);
    });

    it('should handle multiple category selection', async () => {
      const user = userEvent.setup();
      const onCategoriesChange = vi.fn();
      
      render(
        <ErrorCategorization {...defaultProps} onCategoriesChange={onCategoriesChange} />,
        { wrapper: TestWrapper }
      );
      
      const grammarChip = screen.getByText('Grammar');
      const spellingChip = screen.getByText('Spelling');
      
      await user.click(grammarChip);
      await user.click(spellingChip);
      
      expect(onCategoriesChange).toHaveBeenCalledTimes(2);
      expect(onCategoriesChange).toHaveBeenNthCalledWith(1, ['grammar']);
      expect(onCategoriesChange).toHaveBeenNthCalledWith(2, ['spelling']);
    });

    it('should deselect category when clicked again', async () => {
      const user = userEvent.setup();
      const onCategoriesChange = vi.fn();
      
      render(
        <ErrorCategorization 
          {...defaultProps} 
          selectedCategories={['grammar']}
          onCategoriesChange={onCategoriesChange} 
        />,
        { wrapper: TestWrapper }
      );
      
      const grammarChip = screen.getByText('Grammar');
      await user.click(grammarChip);
      
      expect(onCategoriesChange).toHaveBeenCalledWith([]);
    });

    it('should respect max selections limit', async () => {
      const user = userEvent.setup();
      const onCategoriesChange = vi.fn();
      
      render(
        <ErrorCategorization 
          {...defaultProps} 
          maxSelections={1}
          onCategoriesChange={onCategoriesChange} 
        />,
        { wrapper: TestWrapper }
      );
      
      const grammarChip = screen.getByText('Grammar');
      const spellingChip = screen.getByText('Spelling');
      
      await user.click(grammarChip);
      await user.click(spellingChip);
      
      // Should only allow one selection
      expect(onCategoriesChange).toHaveBeenCalledTimes(1);
      expect(onCategoriesChange).toHaveBeenCalledWith(['grammar']);
    });
  });

  describe('Hierarchical Categories', () => {
    it('should show parent-child relationships', () => {
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });
      
      // Parent categories should be displayed prominently
      const grammarSection = screen.getByTestId('category-group-grammar');
      expect(grammarSection).toBeInTheDocument();
      
      // Child categories should be nested under parent
      const punctuationChip = screen.getByText('Punctuation');
      const syntaxChip = screen.getByText('Syntax');
      
      expect(punctuationChip).toBeInTheDocument();
      expect(syntaxChip).toBeInTheDocument();
    });

    it('should auto-select parent when child is selected', async () => {
      const user = userEvent.setup();
      const onCategoriesChange = vi.fn();
      
      render(
        <ErrorCategorization {...defaultProps} onCategoriesChange={onCategoriesChange} />,
        { wrapper: TestWrapper }
      );
      
      const punctuationChip = screen.getByText('Punctuation');
      await user.click(punctuationChip);
      
      expect(onCategoriesChange).toHaveBeenCalledWith(['grammar', 'punctuation']);
    });

    it('should deselect children when parent is deselected', async () => {
      const user = userEvent.setup();
      const onCategoriesChange = vi.fn();
      
      render(
        <ErrorCategorization 
          {...defaultProps} 
          selectedCategories={['grammar', 'punctuation', 'syntax']}
          onCategoriesChange={onCategoriesChange} 
        />,
        { wrapper: TestWrapper }
      );
      
      const grammarChip = screen.getByText('Grammar');
      await user.click(grammarChip);
      
      expect(onCategoriesChange).toHaveBeenCalledWith([]);
    });
  });

  describe('Search and Filter', () => {
    it('should filter categories based on search input', async () => {
      const user = userEvent.setup();
      
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });
      
      const searchInput = screen.getByPlaceholderText('Search categories...');
      await user.type(searchInput, 'spell');
      
      expect(screen.getByText('Spelling')).toBeInTheDocument();
      expect(screen.queryByText('Grammar')).not.toBeInTheDocument();
    });

    it('should show no results message when search yields no matches', async () => {
      const user = userEvent.setup();
      
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });
      
      const searchInput = screen.getByPlaceholderText('Search categories...');
      await user.type(searchInput, 'nonexistent');
      
      expect(screen.getByText('No categories found')).toBeInTheDocument();
    });

    it('should clear search when clear button is clicked', async () => {
      const user = userEvent.setup();
      
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });
      
      const searchInput = screen.getByPlaceholderText('Search categories...');
      await user.type(searchInput, 'spell');
      
      const clearButton = screen.getByRole('button', { name: /clear search/i });
      await user.click(clearButton);
      
      expect(searchInput).toHaveValue('');
      expect(screen.getByText('Grammar')).toBeInTheDocument();
    });
  });

  describe('Validation', () => {
    it('should show error when no categories are selected and required', () => {
      render(
        <ErrorCategorization {...defaultProps} required={true} error="Please select at least one category" />,
        { wrapper: TestWrapper }
      );
      
      expect(screen.getByText('Please select at least one category')).toBeInTheDocument();
    });

    it('should show warning when approaching max selections', () => {
      render(
        <ErrorCategorization
          {...defaultProps}
          maxSelections={2}
          selectedCategories={['grammar']}
        />,
        { wrapper: TestWrapper }
      );

      expect(screen.getByText('1 of 2 categories selected')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });
      
      const container = screen.getByRole('group', { name: /error categories/i });
      expect(container).toBeInTheDocument();
    });

    it('should support keyboard navigation', () => {
      render(<ErrorCategorization {...defaultProps} />, { wrapper: TestWrapper });

      const grammarChip = screen.getByText('Grammar');

      // Should have proper keyboard attributes
      expect(grammarChip).toHaveAttribute('role', 'button');
      expect(grammarChip).toHaveAttribute('tabindex', '0');
    });
  });
});

/**
 * Enhanced tests for ErrorCategorization component with fixes for failing tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '@/shared/theme/theme';
import { ErrorCategorization } from '@/features/error-reporting/components/ErrorCategorization';
import { ErrorCategory } from '@/domain/types/error-reporting';

// Test wrapper
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('ErrorCategorization - Enhanced Tests', () => {
  const mockCategories: ErrorCategory[] = [
    {
      id: 'grammar',
      name: 'Grammar',
      description: 'Grammatical errors and issues',
      subcategories: [
        { id: 'punctuation', name: 'Punctuation', description: 'Punctuation errors' },
        { id: 'syntax', name: 'Syntax', description: 'Syntax errors' }
      ]
    },
    {
      id: 'spelling',
      name: 'Spelling',
      description: 'Spelling mistakes and typos',
      subcategories: []
    },
    {
      id: 'style',
      name: 'Style',
      description: 'Style and formatting issues',
      subcategories: [
        { id: 'tone', name: 'Tone', description: 'Tone and voice issues' },
        { id: 'clarity', name: 'Clarity', description: 'Clarity and readability' }
      ]
    },
    {
      id: 'content',
      name: 'Content',
      description: 'Content accuracy and relevance',
      subcategories: []
    },
    {
      id: 'technical',
      name: 'Technical',
      description: 'Technical terminology and accuracy',
      subcategories: []
    }
  ];

  const defaultProps = {
    categories: mockCategories,
    selectedCategories: [],
    onSelectionChange: jest.fn(),
    disabled: false,
    searchable: true,
    showSubcategories: true
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering - Fixed', () => {
    test('should render all available categories', async () => {
      render(
        <TestWrapper>
          <ErrorCategorization {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Grammar')).toBeInTheDocument();
      expect(screen.getByText('Spelling')).toBeInTheDocument();
      expect(screen.getByText('Style')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.getByText('Technical')).toBeInTheDocument();
    });

    test('should show category descriptions on hover with proper tooltip handling', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization {...defaultProps} />
        </TestWrapper>
      );

      // Find the grammar category chip
      const grammarChip = screen.getByLabelText('Grammatical errors and issues');
      
      // Hover over the chip
      await user.hover(grammarChip);
      
      // Wait for tooltip to appear with more flexible text matching
      await waitFor(() => {
        const tooltip = screen.getByRole('tooltip', { hidden: true });
        expect(tooltip).toBeInTheDocument();
        expect(tooltip).toHaveTextContent('Grammatical errors and issues');
      }, { timeout: 2000 });
    });

    test('should be disabled when disabled prop is true', async () => {
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps} 
            disabled={true}
          />
        </TestWrapper>
      );

      const grammarChip = screen.getByText('Grammar');
      expect(grammarChip.closest('button')).toBeDisabled();
    });
  });

  describe('Category Selection - Enhanced', () => {
    test('should handle single category selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            onSelectionChange={onSelectionChange}
          />
        </TestWrapper>
      );

      const grammarChip = screen.getByText('Grammar');
      await user.click(grammarChip);
      
      expect(onSelectionChange).toHaveBeenCalledWith(['grammar']);
    });

    test('should handle multiple category selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            onSelectionChange={onSelectionChange}
          />
        </TestWrapper>
      );

      const grammarChip = screen.getByText('Grammar');
      const spellingChip = screen.getByText('Spelling');
      
      await user.click(grammarChip);
      await user.click(spellingChip);
      
      expect(onSelectionChange).toHaveBeenCalledTimes(2);
      expect(onSelectionChange).toHaveBeenNthCalledWith(1, ['grammar']);
      expect(onSelectionChange).toHaveBeenNthCalledWith(2, ['grammar', 'spelling']);
    });

    test('should deselect category when clicked again', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['grammar']}
            onSelectionChange={onSelectionChange}
          />
        </TestWrapper>
      );

      const grammarChip = screen.getByText('Grammar');
      await user.click(grammarChip);
      
      expect(onSelectionChange).toHaveBeenCalledWith([]);
    });
  });

  describe('Subcategory Handling', () => {
    test('should show subcategories when parent is selected', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['grammar']}
          />
        </TestWrapper>
      );

      // Subcategories should be visible
      expect(screen.getByText('Punctuation')).toBeInTheDocument();
      expect(screen.getByText('Syntax')).toBeInTheDocument();
    });

    test('should handle subcategory selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['grammar']}
            onSelectionChange={onSelectionChange}
          />
        </TestWrapper>
      );

      const punctuationChip = screen.getByText('Punctuation');
      await user.click(punctuationChip);
      
      expect(onSelectionChange).toHaveBeenCalledWith(['grammar', 'punctuation']);
    });

    test('should hide subcategories when parent is deselected', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['grammar', 'punctuation']}
          />
        </TestWrapper>
      );

      // Deselect parent category
      const grammarChip = screen.getByText('Grammar');
      await user.click(grammarChip);
      
      // Subcategories should be hidden
      await waitFor(() => {
        expect(screen.queryByText('Punctuation')).not.toBeInTheDocument();
        expect(screen.queryByText('Syntax')).not.toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    test('should filter categories based on search query', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization {...defaultProps} />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText('Search categories...');
      await user.type(searchInput, 'gram');
      
      // Should show only grammar category
      expect(screen.getByText('Grammar')).toBeInTheDocument();
      expect(screen.queryByText('Spelling')).not.toBeInTheDocument();
      expect(screen.queryByText('Style')).not.toBeInTheDocument();
    });

    test('should clear search when input is cleared', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization {...defaultProps} />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText('Search categories...');
      await user.type(searchInput, 'gram');
      await user.clear(searchInput);
      
      // All categories should be visible again
      expect(screen.getByText('Grammar')).toBeInTheDocument();
      expect(screen.getByText('Spelling')).toBeInTheDocument();
      expect(screen.getByText('Style')).toBeInTheDocument();
    });

    test('should show no results message when search yields no matches', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization {...defaultProps} />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText('Search categories...');
      await user.type(searchInput, 'nonexistent');
      
      expect(screen.getByText(/no categories found/i)).toBeInTheDocument();
    });
  });

  describe('Selection Counter', () => {
    test('should display correct selection count', async () => {
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['grammar', 'spelling']}
          />
        </TestWrapper>
      );

      expect(screen.getByText('2 of 5 categories selected')).toBeInTheDocument();
    });

    test('should update count when selections change', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['grammar']}
          />
        </TestWrapper>
      );

      expect(screen.getByText('1 of 5 categories selected')).toBeInTheDocument();
      
      const spellingChip = screen.getByText('Spelling');
      await user.click(spellingChip);
      
      await waitFor(() => {
        expect(screen.getByText('2 of 5 categories selected')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('should have proper ARIA labels and roles', async () => {
      render(
        <TestWrapper>
          <ErrorCategorization {...defaultProps} />
        </TestWrapper>
      );

      // Check for fieldset with proper legend
      const fieldset = screen.getByRole('group', { name: /error categories/i });
      expect(fieldset).toBeInTheDocument();
      
      // Check for proper button roles
      const grammarButton = screen.getByRole('button', { name: /grammatical errors and issues/i });
      expect(grammarButton).toBeInTheDocument();
    });

    test('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            onSelectionChange={onSelectionChange}
          />
        </TestWrapper>
      );

      const grammarChip = screen.getByText('Grammar');
      grammarChip.focus();
      
      // Should be able to activate with Enter or Space
      await user.keyboard('{Enter}');
      
      expect(onSelectionChange).toHaveBeenCalledWith(['grammar']);
    });

    test('should announce selection changes to screen readers', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['grammar']}
          />
        </TestWrapper>
      );

      // Check for live region that announces changes
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toBeInTheDocument();
      expect(liveRegion).toHaveTextContent('1 of 5 categories selected');
    });
  });

  describe('Error Handling', () => {
    test('should handle empty categories array', async () => {
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            categories={[]}
          />
        </TestWrapper>
      );

      expect(screen.getByText(/no categories available/i)).toBeInTheDocument();
    });

    test('should handle invalid selected categories', async () => {
      render(
        <TestWrapper>
          <ErrorCategorization 
            {...defaultProps}
            selectedCategories={['nonexistent']}
          />
        </TestWrapper>
      );

      // Should render without crashing and ignore invalid selections
      expect(screen.getByText('Grammar')).toBeInTheDocument();
      expect(screen.getByText('0 of 5 categories selected')).toBeInTheDocument();
    });
  });
});

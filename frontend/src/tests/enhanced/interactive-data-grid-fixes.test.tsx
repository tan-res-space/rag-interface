/**
 * Enhanced tests for InteractiveDataGrid component with fixes for failing tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';
import theme from '@/shared/theme/theme';
import { InteractiveDataGrid } from '@/features/verification/components/InteractiveDataGrid';
import { ErrorReport, ErrorStatus, ErrorSeverity } from '@/domain/types/error-reporting';

// Test wrapper
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('InteractiveDataGrid - Enhanced Tests', () => {
  const mockData: ErrorReport[] = [
    {
      id: 'error-1',
      speaker_id: 'speaker-1',
      original_text: 'This are wrong',
      corrected_text: 'This is wrong',
      error_type: 'grammar',
      severity: ErrorSeverity.MEDIUM,
      status: ErrorStatus.PENDING,
      confidence_score: 0.95,
      created_at: '2024-01-01T10:00:00Z',
      updated_at: '2024-01-01T10:00:00Z',
      reviewed_by: null,
      reviewed_at: null,
      notes: ''
    },
    {
      id: 'error-2',
      speaker_id: 'speaker-2',
      original_text: 'Another eror here',
      corrected_text: 'Another error here',
      error_type: 'spelling',
      severity: ErrorSeverity.LOW,
      status: ErrorStatus.APPROVED,
      confidence_score: 0.88,
      created_at: '2024-01-02T10:00:00Z',
      updated_at: '2024-01-02T10:00:00Z',
      reviewed_by: 'reviewer-1',
      reviewed_at: '2024-01-02T11:00:00Z',
      notes: 'Approved by reviewer'
    },
    {
      id: 'error-3',
      speaker_id: 'speaker-3',
      original_text: 'Third mistake',
      corrected_text: 'Third correction',
      error_type: 'style',
      severity: ErrorSeverity.HIGH,
      status: ErrorStatus.REJECTED,
      confidence_score: 0.72,
      created_at: '2024-01-03T10:00:00Z',
      updated_at: '2024-01-03T10:00:00Z',
      reviewed_by: 'reviewer-2',
      reviewed_at: '2024-01-03T11:00:00Z',
      notes: 'Rejected due to low confidence'
    }
  ];

  const defaultProps = {
    data: mockData,
    columns: [
      { field: 'id', headerName: 'ID', width: 100 },
      { field: 'created_at', headerName: 'Date', width: 120 },
      { field: 'original_text', headerName: 'Original Text', width: 200 },
      { field: 'corrected_text', headerName: 'Corrected Text', width: 200 },
      { field: 'error_type', headerName: 'Type', width: 100 },
      { field: 'severity', headerName: 'Severity', width: 100 },
      { field: 'status', headerName: 'Status', width: 120, editable: true },
      { field: 'confidence_score', headerName: 'Confidence', width: 100 }
    ],
    loading: false,
    onSelectionChange: jest.fn(),
    onEdit: jest.fn(),
    onSort: jest.fn(),
    onFilter: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Row Selection - Fixed', () => {
    test('should handle single row selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            onSelectionChange={onSelectionChange}
            selectable={true}
          />
        </TestWrapper>
      );

      // Wait for grid to render
      await waitFor(() => {
        expect(screen.getByText('error-1')).toBeInTheDocument();
      });

      // Find and click the first row checkbox (not the header checkbox)
      const firstRowCheckbox = screen.getByTestId('row-checkbox-error-1');
      await user.click(firstRowCheckbox);
      
      expect(onSelectionChange).toHaveBeenCalledWith(['error-1']);
    });

    test('should handle multiple row selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            onSelectionChange={onSelectionChange}
            selectable={true}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('error-1')).toBeInTheDocument();
      });

      // Select first row
      const firstRowCheckbox = screen.getByTestId('row-checkbox-error-1');
      await user.click(firstRowCheckbox);
      
      // Select second row
      const secondRowCheckbox = screen.getByTestId('row-checkbox-error-2');
      await user.click(secondRowCheckbox);
      
      expect(onSelectionChange).toHaveBeenCalledTimes(2);
      expect(onSelectionChange).toHaveBeenNthCalledWith(1, ['error-1']);
      expect(onSelectionChange).toHaveBeenNthCalledWith(2, ['error-1', 'error-2']);
    });

    test('should handle select all functionality', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            onSelectionChange={onSelectionChange}
            selectable={true}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('error-1')).toBeInTheDocument();
      });

      // Click select all checkbox
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      await user.click(selectAllCheckbox);
      
      expect(onSelectionChange).toHaveBeenCalledWith(['error-1', 'error-2', 'error-3']);
    });
  });

  describe('Inline Editing - Fixed', () => {
    test('should enable editing for editable cells', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            editable={true}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('error-1')).toBeInTheDocument();
      });

      // Find the status cell for the first row
      const statusCell = screen.getByTestId('cell-error-1-status');
      
      // Double click to enter edit mode
      fireEvent.doubleClick(statusCell);

      // Should show the edit control (select dropdown for status)
      await waitFor(() => {
        const editControls = screen.getAllByRole('combobox');
        // Filter out pagination combobox by looking for the one in the table
        const statusCombobox = editControls.find(control => 
          control.closest('[data-testid="cell-error-1-status"]')
        );
        expect(statusCombobox).toBeInTheDocument();
      });
    });

    test('should call onEdit when cell value is changed', async () => {
      const user = userEvent.setup();
      const onEdit = jest.fn();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            onEdit={onEdit}
            editable={true}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('error-1')).toBeInTheDocument();
      });

      // Enter edit mode
      const statusCell = screen.getByTestId('cell-error-1-status');
      fireEvent.doubleClick(statusCell);

      await waitFor(() => {
        const editControls = screen.getAllByRole('combobox');
        const statusCombobox = editControls.find(control => 
          control.closest('[data-testid="cell-error-1-status"]')
        );
        expect(statusCombobox).toBeInTheDocument();
      });

      // Find the correct select element within the cell
      const statusCombobox = screen.getAllByRole('combobox').find(control => 
        control.closest('[data-testid="cell-error-1-status"]')
      );
      
      if (statusCombobox) {
        await user.click(statusCombobox);
        
        // Select new value
        const inReviewOption = screen.getByRole('option', { name: 'In Review' });
        await user.click(inReviewOption);

        // Verify onEdit was called
        expect(onEdit).toHaveBeenCalledWith('error-1', 'status', 'In Review');
      }
    });

    test('should exit edit mode on blur', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            editable={true}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('error-1')).toBeInTheDocument();
      });

      // Enter edit mode
      const statusCell = screen.getByTestId('cell-error-1-status');
      fireEvent.doubleClick(statusCell);

      await waitFor(() => {
        const editControls = screen.getAllByRole('combobox');
        const statusCombobox = editControls.find(control => 
          control.closest('[data-testid="cell-error-1-status"]')
        );
        expect(statusCombobox).toBeInTheDocument();
      });

      // Click outside to blur
      await user.click(document.body);

      // Edit control should be removed
      await waitFor(() => {
        const editControls = screen.getAllByRole('combobox');
        const statusCombobox = editControls.find(control => 
          control.closest('[data-testid="cell-error-1-status"]')
        );
        expect(statusCombobox).toBeUndefined();
      });
    });
  });

  describe('Sorting and Filtering', () => {
    test('should handle column sorting', async () => {
      const user = userEvent.setup();
      const onSort = jest.fn();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            onSort={onSort}
            sortable={true}
          />
        </TestWrapper>
      );

      // Click on ID column header to sort
      const idHeader = screen.getByText('ID');
      await user.click(idHeader);
      
      expect(onSort).toHaveBeenCalledWith('id', 'asc');
    });

    test('should handle filtering', async () => {
      const user = userEvent.setup();
      const onFilter = jest.fn();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            onFilter={onFilter}
            filterable={true}
          />
        </TestWrapper>
      );

      // Open filter menu
      const filterButton = screen.getByLabelText(/filter/i);
      await user.click(filterButton);

      // Apply a filter
      const statusFilter = screen.getByLabelText(/status filter/i);
      await user.click(statusFilter);
      
      const pendingOption = screen.getByRole('option', { name: /pending/i });
      await user.click(pendingOption);

      expect(onFilter).toHaveBeenCalledWith('status', 'PENDING');
    });
  });

  describe('Pagination', () => {
    test('should display pagination controls', async () => {
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            pagination={true}
            pageSize={10}
            totalRows={25}
          />
        </TestWrapper>
      );

      // Check for pagination controls
      expect(screen.getByText(/rows per page/i)).toBeInTheDocument();
      expect(screen.getByText(/1–3 of 3/i)).toBeInTheDocument();
    });

    test('should handle page size changes', async () => {
      const user = userEvent.setup();
      const onPageSizeChange = jest.fn();
      
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            pagination={true}
            pageSize={10}
            onPageSizeChange={onPageSizeChange}
          />
        </TestWrapper>
      );

      // Find pagination select (not the status edit select)
      const paginationSelect = screen.getByLabelText(/rows per page/i);
      await user.click(paginationSelect);
      
      const option25 = screen.getByRole('option', { name: '25' });
      await user.click(option25);

      expect(onPageSizeChange).toHaveBeenCalledWith(25);
    });
  });

  describe('Loading and Error States', () => {
    test('should display loading state', async () => {
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            loading={true}
          />
        </TestWrapper>
      );

      expect(screen.getByTestId('data-grid-loading')).toBeInTheDocument();
    });

    test('should display empty state', async () => {
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            data={[]}
          />
        </TestWrapper>
      );

      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });

    test('should handle error state', async () => {
      render(
        <TestWrapper>
          <InteractiveDataGrid 
            {...defaultProps}
            error="Failed to load data"
          />
        </TestWrapper>
      );

      expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('should have proper ARIA labels', async () => {
      render(
        <TestWrapper>
          <InteractiveDataGrid
            {...defaultProps}
            selectable={true}
          />
        </TestWrapper>
      );

      // Check for proper ARIA labels
      expect(screen.getByLabelText(/error reports data grid/i)).toBeInTheDocument();
      expect(screen.getByTestId('select-all-checkbox')).toHaveAttribute('aria-label');
    });

    test('should support keyboard navigation', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <InteractiveDataGrid
            {...defaultProps}
            selectable={true}
          />
        </TestWrapper>
      );

      // Focus on first checkbox
      const firstCheckbox = screen.getByTestId('row-checkbox-error-1');
      firstCheckbox.focus();

      // Should be able to activate with space
      await user.keyboard(' ');

      expect(defaultProps.onSelectionChange).toHaveBeenCalledWith(['error-1']);
    });
  });

  describe('Performance', () => {
    test('should handle large datasets efficiently', async () => {
      const largeDataset = Array.from({ length: 1000 }, (_, index) => ({
        ...mockData[0],
        id: `error-${index + 1}`,
        original_text: `Error text ${index + 1}`,
      }));

      render(
        <TestWrapper>
          <InteractiveDataGrid
            {...defaultProps}
            data={largeDataset}
            virtualization={true}
          />
        </TestWrapper>
      );

      // Should render without performance issues
      await waitFor(() => {
        expect(screen.getByText('error-1')).toBeInTheDocument();
      });
    });
  });
});

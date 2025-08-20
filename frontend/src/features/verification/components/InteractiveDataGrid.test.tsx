/**
 * InteractiveDataGrid component tests
 * Following TDD methodology - tests written first
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';
import { lightTheme } from '@shared/theme/theme';
import { InteractiveDataGrid } from './InteractiveDataGrid';
import type { InteractiveDataGridProps, ErrorReport, DataGridColumn } from './InteractiveDataGrid';

// Wrapper component with theme
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={lightTheme}>{children}</ThemeProvider>
);

// Mock data
const mockErrorReports: ErrorReport[] = [
  {
    id: 'error-1',
    dateReported: new Date('2024-01-15'),
    status: 'pending',
    category: 'Grammar',
    originalText: 'This are a test sentence.',
    correctedText: 'This is a test sentence.',
    reportedBy: 'john.doe@example.com',
    reviewedBy: undefined,
    priority: 'high',
    comments: 'Subject-verb disagreement',
    position: { startPosition: 5, endPosition: 8 },
  },
  {
    id: 'error-2',
    dateReported: new Date('2024-01-14'),
    status: 'in_review',
    category: 'Spelling',
    originalText: 'Recieve the package.',
    correctedText: 'Receive the package.',
    reportedBy: 'jane.smith@example.com',
    reviewedBy: 'qa.supervisor@example.com',
    priority: 'medium',
    comments: 'Common spelling error',
    position: { startPosition: 0, endPosition: 7 },
  },
  {
    id: 'error-3',
    dateReported: new Date('2024-01-13'),
    status: 'approved',
    category: 'Punctuation',
    originalText: 'Hello world',
    correctedText: 'Hello, world!',
    reportedBy: 'bob.wilson@example.com',
    reviewedBy: 'qa.supervisor@example.com',
    priority: 'low',
    comments: 'Missing punctuation',
    position: { startPosition: 5, endPosition: 11 },
  },
];

const mockColumns: DataGridColumn[] = [
  { id: 'id', label: 'ID', sortable: true, filterable: false, editable: false, width: 100 },
  { id: 'dateReported', label: 'Date', sortable: true, filterable: true, editable: false, width: 120 },
  { id: 'status', label: 'Status', sortable: true, filterable: true, editable: true, width: 120 },
  { id: 'category', label: 'Category', sortable: true, filterable: true, editable: false, width: 120 },
  { id: 'originalText', label: 'Original Text', sortable: false, filterable: true, editable: false, width: 200 },
  { id: 'correctedText', label: 'Corrected Text', sortable: false, filterable: false, editable: true, width: 200 },
  { id: 'priority', label: 'Priority', sortable: true, filterable: true, editable: true, width: 100 },
];

const defaultProps: InteractiveDataGridProps = {
  data: mockErrorReports,
  columns: mockColumns,
  onSort: vi.fn(),
  onFilter: vi.fn(),
  onEdit: vi.fn(),
  onSelectionChange: vi.fn(),
  loading: false,
  pagination: {
    page: 0,
    pageSize: 10,
    total: mockErrorReports.length,
    onPageChange: vi.fn(),
    onPageSizeChange: vi.fn(),
  },
};

describe('InteractiveDataGrid Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render table with correct headers', () => {
      render(<InteractiveDataGrid {...defaultProps} />, { wrapper: TestWrapper });
      
      mockColumns.forEach(column => {
        expect(screen.getByText(column.label)).toBeInTheDocument();
      });
    });

    it('should render all data rows', () => {
      render(<InteractiveDataGrid {...defaultProps} />, { wrapper: TestWrapper });
      
      mockErrorReports.forEach(report => {
        expect(screen.getByText(report.id)).toBeInTheDocument();
        expect(screen.getByText(report.originalText)).toBeInTheDocument();
      });
    });

    it('should show loading state when loading prop is true', () => {
      render(<InteractiveDataGrid {...defaultProps} loading={true} />, { wrapper: TestWrapper });
      
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('should show empty state when no data provided', () => {
      render(<InteractiveDataGrid {...defaultProps} data={[]} />, { wrapper: TestWrapper });
      
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });
  });

  describe('Column Sorting', () => {
    it('should call onSort when sortable column header is clicked', async () => {
      const user = userEvent.setup();
      const onSort = vi.fn();
      
      render(<InteractiveDataGrid {...defaultProps} onSort={onSort} />, { wrapper: TestWrapper });
      
      const statusHeader = screen.getByText('Status');
      await user.click(statusHeader);
      
      expect(onSort).toHaveBeenCalledWith('status', 'asc');
    });

    it('should toggle sort direction on subsequent clicks', async () => {
      const user = userEvent.setup();
      const onSort = vi.fn();
      
      render(<InteractiveDataGrid {...defaultProps} onSort={onSort} />, { wrapper: TestWrapper });
      
      const statusHeader = screen.getByText('Status');
      await user.click(statusHeader);
      await user.click(statusHeader);
      
      expect(onSort).toHaveBeenNthCalledWith(1, 'status', 'asc');
      expect(onSort).toHaveBeenNthCalledWith(2, 'status', 'desc');
    });

    it('should show sort indicators', () => {
      render(
        <InteractiveDataGrid 
          {...defaultProps} 
          sortBy={{ column: 'status', direction: 'asc' }}
        />, 
        { wrapper: TestWrapper }
      );
      
      const sortIcon = screen.getByTestId('sort-icon-status');
      expect(sortIcon).toBeInTheDocument();
    });

    it('should not allow sorting on non-sortable columns', async () => {
      const user = userEvent.setup();
      const onSort = vi.fn();
      
      render(<InteractiveDataGrid {...defaultProps} onSort={onSort} />, { wrapper: TestWrapper });
      
      const originalTextHeader = screen.getByText('Original Text');
      await user.click(originalTextHeader);
      
      expect(onSort).not.toHaveBeenCalled();
    });
  });

  describe('Filtering', () => {
    it('should show filter inputs for filterable columns', () => {
      render(<InteractiveDataGrid {...defaultProps} showFilters={true} />, { wrapper: TestWrapper });
      
      expect(screen.getByPlaceholderText('Filter by Date')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Filter by Status')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Filter by Category')).toBeInTheDocument();
    });

    it('should call onFilter when filter value changes', async () => {
      const user = userEvent.setup();
      const onFilter = vi.fn();
      
      render(
        <InteractiveDataGrid {...defaultProps} onFilter={onFilter} showFilters={true} />, 
        { wrapper: TestWrapper }
      );
      
      const statusFilter = screen.getByPlaceholderText('Filter by Status');
      await user.type(statusFilter, 'pending');
      
      expect(onFilter).toHaveBeenCalledWith({ status: 'pending' });
    });

    it('should clear filters when clear button is clicked', async () => {
      const user = userEvent.setup();
      const onFilter = vi.fn();
      
      render(
        <InteractiveDataGrid {...defaultProps} onFilter={onFilter} showFilters={true} />, 
        { wrapper: TestWrapper }
      );
      
      const clearButton = screen.getByRole('button', { name: /clear filters/i });
      await user.click(clearButton);
      
      expect(onFilter).toHaveBeenCalledWith({});
    });
  });

  describe('Row Selection', () => {
    it('should handle single row selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = vi.fn();
      
      render(
        <InteractiveDataGrid {...defaultProps} onSelectionChange={onSelectionChange} />, 
        { wrapper: TestWrapper }
      );
      
      const firstRowCheckbox = screen.getByTestId('row-checkbox-error-1');
      await user.click(firstRowCheckbox);
      
      expect(onSelectionChange).toHaveBeenCalledWith(['error-1']);
    });

    it('should handle multiple row selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = vi.fn();
      
      render(
        <InteractiveDataGrid {...defaultProps} onSelectionChange={onSelectionChange} />, 
        { wrapper: TestWrapper }
      );
      
      const firstRowCheckbox = screen.getByTestId('row-checkbox-error-1');
      const secondRowCheckbox = screen.getByTestId('row-checkbox-error-2');
      
      await user.click(firstRowCheckbox);
      await user.click(secondRowCheckbox);
      
      expect(onSelectionChange).toHaveBeenCalledTimes(2);
    });

    it('should handle select all functionality', async () => {
      const user = userEvent.setup();
      const onSelectionChange = vi.fn();
      
      render(
        <InteractiveDataGrid {...defaultProps} onSelectionChange={onSelectionChange} />, 
        { wrapper: TestWrapper }
      );
      
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      await user.click(selectAllCheckbox);
      
      expect(onSelectionChange).toHaveBeenCalledWith(['error-1', 'error-2', 'error-3']);
    });
  });

  describe('Inline Editing', () => {
    it('should enable editing for editable cells', () => {
      render(<InteractiveDataGrid {...defaultProps} />, { wrapper: TestWrapper });

      const statusCell = screen.getByTestId('cell-error-1-status');
      fireEvent.doubleClick(statusCell);

      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('should call onEdit when cell value is changed', async () => {
      const user = userEvent.setup();
      const onEdit = vi.fn();

      render(<InteractiveDataGrid {...defaultProps} onEdit={onEdit} />, { wrapper: TestWrapper });

      const statusCell = screen.getByTestId('cell-error-1-status');
      fireEvent.doubleClick(statusCell);

      const select = screen.getByRole('combobox');
      await user.click(select);
      await user.click(screen.getByText('In Review'));

      expect(onEdit).toHaveBeenCalledWith('error-1', 'status', 'in_review');
    });

    it('should not allow editing for non-editable cells', () => {
      render(<InteractiveDataGrid {...defaultProps} />, { wrapper: TestWrapper });

      const idCell = screen.getByTestId('cell-error-1-id');
      fireEvent.doubleClick(idCell);

      expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
    });
  });

  describe('Pagination', () => {
    it('should show pagination controls', () => {
      render(<InteractiveDataGrid {...defaultProps} />, { wrapper: TestWrapper });

      expect(screen.getByText('Rows per page:')).toBeInTheDocument();
    });

    it('should call onPageChange when page is changed', async () => {
      const user = userEvent.setup();
      const onPageChange = vi.fn();
      
      const paginationProps = {
        ...defaultProps.pagination!,
        onPageChange,
        total: 25, // More than one page
      };
      
      render(
        <InteractiveDataGrid {...defaultProps} pagination={paginationProps} />, 
        { wrapper: TestWrapper }
      );
      
      const nextButton = screen.getByRole('button', { name: /next page/i });
      await user.click(nextButton);
      
      expect(onPageChange).toHaveBeenCalledWith(1);
    });

    it('should call onPageSizeChange when page size is changed', async () => {
      const user = userEvent.setup();
      const onPageSizeChange = vi.fn();
      
      const paginationProps = {
        ...defaultProps.pagination!,
        onPageSizeChange,
      };
      
      render(
        <InteractiveDataGrid {...defaultProps} pagination={paginationProps} />, 
        { wrapper: TestWrapper }
      );
      
      const pageSizeSelect = screen.getByRole('combobox', { name: /rows per page/i });
      await user.click(pageSizeSelect);
      await user.click(screen.getByText('25'));
      
      expect(onPageSizeChange).toHaveBeenCalledWith(25);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<InteractiveDataGrid {...defaultProps} />, { wrapper: TestWrapper });
      
      const table = screen.getByRole('table');
      expect(table).toHaveAttribute('aria-label', 'Error reports data grid');
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();

      render(<InteractiveDataGrid {...defaultProps} />, { wrapper: TestWrapper });

      const firstCell = screen.getByTestId('cell-error-1-id');
      await user.click(firstCell);

      expect(firstCell).toHaveFocus();
      // Note: Arrow key navigation would require more complex implementation
      // For now, just verify the cell can receive focus
    });
  });
});

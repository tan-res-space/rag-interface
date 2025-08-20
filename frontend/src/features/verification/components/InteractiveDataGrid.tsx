/**
 * Interactive Data Grid Component
 * Advanced data grid with sorting, filtering, pagination, and inline editing
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Checkbox,
  IconButton,
  TextField,
  Select,
  MenuItem,
  Box,
  Typography,
  CircularProgress,
  Button,
  Tooltip,
} from '@mui/material';
import {
  ArrowUpward as ArrowUpIcon,
  ArrowDownward as ArrowDownIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';

// Type definitions
export interface ErrorReport {
  id: string;
  dateReported: Date;
  status: 'pending' | 'in_review' | 'approved' | 'rejected';
  category: string;
  originalText: string;
  correctedText?: string;
  reportedBy: string;
  reviewedBy?: string;
  priority: 'high' | 'medium' | 'low';
  comments?: string;
  position: {
    startPosition: number;
    endPosition: number;
  };
}

export interface DataGridColumn {
  id: string;
  label: string;
  sortable: boolean;
  filterable: boolean;
  editable: boolean;
  width?: number;
  align?: 'left' | 'center' | 'right';
  format?: (value: any) => string;
}

export interface SortConfig {
  column: string;
  direction: 'asc' | 'desc';
}

export interface InteractiveDataGridProps {
  data: ErrorReport[];
  columns: DataGridColumn[];
  onSort: (column: string, direction: 'asc' | 'desc') => void;
  onFilter: (filters: Record<string, any>) => void;
  onEdit: (id: string, field: string, value: any) => void;
  onSelectionChange: (selectedIds: string[]) => void;
  loading?: boolean;
  showFilters?: boolean;
  sortBy?: SortConfig;
  selectedRows?: string[];
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onPageChange: (page: number) => void;
    onPageSizeChange: (pageSize: number) => void;
  };
}

export const InteractiveDataGrid: React.FC<InteractiveDataGridProps> = ({
  data,
  columns,
  onSort,
  onFilter,
  onEdit,
  onSelectionChange,
  loading = false,
  showFilters = false,
  sortBy,
  selectedRows = [],
  pagination,
}) => {
  const [editingCell, setEditingCell] = useState<{ rowId: string; columnId: string } | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(sortBy || null);

  // Handle column sorting
  const handleSort = useCallback((columnId: string) => {
    const column = columns.find(col => col.id === columnId);
    if (!column?.sortable) return;

    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig?.column === columnId && sortConfig.direction === 'asc') {
      direction = 'desc';
    }

    setSortConfig({ column: columnId, direction });
    onSort(columnId, direction);
  }, [columns, sortConfig, onSort]);

  // Handle filtering
  const handleFilterChange = useCallback((columnId: string, value: string) => {
    const newFilters = { ...filters, [columnId]: value };
    if (!value) {
      delete newFilters[columnId];
    }
    setFilters(newFilters);
    onFilter(newFilters);
  }, [filters, onFilter]);

  const handleClearFilters = useCallback(() => {
    setFilters({});
    onFilter({});
  }, [onFilter]);

  // Handle row selection
  const handleRowSelect = useCallback((rowId: string) => {
    const newSelection = selectedRows.includes(rowId)
      ? selectedRows.filter(id => id !== rowId)
      : [...selectedRows, rowId];
    onSelectionChange(newSelection);
  }, [selectedRows, onSelectionChange]);

  const handleSelectAll = useCallback(() => {
    const allSelected = selectedRows.length === data.length;
    onSelectionChange(allSelected ? [] : data.map(row => row.id));
  }, [selectedRows, data, onSelectionChange]);

  // Handle inline editing
  const handleCellDoubleClick = useCallback((rowId: string, columnId: string) => {
    const column = columns.find(col => col.id === columnId);
    if (column?.editable) {
      setEditingCell({ rowId, columnId });
    }
  }, [columns]);

  const handleEditComplete = useCallback((rowId: string, columnId: string, value: any) => {
    setEditingCell(null);
    onEdit(rowId, columnId, value);
  }, [onEdit]);

  // Format cell value
  const formatCellValue = useCallback((value: any, column: DataGridColumn) => {
    if (column.format) {
      return column.format(value);
    }
    if (value instanceof Date) {
      return value.toLocaleDateString();
    }
    return value?.toString() || '';
  }, []);

  // Render cell content
  const renderCellContent = useCallback((row: ErrorReport, column: DataGridColumn) => {
    const value = (row as any)[column.id];
    const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;

    if (isEditing) {
      if (column.id === 'status') {
        return (
          <Select
            value={value}
            onChange={(e) => handleEditComplete(row.id, column.id, e.target.value)}
            onBlur={() => setEditingCell(null)}
            autoFocus
            size="small"
          >
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="in_review">In Review</MenuItem>
            <MenuItem value="approved">Approved</MenuItem>
            <MenuItem value="rejected">Rejected</MenuItem>
          </Select>
        );
      } else if (column.id === 'priority') {
        return (
          <Select
            value={value}
            onChange={(e) => handleEditComplete(row.id, column.id, e.target.value)}
            onBlur={() => setEditingCell(null)}
            autoFocus
            size="small"
          >
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="low">Low</MenuItem>
          </Select>
        );
      } else {
        return (
          <TextField
            value={value || ''}
            onChange={(e) => handleEditComplete(row.id, column.id, e.target.value)}
            onBlur={() => setEditingCell(null)}
            autoFocus
            size="small"
            fullWidth
          />
        );
      }
    }

    return formatCellValue(value, column);
  }, [editingCell, handleEditComplete, formatCellValue]);

  // Memoized table rows
  const tableRows = useMemo(() => {
    return data.map((row) => (
      <TableRow
        key={row.id}
        selected={selectedRows.includes(row.id)}
        hover
      >
        <TableCell padding="checkbox">
          <Checkbox
            checked={selectedRows.includes(row.id)}
            onChange={() => handleRowSelect(row.id)}
            data-testid={`row-checkbox-${row.id}`}
          />
        </TableCell>
        {columns.map((column) => (
          <TableCell
            key={column.id}
            align={column.align || 'left'}
            style={{ width: column.width }}
            onDoubleClick={() => handleCellDoubleClick(row.id, column.id)}
            data-testid={`cell-${row.id}-${column.id}`}
            tabIndex={0}
            sx={{
              cursor: column.editable ? 'pointer' : 'default',
              '&:focus': {
                outline: '2px solid',
                outlineColor: 'primary.main',
                outlineOffset: -2,
              },
            }}
          >
            {renderCellContent(row, column)}
          </TableCell>
        ))}
      </TableRow>
    ));
  }, [data, columns, selectedRows, handleRowSelect, handleCellDoubleClick, renderCellContent]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  if (data.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <Typography variant="body1" color="text.secondary">
          No data available
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {/* Filter Controls */}
      {showFilters && (
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <FilterIcon />
            <Typography variant="h6">Filters</Typography>
            <Button
              size="small"
              onClick={handleClearFilters}
              startIcon={<ClearIcon />}
            >
              Clear Filters
            </Button>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {columns.filter(col => col.filterable).map(column => (
              <TextField
                key={column.id}
                placeholder={`Filter by ${column.label}`}
                value={filters[column.id] || ''}
                onChange={(e) => handleFilterChange(column.id, e.target.value)}
                size="small"
                sx={{ minWidth: 150 }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Data Table */}
      <TableContainer>
        <Table
          aria-label="Error reports data grid"
          stickyHeader
        >
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selectedRows.length > 0 && selectedRows.length < data.length}
                  checked={data.length > 0 && selectedRows.length === data.length}
                  onChange={handleSelectAll}
                  data-testid="select-all-checkbox"
                />
              </TableCell>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  style={{ width: column.width }}
                  sortDirection={sortConfig?.column === column.id ? sortConfig.direction : false}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      cursor: column.sortable ? 'pointer' : 'default',
                    }}
                    onClick={() => handleSort(column.id)}
                  >
                    <Typography variant="subtitle2" fontWeight="bold">
                      {column.label}
                    </Typography>
                    {column.sortable && (
                      <Box sx={{ ml: 1 }}>
                        {sortConfig?.column === column.id ? (
                          <Tooltip title={`Sorted ${sortConfig.direction}ending`}>
                            <IconButton size="small" data-testid={`sort-icon-${column.id}`}>
                              {sortConfig.direction === 'asc' ? <ArrowUpIcon /> : <ArrowDownIcon />}
                            </IconButton>
                          </Tooltip>
                        ) : (
                          <IconButton size="small" sx={{ opacity: 0.5 }}>
                            <ArrowUpIcon />
                          </IconButton>
                        )}
                      </Box>
                    )}
                  </Box>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {tableRows}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {pagination && (
        <TablePagination
          component="div"
          count={pagination.total}
          page={pagination.page}
          onPageChange={(_, newPage) => pagination.onPageChange(newPage)}
          rowsPerPage={pagination.pageSize}
          onRowsPerPageChange={(e) => pagination.onPageSizeChange(parseInt(e.target.value, 10))}
          rowsPerPageOptions={[5, 10, 25, 50]}
          aria-label="pagination navigation"
        />
      )}
    </Paper>
  );
};

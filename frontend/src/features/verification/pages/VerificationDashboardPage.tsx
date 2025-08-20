/**
 * Verification Dashboard Page
 * Demonstrates the interactive data grid and before/after comparison components
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import { InteractiveDataGrid } from '../components/InteractiveDataGrid';
import { BeforeAfterComparison } from '../components/BeforeAfterComparison';
import type { ErrorReport, DataGridColumn } from '../components/InteractiveDataGrid';
import type { TextChange } from '../components/BeforeAfterComparison';

// Sample error reports data
const sampleErrorReports: ErrorReport[] = [
  {
    id: 'error-001',
    dateReported: new Date('2024-01-15'),
    status: 'pending',
    category: 'Grammar',
    originalText: 'This are a test sentence with grammatical errors.',
    correctedText: 'This is a test sentence with grammatical corrections.',
    reportedBy: 'john.doe@example.com',
    reviewedBy: undefined,
    priority: 'high',
    comments: 'Subject-verb disagreement needs correction',
    position: { startPosition: 5, endPosition: 8 },
  },
  {
    id: 'error-002',
    dateReported: new Date('2024-01-14'),
    status: 'in_review',
    category: 'Spelling',
    originalText: 'Recieve the package from the delivery person.',
    correctedText: 'Receive the package from the delivery person.',
    reportedBy: 'jane.smith@example.com',
    reviewedBy: 'qa.supervisor@example.com',
    priority: 'medium',
    comments: 'Common spelling error - i before e rule',
    position: { startPosition: 0, endPosition: 7 },
  },
  {
    id: 'error-003',
    dateReported: new Date('2024-01-13'),
    status: 'approved',
    category: 'Punctuation',
    originalText: 'Hello world how are you today',
    correctedText: 'Hello world, how are you today?',
    reportedBy: 'bob.wilson@example.com',
    reviewedBy: 'qa.supervisor@example.com',
    priority: 'low',
    comments: 'Missing comma and question mark',
    position: { startPosition: 11, endPosition: 28 },
  },
  {
    id: 'error-004',
    dateReported: new Date('2024-01-12'),
    status: 'rejected',
    category: 'Grammar',
    originalText: 'The team have completed their work.',
    correctedText: 'The team has completed their work.',
    reportedBy: 'alice.brown@example.com',
    reviewedBy: 'qa.supervisor@example.com',
    priority: 'medium',
    comments: 'Collective noun agreement - rejected due to regional variation',
    position: { startPosition: 9, endPosition: 13 },
  },
  {
    id: 'error-005',
    dateReported: new Date('2024-01-11'),
    status: 'pending',
    category: 'Terminology',
    originalText: 'The software program is running smoothly.',
    correctedText: 'The software application is running smoothly.',
    reportedBy: 'charlie.davis@example.com',
    reviewedBy: undefined,
    priority: 'low',
    comments: 'Prefer "application" over "program" in this context',
    position: { startPosition: 13, endPosition: 20 },
  },
];

// Data grid columns configuration
const columns: DataGridColumn[] = [
  { id: 'id', label: 'ID', sortable: true, filterable: false, editable: false, width: 100 },
  { id: 'dateReported', label: 'Date', sortable: true, filterable: true, editable: false, width: 120 },
  { id: 'status', label: 'Status', sortable: true, filterable: true, editable: true, width: 120 },
  { id: 'category', label: 'Category', sortable: true, filterable: true, editable: false, width: 120 },
  { id: 'originalText', label: 'Original Text', sortable: false, filterable: true, editable: false, width: 250 },
  { id: 'correctedText', label: 'Corrected Text', sortable: false, filterable: false, editable: true, width: 250 },
  { id: 'priority', label: 'Priority', sortable: true, filterable: true, editable: true, width: 100 },
  { id: 'reportedBy', label: 'Reporter', sortable: true, filterable: true, editable: false, width: 150 },
];

const VerificationDashboardPage: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [selectedErrorReport, setSelectedErrorReport] = useState<ErrorReport | null>(null);
  const [sortedData, setSortedData] = useState(sampleErrorReports);
  const [selectedRows, setSelectedRows] = useState<string[]>([]);

  // Generate text changes for comparison
  const generateTextChanges = (original: string, corrected: string): TextChange[] => {
    // Simple diff algorithm for demonstration
    if (original === corrected) return [];
    
    // For demo purposes, create a basic substitution change
    return [
      {
        type: 'substitution',
        originalStart: 0,
        originalEnd: original.length,
        correctedStart: 0,
        correctedEnd: corrected.length,
        originalText: original,
        correctedText: corrected,
      },
    ];
  };

  // Handle data grid events
  const handleSort = (column: string, direction: 'asc' | 'desc') => {
    const sorted = [...sortedData].sort((a, b) => {
      const aValue = (a as any)[column];
      const bValue = (b as any)[column];
      
      if (direction === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    setSortedData(sorted);
  };

  const handleFilter = (filters: Record<string, any>) => {
    let filtered = sampleErrorReports;
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        filtered = filtered.filter(item => 
          String((item as any)[key]).toLowerCase().includes(value.toLowerCase())
        );
      }
    });
    
    setSortedData(filtered);
  };

  const handleEdit = (id: string, field: string, value: any) => {
    setSortedData(prev => 
      prev.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const handleSelectionChange = (selectedIds: string[]) => {
    setSelectedRows(selectedIds);
    if (selectedIds.length === 1) {
      const selected = sortedData.find(item => item.id === selectedIds[0]);
      setSelectedErrorReport(selected || null);
    } else {
      setSelectedErrorReport(null);
    }
  };

  // Handle comparison actions
  const handleApprove = () => {
    if (selectedErrorReport) {
      handleEdit(selectedErrorReport.id, 'status', 'approved');
      setSelectedErrorReport(prev => prev ? { ...prev, status: 'approved' } : null);
    }
  };

  const handleReject = () => {
    if (selectedErrorReport) {
      handleEdit(selectedErrorReport.id, 'status', 'rejected');
      setSelectedErrorReport(prev => prev ? { ...prev, status: 'rejected' } : null);
    }
  };

  // Memoized text changes
  const textChanges = useMemo(() => {
    if (!selectedErrorReport) return [];
    return generateTextChanges(selectedErrorReport.originalText, selectedErrorReport.correctedText || '');
  }, [selectedErrorReport]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Verification Dashboard
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Review and verify error reports using the interactive data grid and before/after comparison tools.
        Select a row in the grid to see the detailed comparison view.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
          <Tab label="Error Reports Grid" />
          <Tab label="Comparison View" disabled={!selectedErrorReport} />
        </Tabs>
      </Box>

      {currentTab === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Error Reports Data Grid
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Interactive grid with sorting, filtering, pagination, and inline editing. 
            Select a row to enable the comparison view.
          </Typography>
          
          <InteractiveDataGrid
            data={sortedData}
            columns={columns}
            onSort={handleSort}
            onFilter={handleFilter}
            onEdit={handleEdit}
            onSelectionChange={handleSelectionChange}
            selectedRows={selectedRows}
            showFilters={true}
            pagination={{
              page: 0,
              pageSize: 10,
              total: sortedData.length,
              onPageChange: () => {},
              onPageSizeChange: () => {},
            }}
          />
          
          {selectedRows.length > 0 && (
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>{selectedRows.length}</strong> row(s) selected. 
                {selectedRows.length === 1 && ' Click the "Comparison View" tab to see detailed analysis.'}
              </Typography>
            </Box>
          )}
        </Paper>
      )}

      {currentTab === 1 && selectedErrorReport && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Before/After Comparison
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Side-by-side comparison of original and corrected text with diff highlighting.
          </Typography>
          
          <Box sx={{ mb: 3, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Error Report Details
            </Typography>
            <Typography variant="body2">
              <strong>ID:</strong> {selectedErrorReport.id} | 
              <strong> Category:</strong> {selectedErrorReport.category} | 
              <strong> Priority:</strong> {selectedErrorReport.priority} | 
              <strong> Status:</strong> {selectedErrorReport.status}
            </Typography>
            <Typography variant="body2">
              <strong>Reporter:</strong> {selectedErrorReport.reportedBy}
              {selectedErrorReport.reviewedBy && (
                <> | <strong>Reviewer:</strong> {selectedErrorReport.reviewedBy}</>
              )}
            </Typography>
            {selectedErrorReport.comments && (
              <Typography variant="body2">
                <strong>Comments:</strong> {selectedErrorReport.comments}
              </Typography>
            )}
          </Box>

          <Divider sx={{ my: 2 }} />

          <BeforeAfterComparison
            originalText={selectedErrorReport.originalText}
            correctedText={selectedErrorReport.correctedText || ''}
            changes={textChanges}
            onApprove={handleApprove}
            onReject={handleReject}
            showActions={selectedErrorReport.status === 'pending' || selectedErrorReport.status === 'in_review'}
            highlightDifferences={true}
            disabled={selectedErrorReport.status === 'approved' || selectedErrorReport.status === 'rejected'}
          />
        </Paper>
      )}
    </Box>
  );
};

export default VerificationDashboardPage;

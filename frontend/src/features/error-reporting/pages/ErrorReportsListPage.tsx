/**
 * Error Reports List Page
 * Displays user's submitted error reports with filtering, search, and pagination
 */

import React, { useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Button,
  Grid,
  Card,
  CardContent,
  Skeleton,
  Alert,
  Tooltip,
  useTheme,
  useMediaQuery,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  Download as ExportIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useSearchErrorReportsQuery } from '@infrastructure/api/error-report-api';
import type { ErrorReport } from '@domain/types';

// Status color mapping
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'warning';
    case 'processed':
      return 'success';
    case 'archived':
      return 'default';
    case 'rejected':
      return 'error';
    default:
      return 'default';
  }
};

// Status display mapping
const getStatusDisplay = (status: string) => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'Under Review';
    case 'processed':
      return 'Completed';
    case 'archived':
      return 'Archived';
    case 'rejected':
      return 'Rejected';
    default:
      return status;
  }
};

interface FilterState {
  search: string;
  status: string;
  speakerId: string;
  clientId: string;
  bucketType: string;
  dateFrom: Date | null;
  dateTo: Date | null;
}

const ErrorReportsListPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // State management
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    status: '',
    speakerId: '',
    clientId: '',
    bucketType: '',
    dateFrom: null,
    dateTo: null,
  });

  // Build search request
  const searchRequest = useMemo(() => ({
    page: page + 1, // API uses 1-based pagination
    size: rowsPerPage,
    status: filters.status || undefined,
    speaker_id: filters.speakerId || undefined,
    client_id: filters.clientId || undefined,
    bucket_type: filters.bucketType || undefined,
    search: filters.search || undefined,
    date_from: filters.dateFrom?.toISOString() || undefined,
    date_to: filters.dateTo?.toISOString() || undefined,
  }), [page, rowsPerPage, filters]);

  // API query
  const {
    data: reportsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useSearchErrorReportsQuery(searchRequest);

  // Event handlers
  const handlePageChange = useCallback((_: unknown, newPage: number) => {
    setPage(newPage);
  }, []);

  const handleRowsPerPageChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  }, []);

  const handleFilterChange = useCallback((field: keyof FilterState, value: any) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(0); // Reset to first page when filtering
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters({
      search: '',
      status: '',
      speakerId: '',
      clientId: '',
      bucketType: '',
      dateFrom: null,
      dateTo: null,
    });
    setPage(0);
  }, []);

  const handleViewReport = useCallback((reportId: string) => {
    navigate(`/error-reporting/reports/${reportId}`);
  }, [navigate]);

  const handleNewReport = useCallback(() => {
    navigate('/error-reporting');
  }, [navigate]);

  const handleExport = useCallback(() => {
    // TODO: Implement export functionality
    console.log('Export reports with filters:', filters);
  }, [filters]);

  // Mobile card view for small screens
  const renderMobileCard = (report: ErrorReport) => (
    <Card key={report.id} sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Typography variant="h6" component="div" sx={{ fontFamily: 'monospace', fontSize: '0.9rem' }}>
            {report.id}
          </Typography>
          <Chip
            label={getStatusDisplay(report.status)}
            color={getStatusColor(report.status) as any}
            size="small"
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Submitted: {new Date(report.created_at).toLocaleDateString()}
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip label={`Speaker: ${report.speaker_id}`} size="small" variant="outlined" />
          <Chip label={`Client: ${report.client_id}`} size="small" variant="outlined" />
          <Chip
            label={`Bucket: ${report.bucket_type?.charAt(0).toUpperCase() + report.bucket_type?.slice(1) || 'Unknown'}`}
            size="small"
            variant="outlined"
            color="primary"
          />
        </Box>
        
        <Typography variant="body2" sx={{ mb: 1 }}>
          <strong>Original:</strong> {report.original_text.substring(0, 100)}...
        </Typography>
        
        <Typography variant="body2" sx={{ mb: 2 }}>
          <strong>Correction:</strong> {report.corrected_text.substring(0, 100)}...
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            size="small"
            startIcon={<ViewIcon />}
            onClick={() => handleViewReport(report.id)}
          >
            View Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            My Error Reports
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View and manage your submitted error reports. Track the status and progress of your contributions.
          </Typography>
        </Box>

        {/* Filters */}
        <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterIcon />
            Filters & Search
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            {/* Search */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search reports"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Search by text, ID, or keywords..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                size="small"
              />
            </Grid>

            {/* Status Filter */}
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  label="Status"
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="pending">Under Review</MenuItem>
                  <MenuItem value="processed">Completed</MenuItem>
                  <MenuItem value="archived">Archived</MenuItem>
                  <MenuItem value="rejected">Rejected</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Speaker ID Filter */}
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                label="Speaker ID"
                value={filters.speakerId}
                onChange={(e) => handleFilterChange('speakerId', e.target.value)}
                placeholder="Filter by speaker..."
                size="small"
              />
            </Grid>

            {/* Bucket Type Filter */}
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Bucket Type</InputLabel>
                <Select
                  value={filters.bucketType}
                  label="Bucket Type"
                  onChange={(e) => handleFilterChange('bucketType', e.target.value)}
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="beginner">Beginner</MenuItem>
                  <MenuItem value="intermediate">Intermediate</MenuItem>
                  <MenuItem value="advanced">Advanced</MenuItem>
                  <MenuItem value="expert">Expert</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Date Range */}
            <Grid item xs={12} sm={6} md={2}>
              <DatePicker
                label="From Date"
                value={filters.dateFrom}
                onChange={(date) => handleFilterChange('dateFrom', date)}
                slotProps={{ textField: { size: 'small', fullWidth: true } }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <DatePicker
                label="To Date"
                value={filters.dateTo}
                onChange={(date) => handleFilterChange('dateTo', date)}
                slotProps={{ textField: { size: 'small', fullWidth: true } }}
              />
            </Grid>
          </Grid>

          {/* Filter Actions */}
          <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
            <Button
              startIcon={<ClearIcon />}
              onClick={handleClearFilters}
              variant="outlined"
              size="small"
            >
              Clear Filters
            </Button>
            <Button
              startIcon={<RefreshIcon />}
              onClick={() => refetch()}
              variant="outlined"
              size="small"
            >
              Refresh
            </Button>
            <Button
              startIcon={<ExportIcon />}
              onClick={handleExport}
              variant="outlined"
              size="small"
            >
              Export
            </Button>
            <Button
              startIcon={<AddIcon />}
              onClick={handleNewReport}
              variant="contained"
              size="small"
            >
              New Report
            </Button>
          </Box>
        </Paper>

        {/* Error State */}
        {isError && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Failed to load error reports. {error && 'message' in error ? error.message : 'Please try again.'}
          </Alert>
        )}

        {/* Content */}
        <Paper elevation={2}>
          {isLoading ? (
            // Loading skeletons
            <Box sx={{ p: 3 }}>
              {Array.from({ length: 5 }).map((_, index) => (
                <Skeleton key={index} variant="rectangular" height={60} sx={{ mb: 1 }} />
              ))}
            </Box>
          ) : reportsData?.items?.length === 0 ? (
            // Empty state
            <Box sx={{ p: 6, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No error reports found
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {Object.values(filters).some(v => v) 
                  ? 'Try adjusting your filters or search criteria.'
                  : 'You haven\'t submitted any error reports yet.'
                }
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleNewReport}
              >
                Submit Your First Report
              </Button>
            </Box>
          ) : isMobile ? (
            // Mobile card view
            <Box sx={{ p: 2 }}>
              {reportsData?.items?.map(renderMobileCard)}
            </Box>
          ) : (
            // Desktop table view
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Report ID</TableCell>
                    <TableCell>Submitted</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Speaker ID</TableCell>
                    <TableCell>Client ID</TableCell>
                    <TableCell>Bucket Type</TableCell>
                    <TableCell>Original Text</TableCell>
                    <TableCell>Correction</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportsData?.items?.map((report) => (
                    <TableRow key={report.id} hover>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {report.id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(report.created_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusDisplay(report.status)}
                          color={getStatusColor(report.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {report.speaker_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {report.client_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={report.bucket_type?.charAt(0).toUpperCase() + report.bucket_type?.slice(1) || 'Unknown'}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 200 }}>
                          {report.original_text.substring(0, 50)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 200 }}>
                          {report.corrected_text.substring(0, 50)}...
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewReport(report.id)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Pagination */}
          {reportsData && reportsData.items && reportsData.items.length > 0 && (
            <TablePagination
              component="div"
              count={reportsData.total || 0}
              page={page}
              onPageChange={handlePageChange}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleRowsPerPageChange}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          )}
        </Paper>
      </Container>
    </LocalizationProvider>
  );
};

export default ErrorReportsListPage;

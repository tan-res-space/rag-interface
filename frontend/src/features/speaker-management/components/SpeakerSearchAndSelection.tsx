/**
 * Speaker Search and Selection Component
 * 
 * Main component for searching, filtering, and selecting speakers
 * with comprehensive filtering options and real-time search.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Paper,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Typography,
  Divider,
  Collapse,
  Grid,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
  ViewList as ViewListIcon,
  ViewModule as ViewModuleIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  searchSpeakers,
  setSearchFilters,
  clearSearchFilters,
  setCurrentPage,
  setViewMode,
  getQuickFilterOptions,
  selectSpeakers,
  selectSpeakersLoading,
  selectSpeakersError,
  selectSearchFilters,
  selectPagination,
  selectViewMode,
  selectQuickFilters,
} from '../speaker-slice';
import { SpeakerBucket, QualityTrend, SpeakerSearchFilters } from '@/domain/types/speaker';
// Note: lodash debounce would need to be installed or implemented
// For now, using a simple debounce implementation
const debounce = (func: Function, wait: number) => {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

interface SpeakerSearchAndSelectionProps {
  onSpeakerSelect?: (speakerId: string) => void;
  multiSelect?: boolean;
  showViewModeToggle?: boolean;
  showQuickFilters?: boolean;
  compact?: boolean;
}

export const SpeakerSearchAndSelection: React.FC<SpeakerSearchAndSelectionProps> = ({
  onSpeakerSelect,
  multiSelect = false,
  showViewModeToggle = true,
  showQuickFilters = true,
  compact = false,
}) => {
  const dispatch = useAppDispatch();
  
  // Redux state
  const speakers = useAppSelector(selectSpeakers);
  const loading = useAppSelector(selectSpeakersLoading);
  const error = useAppSelector(selectSpeakersError);
  const searchFilters = useAppSelector(selectSearchFilters);
  const pagination = useAppSelector(selectPagination);
  const viewMode = useAppSelector(selectViewMode);
  const quickFilters = useAppSelector(selectQuickFilters);
  
  // Local state
  const [searchText, setSearchText] = useState(searchFilters.name_pattern || '');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [localFilters, setLocalFilters] = useState<SpeakerSearchFilters>(searchFilters);

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce((filters: SpeakerSearchFilters) => {
      dispatch(setSearchFilters(filters));
      dispatch(searchSpeakers({ ...filters, page: 1, page_size: pagination.pageSize }));
    }, 300),
    [dispatch, pagination.pageSize]
  );

  // Initialize data
  useEffect(() => {
    if (quickFilters.length === 0) {
      dispatch(getQuickFilterOptions());
    }
    
    // Initial search if no speakers loaded
    if (speakers.length === 0 && !loading) {
      dispatch(searchSpeakers({ page: 1, page_size: pagination.pageSize }));
    }
  }, [dispatch, quickFilters.length, speakers.length, loading, pagination.pageSize]);

  // Handle search text change
  const handleSearchTextChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchText(value);
    
    const newFilters = { ...localFilters, name_pattern: value || undefined };
    setLocalFilters(newFilters);
    debouncedSearch(newFilters);
  };

  // Handle filter changes
  const handleFilterChange = (field: keyof SpeakerSearchFilters, value: any) => {
    const newFilters = { ...localFilters, [field]: value || undefined };
    setLocalFilters(newFilters);
    debouncedSearch(newFilters);
  };

  // Handle quick filter selection
  const handleQuickFilterSelect = (filterOption: any) => {
    const newFilters = { ...filterOption.filters };
    setLocalFilters(newFilters);
    setSearchText(newFilters.name_pattern || '');
    dispatch(setSearchFilters(newFilters));
    dispatch(searchSpeakers({ ...newFilters, page: 1, page_size: pagination.pageSize }));
  };

  // Clear all filters
  const handleClearFilters = () => {
    setSearchText('');
    setLocalFilters({});
    dispatch(clearSearchFilters());
    dispatch(searchSpeakers({ page: 1, page_size: pagination.pageSize }));
  };

  // Refresh data
  const handleRefresh = () => {
    dispatch(searchSpeakers({ ...searchFilters, page: pagination.currentPage, page_size: pagination.pageSize }));
    dispatch(getQuickFilterOptions());
  };

  // Get active filter count
  const getActiveFilterCount = () => {
    return Object.values(localFilters).filter(value => 
      value !== undefined && value !== null && value !== ''
    ).length;
  };

  return (
    <Paper elevation={1} sx={{ p: compact ? 2 : 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant={compact ? 'h6' : 'h5'} component="h2">
          Speaker Search & Selection
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {showViewModeToggle && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Tooltip title="Table View">
                <IconButton
                  size="small"
                  onClick={() => dispatch(setViewMode('table'))}
                  color={viewMode === 'table' ? 'primary' : 'default'}
                >
                  <ViewListIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Grid View">
                <IconButton
                  size="small"
                  onClick={() => dispatch(setViewMode('grid'))}
                  color={viewMode === 'grid' ? 'primary' : 'default'}
                >
                  <ViewModuleIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Analytics View">
                <IconButton
                  size="small"
                  onClick={() => dispatch(setViewMode('analytics'))}
                  color={viewMode === 'analytics' ? 'primary' : 'default'}
                >
                  <AnalyticsIcon />
                </IconButton>
              </Tooltip>
            </Box>
          )}
          
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Quick Filters */}
      {showQuickFilters && quickFilters.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Quick Filters
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {quickFilters.map((filter) => (
              <Chip
                key={filter.value}
                label={`${filter.label} (${filter.count})`}
                onClick={() => handleQuickFilterSelect(filter)}
                variant="outlined"
                size="small"
                clickable
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Search Bar */}
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          placeholder="Search speakers by name or identifier..."
          value={searchText}
          onChange={handleSearchTextChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchText && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={() => handleSearchTextChange({ target: { value: '' } } as any)}>
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
          disabled={loading}
        />
      </Box>

      {/* Filter Controls */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Button
          startIcon={<FilterIcon />}
          endIcon={showAdvancedFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          variant="outlined"
          size="small"
        >
          Advanced Filters
          {getActiveFilterCount() > 0 && (
            <Chip
              label={getActiveFilterCount()}
              size="small"
              color="primary"
              sx={{ ml: 1, height: 20, fontSize: '0.75rem' }}
            />
          )}
        </Button>

        {getActiveFilterCount() > 0 && (
          <Button
            startIcon={<ClearIcon />}
            onClick={handleClearFilters}
            variant="text"
            size="small"
            color="secondary"
          >
            Clear Filters
          </Button>
        )}
      </Box>

      {/* Advanced Filters */}
      <Collapse in={showAdvancedFilters}>
        <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
          <Grid container spacing={2}>
            {/* Bucket Filter */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Bucket</InputLabel>
                <Select
                  value={localFilters.bucket || ''}
                  onChange={(e) => handleFilterChange('bucket', e.target.value)}
                  label="Bucket"
                >
                  <MenuItem value="">All Buckets</MenuItem>
                  {Object.values(SpeakerBucket).map((bucket) => (
                    <MenuItem key={bucket} value={bucket}>
                      {bucket.replace('_', ' ')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Quality Trend Filter */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Quality Trend</InputLabel>
                <Select
                  value={localFilters.quality_trend || ''}
                  onChange={(e) => handleFilterChange('quality_trend', e.target.value)}
                  label="Quality Trend"
                >
                  <MenuItem value="">All Trends</MenuItem>
                  {Object.values(QualityTrend).map((trend) => (
                    <MenuItem key={trend} value={trend}>
                      {trend.replace('_', ' ').toUpperCase()}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* SER Score Range */}
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Min SER Score"
                type="number"
                value={localFilters.min_ser_score || ''}
                onChange={(e) => handleFilterChange('min_ser_score', parseFloat(e.target.value) || undefined)}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Max SER Score"
                type="number"
                value={localFilters.max_ser_score || ''}
                onChange={(e) => handleFilterChange('max_ser_score', parseFloat(e.target.value) || undefined)}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
              />
            </Grid>

            {/* Data Sufficiency Filter */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Data Sufficiency</InputLabel>
                <Select
                  value={localFilters.has_sufficient_data !== undefined ? localFilters.has_sufficient_data.toString() : ''}
                  onChange={(e) => handleFilterChange('has_sufficient_data', 
                    e.target.value === '' ? undefined : e.target.value === 'true'
                  )}
                  label="Data Sufficiency"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="true">Sufficient Data</MenuItem>
                  <MenuItem value="false">Insufficient Data</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
      </Collapse>

      {/* Results Summary */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">
          {loading ? 'Searching...' : `${pagination.totalCount} speakers found`}
          {getActiveFilterCount() > 0 && ` (${getActiveFilterCount()} filters applied)`}
        </Typography>
        
        {pagination.totalCount > 0 && (
          <Typography variant="body2" color="text.secondary">
            Page {pagination.currentPage} of {pagination.totalPages}
          </Typography>
        )}
      </Box>

      <Divider />
    </Paper>
  );
};

export default SpeakerSearchAndSelection;

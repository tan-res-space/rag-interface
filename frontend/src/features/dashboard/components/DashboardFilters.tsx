/**
 * Dashboard Filters Component
 * 
 * Comprehensive filtering dialog for dashboard data
 * with date ranges, speaker selection, and service filters.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,

  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  TextField,
  Autocomplete,
  ToggleButton,
  ToggleButtonGroup,
  IconButton,
  Divider,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Close as CloseIcon,
  CalendarToday as CalendarIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DashboardFilters as DashboardFiltersType } from '@/domain/types/dashboard';
import { SpeakerBucket } from '@/domain/types/speaker';

interface DashboardFiltersProps {
  open: boolean;
  onClose: () => void;
  filters: DashboardFiltersType;
  onApplyFilters?: (filters: DashboardFiltersType) => void;
}

// Mock data - in real app, this would come from API
const mockSpeakers = [
  { id: '1', name: 'Dr. John Smith', identifier: 'SPEAKER_001' },
  { id: '2', name: 'Dr. Sarah Johnson', identifier: 'SPEAKER_002' },
  { id: '3', name: 'Dr. Michael Brown', identifier: 'SPEAKER_003' },
];

const mockMTUsers = [
  { id: '1', name: 'Alice Wilson', email: 'alice@example.com' },
  { id: '2', name: 'Bob Davis', email: 'bob@example.com' },
  { id: '3', name: 'Carol Martinez', email: 'carol@example.com' },
];

const services = [
  'user_management',
  'verification',
  'rag_integration',
  'api_gateway',
];

const datePresets = [
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'Last 7 days', value: 'week' },
  { label: 'Last 30 days', value: 'month' },
  { label: 'Last 90 days', value: 'quarter' },
  { label: 'Last year', value: 'year' },
  { label: 'Custom', value: 'custom' },
];

export const DashboardFilters: React.FC<DashboardFiltersProps> = ({
  open,
  onClose,
  filters,
  onApplyFilters,
}) => {
  const [localFilters, setLocalFilters] = useState<DashboardFiltersType>(filters);

  // Update local filters when props change
  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  // Handle date preset selection
  const handleDatePresetChange = (preset: string) => {
    const now = new Date();
    let start: Date;
    let end: Date = now;

    switch (preset) {
      case 'today':
        start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        break;
      case 'yesterday':
        start = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
        end = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
        break;
      case 'week':
        start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case 'quarter':
        start = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      case 'year':
        start = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
      default:
        return; // Custom - don't change dates
    }

    setLocalFilters(prev => ({
      ...prev,
      dateRange: {
        start: start.toISOString().split('T')[0],
        end: end.toISOString().split('T')[0],
        preset,
      },
    }));
  };

  // Handle filter changes
  const handleFilterChange = (key: keyof DashboardFiltersType, value: any) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // Handle apply filters
  const handleApply = () => {
    onApplyFilters?.(localFilters);
    onClose();
  };

  // Handle clear filters
  const handleClear = () => {
    const clearedFilters: DashboardFiltersType = {
      dateRange: {
        start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end: new Date().toISOString().split('T')[0],
        preset: 'week',
      },
    };
    setLocalFilters(clearedFilters);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ sx: { height: '80vh' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterIcon color="primary" />
            <Typography variant="h6">Dashboard Filters</Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Grid container spacing={3}>
            {/* Date Range */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Date Range
              </Typography>
              
              {/* Date Presets */}
              <Box sx={{ mb: 2 }}>
                <ToggleButtonGroup
                  value={localFilters.dateRange?.preset || 'custom'}
                  exclusive
                  onChange={(_, value) => value && handleDatePresetChange(value)}
                  size="small"
                  sx={{ flexWrap: 'wrap' }}
                >
                  {datePresets.map((preset) => (
                    <ToggleButton key={preset.value} value={preset.value}>
                      {preset.label}
                    </ToggleButton>
                  ))}
                </ToggleButtonGroup>
              </Box>

              {/* Custom Date Range */}
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <DatePicker
                    label="Start Date"
                    value={localFilters.dateRange?.start ? new Date(localFilters.dateRange.start) : null}
                    onChange={(date) => {
                      if (date) {
                        handleFilterChange('dateRange', {
                          ...localFilters.dateRange,
                          start: date.toISOString().split('T')[0],
                          preset: 'custom',
                        });
                      }
                    }}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Grid>
                <Grid item xs={6}>
                  <DatePicker
                    label="End Date"
                    value={localFilters.dateRange?.end ? new Date(localFilters.dateRange.end) : null}
                    onChange={(date) => {
                      if (date) {
                        handleFilterChange('dateRange', {
                          ...localFilters.dateRange,
                          end: date.toISOString().split('T')[0],
                          preset: 'custom',
                        });
                      }
                    }}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Grid>
              </Grid>
            </Grid>

            <Grid item xs={12}>
              <Divider />
            </Grid>

            {/* Speakers */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Speakers
              </Typography>
              <Autocomplete
                multiple
                options={mockSpeakers}
                getOptionLabel={(option) => `${option.name} (${option.identifier})`}
                value={mockSpeakers.filter(speaker => localFilters.speakers?.includes(speaker.id))}
                onChange={(_, value) => {
                  handleFilterChange('speakers', value.map(speaker => speaker.id));
                }}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      variant="outlined"
                      label={option.name}
                      {...getTagProps({ index })}
                      key={option.id}
                    />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="Select speakers..."
                    variant="outlined"
                  />
                )}
              />
            </Grid>

            {/* Speaker Buckets */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Speaker Buckets
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Buckets</InputLabel>
                <Select
                  multiple
                  value={localFilters.buckets || []}
                  onChange={(e) => handleFilterChange('buckets', e.target.value)}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as SpeakerBucket[]).map((value) => (
                        <Chip
                          key={value}
                          label={value.replace('_', ' ')}
                          size="small"
                        />
                      ))}
                    </Box>
                  )}
                >
                  {Object.values(SpeakerBucket).map((bucket) => (
                    <MenuItem key={bucket} value={bucket}>
                      {bucket.replace('_', ' ')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Services */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Services
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Services</InputLabel>
                <Select
                  multiple
                  value={localFilters.services || []}
                  onChange={(e) => handleFilterChange('services', e.target.value)}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as string[]).map((value) => (
                        <Chip
                          key={value}
                          label={value.replace('_', ' ')}
                          size="small"
                        />
                      ))}
                    </Box>
                  )}
                >
                  {services.map((service) => (
                    <MenuItem key={service} value={service}>
                      {service.replace('_', ' ')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* MT Users */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                MT Users
              </Typography>
              <Autocomplete
                multiple
                options={mockMTUsers}
                getOptionLabel={(option) => `${option.name} (${option.email})`}
                value={mockMTUsers.filter(user => localFilters.mtUsers?.includes(user.id))}
                onChange={(_, value) => {
                  handleFilterChange('mtUsers', value.map(user => user.id));
                }}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      variant="outlined"
                      label={option.name}
                      {...getTagProps({ index })}
                      key={option.id}
                    />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="Select MT users..."
                    variant="outlined"
                  />
                )}
              />
            </Grid>
          </Grid>
        </LocalizationProvider>
      </DialogContent>

      <DialogActions>
        <Button
          startIcon={<ClearIcon />}
          onClick={handleClear}
          color="secondary"
        >
          Clear All
        </Button>
        
        <Button onClick={onClose}>
          Cancel
        </Button>
        
        <Button
          onClick={handleApply}
          variant="contained"
          color="primary"
        >
          Apply Filters
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DashboardFilters;

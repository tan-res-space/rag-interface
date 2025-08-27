/**
 * Speaker Table Component
 * 
 * Advanced data table for displaying speakers with sorting, selection,
 * and inline actions. Uses Material-UI DataGrid for performance.
 */

import React, { useMemo, useCallback } from 'react';
import {
  Box,
  Chip,
  IconButton,
  Tooltip,
  Typography,
  LinearProgress,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRowSelectionModel,
  GridSortModel,
  GridPaginationModel,
  GridActionsCellItem,
  GridRowParams,
} from '@mui/x-data-grid';
import {
  Visibility as ViewIcon,
  Edit as EditIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  MoreVert as MoreVertIcon,
  Assessment as AssessmentIcon,
  SwapHoriz as TransitionIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  searchSpeakers,
  setCurrentPage,
  setPageSize,
  setSorting,
  setSelectedSpeakerIds,
  selectSpeakers,
  selectSpeakersLoading,
  selectSelectedSpeakerIds,
  selectPagination,
  selectSearchFilters,
} from '../speaker-slice';
import { Speaker, SpeakerBucket, QualityTrend } from '@/domain/types/speaker';

interface SpeakerTableProps {
  onSpeakerView?: (speaker: Speaker) => void;
  onSpeakerEdit?: (speaker: Speaker) => void;
  onSpeakerAssess?: (speaker: Speaker) => void;
  onTransitionRequest?: (speaker: Speaker) => void;
  onViewHistory?: (speaker: Speaker) => void;
  selectable?: boolean;
  compact?: boolean;
}

export const SpeakerTable: React.FC<SpeakerTableProps> = ({
  onSpeakerView,
  onSpeakerEdit,
  onSpeakerAssess,
  onTransitionRequest,
  onViewHistory,
  selectable = true,
  compact = false,
}) => {
  const dispatch = useAppDispatch();
  
  // Redux state
  const speakers = useAppSelector(selectSpeakers);
  const loading = useAppSelector(selectSpeakersLoading);
  const selectedSpeakerIds = useAppSelector(selectSelectedSpeakerIds);
  const pagination = useAppSelector(selectPagination);
  const searchFilters = useAppSelector(selectSearchFilters);

  // Bucket color mapping
  const getBucketColor = (bucket: SpeakerBucket): 'error' | 'warning' | 'info' | 'success' => {
    switch (bucket) {
      case SpeakerBucket.HIGH_TOUCH: return 'error';
      case SpeakerBucket.MEDIUM_TOUCH: return 'warning';
      case SpeakerBucket.LOW_TOUCH: return 'info';
      case SpeakerBucket.NO_TOUCH: return 'success';
      default: return 'info';
    }
  };

  // Quality trend icon
  const getTrendIcon = (trend: QualityTrend) => {
    switch (trend) {
      case QualityTrend.IMPROVING:
        return <TrendingUpIcon color="success" fontSize="small" />;
      case QualityTrend.DECLINING:
        return <TrendingDownIcon color="error" fontSize="small" />;
      case QualityTrend.STABLE:
        return <TrendingFlatIcon color="info" fontSize="small" />;
      default:
        return <TrendingFlatIcon color="disabled" fontSize="small" />;
    }
  };

  // Column definitions
  const columns: GridColDef[] = useMemo(() => [
    {
      field: 'speaker_name',
      headerName: 'Speaker',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
            {params.row.speaker_name.charAt(0).toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.speaker_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.speaker_identifier}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'current_bucket',
      headerName: 'Bucket',
      width: 130,
      renderCell: (params) => (
        <Chip
          label={params.value.replace('_', ' ')}
          color={getBucketColor(params.value)}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'note_count',
      headerName: 'Notes',
      width: 80,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value.toLocaleString()}
        </Typography>
      ),
    },
    {
      field: 'average_ser_score',
      headerName: 'Avg SER',
      width: 100,
      type: 'number',
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" fontWeight="medium">
            {params.value.toFixed(1)}%
          </Typography>
          <LinearProgress
            variant="determinate"
            value={Math.min(params.value, 100)}
            sx={{ 
              width: 40, 
              height: 4,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                backgroundColor: params.value > 25 ? 'error.main' : 
                                params.value > 15 ? 'warning.main' : 'success.main'
              }
            }}
          />
        </Box>
      ),
    },
    {
      field: 'quality_trend',
      headerName: 'Trend',
      width: 80,
      renderCell: (params) => (
        <Tooltip title={params.value.replace('_', ' ').toUpperCase()}>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            {getTrendIcon(params.value)}
          </Box>
        </Tooltip>
      ),
    },
    {
      field: 'has_sufficient_data',
      headerName: 'Data',
      width: 80,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Sufficient' : 'Limited'}
          color={params.value ? 'success' : 'warning'}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'should_transition',
      headerName: 'Transition',
      width: 100,
      renderCell: (params) => (
        params.value ? (
          <Chip
            label="Recommended"
            color="info"
            size="small"
            icon={<TransitionIcon />}
          />
        ) : null
      ),
    },
    {
      field: 'updated_at',
      headerName: 'Last Updated',
      width: 120,
      renderCell: (params) => (
        <Typography variant="caption" color="text.secondary">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      ),
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 120,
      getActions: (params: GridRowParams) => {
        const actions = [
          <GridActionsCellItem
            icon={<ViewIcon />}
            label="View Details"
            onClick={() => onSpeakerView?.(params.row)}
          />,
        ];

        if (onSpeakerEdit) {
          actions.push(
            <GridActionsCellItem
              icon={<EditIcon />}
              label="Edit"
              onClick={() => onSpeakerEdit(params.row)}
            />
          );
        }

        if (onSpeakerAssess) {
          actions.push(
            <GridActionsCellItem
              icon={<AssessmentIcon />}
              label="Assess"
              onClick={() => onSpeakerAssess(params.row)}
            />
          );
        }

        return actions;
      },
    },
  ], [onSpeakerView, onSpeakerEdit, onSpeakerAssess]);

  // Handle selection change
  const handleSelectionChange = useCallback((newSelection: GridRowSelectionModel) => {
    dispatch(setSelectedSpeakerIds(newSelection as string[]));
  }, [dispatch]);

  // Handle sort change
  const handleSortChange = useCallback((sortModel: GridSortModel) => {
    if (sortModel.length > 0) {
      const { field, sort } = sortModel[0];
      dispatch(setSorting({ sortBy: field, sortOrder: sort as 'asc' | 'desc' }));
      
      // Trigger new search with sorting
      dispatch(searchSpeakers({
        ...searchFilters,
        page: pagination.currentPage,
        page_size: pagination.pageSize,
        sort_by: field,
        sort_order: sort as 'asc' | 'desc',
      }));
    }
  }, [dispatch, searchFilters, pagination]);

  // Handle pagination change
  const handlePaginationChange = useCallback((paginationModel: GridPaginationModel) => {
    const { page, pageSize } = paginationModel;
    
    if (pageSize !== pagination.pageSize) {
      dispatch(setPageSize(pageSize));
    }
    
    if (page + 1 !== pagination.currentPage) {
      dispatch(setCurrentPage(page + 1));
    }
    
    // Trigger new search with pagination
    dispatch(searchSpeakers({
      ...searchFilters,
      page: page + 1,
      page_size: pageSize,
    }));
  }, [dispatch, searchFilters, pagination]);

  // Handle row double click
  const handleRowDoubleClick = useCallback((params: GridRowParams) => {
    onSpeakerView?.(params.row);
  }, [onSpeakerView]);

  return (
    <Box sx={{ height: compact ? 400 : 600, width: '100%' }}>
      <DataGrid
        rows={speakers}
        columns={columns}
        getRowId={(row) => row.speaker_id}
        loading={loading}
        
        // Selection
        checkboxSelection={selectable}
        rowSelectionModel={selectedSpeakerIds}
        onRowSelectionModelChange={handleSelectionChange}
        
        // Sorting
        sortingMode="server"
        onSortModelChange={handleSortChange}
        
        // Pagination
        paginationMode="server"
        paginationModel={{
          page: pagination.currentPage - 1, // DataGrid uses 0-based indexing
          pageSize: pagination.pageSize,
        }}
        onPaginationModelChange={handlePaginationChange}
        rowCount={pagination.totalCount}
        pageSizeOptions={[25, 50, 100]}
        
        // Row interaction
        onRowDoubleClick={handleRowDoubleClick}
        
        // Styling
        density={compact ? 'compact' : 'standard'}
        disableRowSelectionOnClick
        sx={{
          '& .MuiDataGrid-row:hover': {
            backgroundColor: 'action.hover',
          },
          '& .MuiDataGrid-cell:focus': {
            outline: 'none',
          },
        }}
        
        // Loading overlay
        slots={{
          loadingOverlay: () => (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '100%',
              flexDirection: 'column',
              gap: 2
            }}>
              <LinearProgress sx={{ width: 200 }} />
              <Typography variant="body2" color="text.secondary">
                Loading speakers...
              </Typography>
            </Box>
          ),
        }}
      />
    </Box>
  );
};

export default SpeakerTable;

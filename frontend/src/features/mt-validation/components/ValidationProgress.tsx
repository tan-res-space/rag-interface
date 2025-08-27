/**
 * Validation Progress Component
 * 
 * Progress indicator for MT validation sessions with
 * detailed statistics and time estimates.
 */

import React from 'react';
import {
  Box,
  LinearProgress,
  Typography,
  Chip,
  Card,
  CardContent,
  Grid,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle as CompletedIcon,
  Schedule as TimeIcon,
  Speed as VelocityIcon,
} from '@mui/icons-material';

interface ValidationProgressProps {
  current: number;
  total: number;
  progress: number;
  compact?: boolean;
  showDetails?: boolean;
  estimatedTimeRemaining?: number;
  averageTimePerItem?: number;
  completedItems?: number;
}

export const ValidationProgress: React.FC<ValidationProgressProps> = ({
  current,
  total,
  progress,
  compact = false,
  showDetails = true,
  estimatedTimeRemaining,
  averageTimePerItem,
  completedItems,
}) => {
  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.round(seconds % 60);
      return `${minutes}m ${remainingSeconds}s`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  };

  const getProgressColor = (progress: number): 'primary' | 'secondary' | 'success' | 'warning' => {
    if (progress >= 90) return 'success';
    if (progress >= 70) return 'primary';
    if (progress >= 40) return 'secondary';
    return 'warning';
  };

  if (compact) {
    return (
      <Box sx={{ width: '100%' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Progress
          </Typography>
          <Typography variant="body2" fontWeight="medium">
            {current} / {total} ({progress.toFixed(1)}%)
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={progress}
          color={getProgressColor(progress)}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Box>
    );
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="h6" component="h3">
              Validation Progress
            </Typography>
            <Chip
              label={`${progress.toFixed(1)}% Complete`}
              color={getProgressColor(progress)}
              variant="outlined"
            />
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={progress}
            color={getProgressColor(progress)}
            sx={{ height: 12, borderRadius: 6, mb: 1 }}
          />
          
          <Typography variant="body2" color="text.secondary" textAlign="center">
            {current} of {total} items completed
          </Typography>
        </Box>

        {showDetails && (
          <Grid container spacing={2}>
            {/* Completed Items */}
            <Grid item xs={12} sm={4}>
              <Box sx={{ textAlign: 'center' }}>
                <CompletedIcon color="success" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h6" fontWeight="bold">
                  {completedItems || current - 1}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Items Completed
                </Typography>
              </Box>
            </Grid>

            {/* Average Time */}
            {averageTimePerItem && (
              <Grid item xs={12} sm={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <VelocityIcon color="info" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    {formatTime(averageTimePerItem)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Avg per Item
                  </Typography>
                </Box>
              </Grid>
            )}

            {/* Estimated Time Remaining */}
            {estimatedTimeRemaining && (
              <Grid item xs={12} sm={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <TimeIcon color="warning" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    {formatTime(estimatedTimeRemaining)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Est. Remaining
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
        )}

        {/* Progress Milestones */}
        {showDetails && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Milestones
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Tooltip title="25% Complete">
                <Chip
                  label="25%"
                  size="small"
                  color={progress >= 25 ? 'success' : 'default'}
                  variant={progress >= 25 ? 'filled' : 'outlined'}
                />
              </Tooltip>
              <Tooltip title="50% Complete">
                <Chip
                  label="50%"
                  size="small"
                  color={progress >= 50 ? 'success' : 'default'}
                  variant={progress >= 50 ? 'filled' : 'outlined'}
                />
              </Tooltip>
              <Tooltip title="75% Complete">
                <Chip
                  label="75%"
                  size="small"
                  color={progress >= 75 ? 'success' : 'default'}
                  variant={progress >= 75 ? 'filled' : 'outlined'}
                />
              </Tooltip>
              <Tooltip title="100% Complete">
                <Chip
                  label="100%"
                  size="small"
                  color={progress >= 100 ? 'success' : 'default'}
                  variant={progress >= 100 ? 'filled' : 'outlined'}
                />
              </Tooltip>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ValidationProgress;

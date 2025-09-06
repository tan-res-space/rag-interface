/**
 * MT Validation Metrics Component
 * 
 * Metrics overview for medical transcriptionist validation
 * with session statistics and productivity indicators.
 */

import React from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,

  Chip,
  LinearProgress,
  Alert,
  Skeleton,
  IconButton,
  Tooltip,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  PlayArrow as ActiveIcon,
  CheckCircle as CompletedIcon,
  Person as UserIcon,
  Speed as ProductivityIcon,
  Star as RatingIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { MTValidationSummary } from '@/domain/types/dashboard';

interface MTValidationMetricsProps {
  data?: MTValidationSummary;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

export const MTValidationMetrics: React.FC<MTValidationMetricsProps> = ({
  data,
  loading = false,
  error,
  onRefresh,
}) => {
  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={<Skeleton variant="text" width={200} />}
          action={<Skeleton variant="circular" width={40} height={40} />}
        />
        <CardContent>
          {[1, 2, 3].map((i) => (
            <Box key={i} sx={{ mb: 2 }}>
              <Skeleton variant="text" width="100%" />
              <Skeleton variant="rectangular" width="100%" height={8} />
            </Box>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="MT Validation Metrics" />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="MT Validation Metrics" />
        <CardContent>
          <Alert severity="info">No MT validation data available</Alert>
        </CardContent>
      </Card>
    );
  }

  const completionRate = (data.statistics.completed_sessions / data.statistics.total_sessions) * 100;

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title="MT Validation Metrics"
        subheader={`${data.statistics.total_sessions} total sessions`}
        action={
          onRefresh && (
            <Tooltip title="Refresh">
              <IconButton onClick={onRefresh} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )
        }
      />
      
      <CardContent>
        {/* Active Sessions */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Typography variant="h3" fontWeight="bold" color="primary.main">
            {data.statistics.active_sessions}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Active Sessions
          </Typography>
          {data.statistics.active_sessions > 0 && (
            <Chip
              icon={<ActiveIcon />}
              label="In Progress"
              color="primary"
              size="small"
              sx={{ mt: 1 }}
            />
          )}
        </Box>

        {/* Session Statistics */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight="bold" color="success.main">
                {data.statistics.completed_sessions}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Completed
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight="bold" color="info.main">
                {data.statistics.total_feedback_items.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Feedback Items
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Completion Rate */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              Completion Rate
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {completionRate.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={completionRate}
            color={completionRate > 90 ? 'success' : completionRate > 70 ? 'warning' : 'error'}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Average Rating */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <RatingIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Average Rating
            </Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold" color="warning.main">
            {data.quality_metrics.average_rating.toFixed(1)}/5
          </Typography>
        </Box>

        {/* MT Users */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <UserIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Active MT Users
            </Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold">
            {data.productivity.mt_user_count}
          </Typography>
        </Box>

        {/* Productivity Metrics */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <ProductivityIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Items per Hour
            </Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold">
            {data.productivity.items_per_hour.toFixed(1)}
          </Typography>
        </Box>

        {/* Bucket Recommendations */}
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Bucket Change Recommendations
          </Typography>
          <Typography variant="h6" fontWeight="bold" color="secondary.main">
            {data.quality_metrics.bucket_change_recommendations}
          </Typography>
        </Box>

        {/* Status Indicators */}
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {data.quality_metrics.average_rating > 4 && (
            <Chip
              icon={<RatingIcon />}
              label="High Quality"
              color="success"
              size="small"
              variant="outlined"
            />
          )}
          
          {data.productivity.efficiency_score > 85 && (
            <Chip
              icon={<ProductivityIcon />}
              label="High Efficiency"
              color="info"
              size="small"
              variant="outlined"
            />
          )}
          
          {data.quality_metrics.bucket_change_recommendations > 0 && (
            <Chip
              label="Pending Recommendations"
              color="warning"
              size="small"
              variant="outlined"
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default MTValidationMetrics;

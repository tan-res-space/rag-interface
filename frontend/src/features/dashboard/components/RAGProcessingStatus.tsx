/**
 * RAG Processing Status Component
 * 
 * Status overview for RAG processing pipeline
 * with job queue, performance metrics, and quality indicators.
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
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Queue as QueueIcon,
  Speed as SpeedIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { RAGProcessingSummary } from '@/domain/types/dashboard';

interface RAGProcessingStatusProps {
  data?: RAGProcessingSummary;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

export const RAGProcessingStatus: React.FC<RAGProcessingStatusProps> = ({
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
        <CardHeader title="RAG Processing Status" />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="RAG Processing Status" />
        <CardContent>
          <Alert severity="info">No RAG processing data available</Alert>
        </CardContent>
      </Card>
    );
  }

  const successRate = data.processing_stats.successful_jobs / 
    (data.processing_stats.successful_jobs + data.processing_stats.failed_jobs) * 100;

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title="RAG Processing Status"
        subheader={`${data.summary.total_speakers_processed} speakers processed`}
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
        {/* Active Jobs */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Typography variant="h3" fontWeight="bold" color="primary.main">
            {data.summary.active_jobs}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Active Jobs
          </Typography>
          {data.summary.active_jobs > 0 && (
            <Chip
              icon={<ActiveIcon />}
              label="Processing"
              color="primary"
              size="small"
              sx={{ mt: 1 }}
            />
          )}
        </Box>

        {/* Processing Statistics */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight="bold" color="success.main">
                {data.processing_stats.successful_jobs}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Successful
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight="bold" color="error.main">
                {data.processing_stats.failed_jobs}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Failed
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Success Rate */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              Success Rate
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {successRate.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={successRate}
            color={successRate > 95 ? 'success' : successRate > 85 ? 'warning' : 'error'}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Queue Length */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <QueueIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Queue Length
            </Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold">
            {data.processing_stats.queue_length}
          </Typography>
        </Box>

        {/* Average Processing Time */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <SpeedIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Avg Processing Time
            </Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold">
            {data.processing_stats.average_processing_time_minutes.toFixed(1)}m
          </Typography>
        </Box>

        {/* Quality Metrics */}
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Correction Accuracy
          </Typography>
          <Typography variant="h6" fontWeight="bold" color="info.main">
            {data.quality_metrics.correction_accuracy.toFixed(1)}%
          </Typography>
        </Box>

        {/* Status Indicators */}
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {data.processing_stats.queue_length === 0 && (
            <Chip
              label="Queue Empty"
              color="success"
              size="small"
              variant="outlined"
            />
          )}
          
          {successRate > 95 && (
            <Chip
              icon={<SuccessIcon />}
              label="High Success Rate"
              color="success"
              size="small"
              variant="outlined"
            />
          )}
          
          {data.processing_stats.failed_jobs > 10 && (
            <Chip
              icon={<ErrorIcon />}
              label="High Failure Rate"
              color="error"
              size="small"
              variant="outlined"
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default RAGProcessingStatus;

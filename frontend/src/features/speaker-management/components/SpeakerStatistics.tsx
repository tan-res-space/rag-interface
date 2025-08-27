/**
 * Speaker Statistics Component
 * 
 * Comprehensive visualization of speaker bucket statistics,
 * quality metrics, and trends with interactive charts.
 */

import React, { useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Divider,
  Alert,
  CircularProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
  SwapHoriz as TransitionIcon,
  DataUsage as DataIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  getBucketStatistics,
  selectBucketStatistics,
  selectSpeakers,
} from '../speaker-slice';
import { SpeakerBucket, BucketVisualizationData } from '@/domain/types/speaker';

interface SpeakerStatisticsProps {
  compact?: boolean;
  showRefresh?: boolean;
}

export const SpeakerStatistics: React.FC<SpeakerStatisticsProps> = ({
  compact = false,
  showRefresh = true,
}) => {
  const dispatch = useAppDispatch();
  
  // Redux state
  const bucketStatistics = useAppSelector(selectBucketStatistics);
  const speakers = useAppSelector(selectSpeakers);

  // Load statistics on mount
  useEffect(() => {
    if (!bucketStatistics) {
      dispatch(getBucketStatistics());
    }
  }, [dispatch, bucketStatistics]);

  // Bucket visualization data
  const bucketVisualizationData: BucketVisualizationData[] = useMemo(() => {
    if (!bucketStatistics) return [];

    const total = bucketStatistics.total_speakers;
    const bucketColors = {
      [SpeakerBucket.HIGH_TOUCH]: '#f44336',
      [SpeakerBucket.MEDIUM_TOUCH]: '#ff9800',
      [SpeakerBucket.LOW_TOUCH]: '#2196f3',
      [SpeakerBucket.NO_TOUCH]: '#4caf50',
    };

    return Object.entries(bucketStatistics.bucket_distribution).map(([bucket, count]) => ({
      bucket: bucket as SpeakerBucket,
      count,
      percentage: total > 0 ? (count / total) * 100 : 0,
      averageQuality: bucketStatistics.quality_metrics.average_ser_score || 0,
      trend: 'stable' as any, // Would come from actual trend data
      color: bucketColors[bucket as SpeakerBucket],
    }));
  }, [bucketStatistics]);

  // Handle refresh
  const handleRefresh = () => {
    dispatch(getBucketStatistics());
  };

  if (!bucketStatistics) {
    return (
      <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Loading statistics...
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={1} sx={{ p: compact ? 2 : 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant={compact ? 'h6' : 'h5'} component="h2">
          Speaker Statistics
        </Typography>
        
        {showRefresh && (
          <Tooltip title="Refresh Statistics">
            <IconButton size="small" onClick={handleRefresh}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {/* Total Speakers */}
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <PeopleIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" component="div" fontWeight="bold">
                {bucketStatistics.total_speakers.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Speakers
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Average SER Score */}
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <AssessmentIcon color="info" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" component="div" fontWeight="bold">
                {bucketStatistics.quality_metrics.average_ser_score.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average SER Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Pending Transitions */}
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <TransitionIcon color="warning" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" component="div" fontWeight="bold">
                {bucketStatistics.transition_metrics.pending_transitions}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pending Transitions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Data Coverage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <DataIcon color="success" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" component="div" fontWeight="bold">
                {bucketStatistics.data_quality.data_coverage_percentage.toFixed(0)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Data Coverage
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Bucket Distribution */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Bucket Distribution
        </Typography>
        
        <Grid container spacing={2}>
          {bucketVisualizationData.map((bucket) => (
            <Grid item xs={12} sm={6} md={3} key={bucket.bucket}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1" fontWeight="medium">
                      {bucket.bucket.replace('_', ' ')}
                    </Typography>
                    <Chip
                      label={`${bucket.percentage.toFixed(1)}%`}
                      size="small"
                      sx={{ backgroundColor: bucket.color, color: 'white' }}
                    />
                  </Box>
                  
                  <Typography variant="h5" fontWeight="bold" sx={{ mb: 1 }}>
                    {bucket.count.toLocaleString()}
                  </Typography>
                  
                  <LinearProgress
                    variant="determinate"
                    value={bucket.percentage}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: bucket.color,
                        borderRadius: 4,
                      },
                    }}
                  />
                  
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    {bucket.count} of {bucketStatistics.total_speakers} speakers
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Quality Metrics */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quality Metrics
        </Typography>
        
        <Grid container spacing={2}>
          {/* Quality Distribution */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                  Quality Distribution
                </Typography>
                
                {Object.entries(bucketStatistics.quality_metrics.quality_distribution).map(([level, count]) => (
                  <Box key={level} sx={{ mb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {level} Quality
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {count}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(count / bucketStatistics.total_speakers) * 100}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Improvement Trends */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                  Improvement Trends
                </Typography>
                
                {Object.entries(bucketStatistics.quality_metrics.improvement_trends).map(([trend, count]) => (
                  <Box key={trend} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {trend === 'improving' && <TrendingUpIcon color="success" fontSize="small" />}
                      {trend === 'declining' && <TrendingDownIcon color="error" fontSize="small" />}
                      {trend === 'stable' && <TrendingFlatIcon color="info" fontSize="small" />}
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {trend}
                      </Typography>
                    </Box>
                    <Typography variant="body2" fontWeight="medium">
                      {count}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Transition Metrics */}
      <Box>
        <Typography variant="h6" gutterBottom>
          Transition Metrics
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  {bucketStatistics.transition_metrics.pending_transitions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Requests
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="info.main">
                  {bucketStatistics.transition_metrics.recent_transitions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Recent Transitions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {bucketStatistics.transition_metrics.success_rate.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Success Rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Data Quality Alert */}
      {bucketStatistics.data_quality.data_coverage_percentage < 80 && (
        <Alert severity="warning" sx={{ mt: 3 }}>
          <Typography variant="body2">
            Data coverage is below 80%. Consider processing more historical data to improve 
            speaker assessment accuracy.
          </Typography>
        </Alert>
      )}
    </Paper>
  );
};

export default SpeakerStatistics;

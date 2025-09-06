/**
 * Speaker Bucket Overview Component
 * 
 * Comprehensive overview of speaker bucket distribution
 * with pie chart and detailed statistics.
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
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip as RechartsTooltip,
} from 'recharts';
import {
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  TrendingFlat as TrendFlatIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { SpeakerBucketStats } from '@/domain/types/dashboard';
import { SpeakerBucket } from '@/domain/types/speaker';

interface SpeakerBucketOverviewProps {
  data?: SpeakerBucketStats;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

// Color mapping for speaker buckets
const BUCKET_COLORS = {
  [SpeakerBucket.NO_TOUCH]: '#4caf50',
  [SpeakerBucket.LOW_TOUCH]: '#8bc34a',
  [SpeakerBucket.MEDIUM_TOUCH]: '#ff9800',
  [SpeakerBucket.HIGH_TOUCH]: '#f44336',
};

const BUCKET_LABELS = {
  [SpeakerBucket.NO_TOUCH]: 'No Touch',
  [SpeakerBucket.LOW_TOUCH]: 'Low Touch',
  [SpeakerBucket.MEDIUM_TOUCH]: 'Medium Touch',
  [SpeakerBucket.HIGH_TOUCH]: 'High Touch',
};

export const SpeakerBucketOverview: React.FC<SpeakerBucketOverviewProps> = ({
  data,
  loading = false,
  error,
  onRefresh,
}) => {
  // Prepare chart data
  const chartData = data ? Object.entries(data.bucket_distribution).map(([bucket, count]) => ({
    name: BUCKET_LABELS[bucket as SpeakerBucket],
    value: count,
    color: BUCKET_COLORS[bucket as SpeakerBucket],
    bucket: bucket,
  })) : [];

  // Custom tooltip for pie chart
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = ((data.value / (chartData.reduce((sum, item) => sum + item.value, 0))) * 100).toFixed(1);
      
      return (
        <Box
          sx={{
            backgroundColor: 'background.paper',
            p: 1,
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            boxShadow: 2,
          }}
        >
          <Typography variant="body2" fontWeight="bold">
            {data.payload.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {data.value} speakers ({percentage}%)
          </Typography>
        </Box>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={<Skeleton variant="text" width={200} />}
          action={<Skeleton variant="circular" width={40} height={40} />}
        />
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Skeleton variant="circular" width={200} height={200} sx={{ mx: 'auto' }} />
            </Grid>
            <Grid item xs={12} md={6}>
              {[1, 2, 3, 4].map((i) => (
                <Box key={i} sx={{ mb: 2 }}>
                  <Skeleton variant="text" width="100%" />
                  <Skeleton variant="rectangular" width="100%" height={8} />
                </Box>
              ))}
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="Speaker Bucket Overview" />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="Speaker Bucket Overview" />
        <CardContent>
          <Alert severity="info">No speaker data available</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title="Speaker Bucket Overview"
        subheader={`${data.total_speakers} total speakers`}
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
        <Grid container spacing={2}>
          {/* Pie Chart */}
          <Grid item xs={12} md={6}>
            <Box sx={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Grid>

          {/* Statistics */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {/* Bucket Distribution */}
              {chartData.map((bucket) => {
                const percentage = ((bucket.value / data.total_speakers) * 100).toFixed(1);
                return (
                  <Box key={bucket.bucket}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" fontWeight="medium">
                        {bucket.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {bucket.value} ({percentage}%)
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={parseFloat(percentage)}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: bucket.color,
                        },
                      }}
                    />
                  </Box>
                );
              })}
            </Box>
          </Grid>

          {/* Quality Metrics */}
          <Grid item xs={12}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Quality Metrics
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="primary.main">
                      {data.quality_metrics.average_ser_score.toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Average SER Score
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="success.main">
                      {data.transition_metrics.pending_transitions}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Pending Transitions
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="info.main">
                      {data.transition_metrics.success_rate.toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Success Rate
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="warning.main">
                      {data.data_quality.data_coverage_percentage.toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Data Coverage
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </Grid>

          {/* Transition Insights */}
          {data.transition_metrics.pending_transitions > 0 && (
            <Grid item xs={12}>
              <Alert severity="info" icon={<InfoIcon />}>
                <Typography variant="body2">
                  {data.transition_metrics.pending_transitions} speakers are pending bucket transitions. 
                  Review the transition queue for approval decisions.
                </Typography>
              </Alert>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SpeakerBucketOverview;

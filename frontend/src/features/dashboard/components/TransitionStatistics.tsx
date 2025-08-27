/**
 * Transition Statistics Component
 * 
 * Statistics and trends for speaker bucket transitions
 * with approval rates and impact analysis.
 */

import React from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  Skeleton,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  SwapHoriz as TransitionIcon,
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  CheckCircle as ApprovedIcon,
  Cancel as RejectedIcon,
  Pending as PendingIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { TransitionStatisticsSummary } from '@/domain/types/dashboard';

interface TransitionStatisticsProps {
  data?: TransitionStatisticsSummary;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

export const TransitionStatistics: React.FC<TransitionStatisticsProps> = ({
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
        <CardHeader title="Transition Statistics" />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="Transition Statistics" />
        <CardContent>
          <Alert severity="info">No transition data available</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title="Transition Statistics"
        subheader={`${data.statistics.total_requests} total requests`}
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
        {/* Pending Requests */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Typography variant="h3" fontWeight="bold" color="warning.main">
            {data.statistics.pending_requests}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Pending Requests
          </Typography>
          {data.statistics.pending_requests > 0 && (
            <Chip
              icon={<PendingIcon />}
              label="Needs Review"
              color="warning"
              size="small"
              sx={{ mt: 1 }}
            />
          )}
        </Box>

        {/* Request Statistics */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight="bold" color="success.main">
                {data.statistics.approved_requests}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Approved
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight="bold" color="error.main">
                {data.statistics.rejected_requests}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Rejected
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Approval Rate */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              Approval Rate
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {data.statistics.approval_rate.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={data.statistics.approval_rate}
            color={data.statistics.approval_rate > 80 ? 'success' : data.statistics.approval_rate > 60 ? 'warning' : 'error'}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Impact Metrics */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Speakers Promoted
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendUpIcon fontSize="small" color="success" />
            <Typography variant="h6" fontWeight="bold" color="success.main">
              {data.impact.speakers_promoted}
            </Typography>
          </Box>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Speakers Demoted
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendDownIcon fontSize="small" color="error" />
            <Typography variant="h6" fontWeight="bold" color="error.main">
              {data.impact.speakers_demoted}
            </Typography>
          </Box>
        </Box>

        {/* Quality Correlation */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Quality Improvement Correlation
          </Typography>
          <Typography variant="h6" fontWeight="bold" color="info.main">
            {data.impact.quality_improvement_correlation.toFixed(2)}
          </Typography>
        </Box>

        {/* Cost Savings */}
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Estimated Cost Savings
          </Typography>
          <Typography variant="h6" fontWeight="bold" color="secondary.main">
            ${data.impact.cost_savings_estimate.toLocaleString()}
          </Typography>
        </Box>

        {/* Status Indicators */}
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {data.statistics.approval_rate > 80 && (
            <Chip
              icon={<ApprovedIcon />}
              label="High Approval Rate"
              color="success"
              size="small"
              variant="outlined"
            />
          )}
          
          {data.impact.quality_improvement_correlation > 0.7 && (
            <Chip
              label="Strong Quality Correlation"
              color="info"
              size="small"
              variant="outlined"
            />
          )}
          
          {data.statistics.pending_requests > 10 && (
            <Chip
              icon={<PendingIcon />}
              label="High Pending Volume"
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

export default TransitionStatistics;

/**
 * Quick Metrics Bar Component
 * 
 * Horizontal bar displaying key metrics with trends
 * and status indicators.
 */

import React from 'react';
import {
  Box,
  Paper,
  Grid,
  Typography,
  Chip,
  Skeleton,
  Icon,
} from '@mui/material';
import {
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  TrendingFlat as TrendFlatIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
  PlayArrow as PlayIcon,
  SwapHoriz as SwapIcon,
} from '@mui/icons-material';
import { QuickMetric } from '@/domain/types/dashboard';

interface QuickMetricsBarProps {
  metrics: QuickMetric[];
  loading?: boolean;
}

interface MetricCardProps {
  metric: QuickMetric;
}

const MetricCard: React.FC<MetricCardProps> = ({ metric }) => {
  const getIcon = (iconName?: string) => {
    switch (iconName) {
      case 'people': return <PeopleIcon />;
      case 'assessment': return <AssessmentIcon />;
      case 'play_arrow': return <PlayIcon />;
      case 'swap_horiz': return <SwapIcon />;
      default: return <AssessmentIcon />;
    }
  };

  const getTrendIcon = (direction?: 'up' | 'down' | 'stable') => {
    switch (direction) {
      case 'up': return <TrendUpIcon color="success" fontSize="small" />;
      case 'down': return <TrendDownIcon color="error" fontSize="small" />;
      case 'stable': return <TrendFlatIcon color="info" fontSize="small" />;
      default: return null;
    }
  };

  const getStatusColor = (status?: 'good' | 'warning' | 'critical') => {
    switch (status) {
      case 'good': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'primary';
    }
  };

  return (
    <Paper
      elevation={1}
      sx={{
        p: 2,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        borderLeft: 4,
        borderLeftColor: `${metric.color || 'primary'}.main`,
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          elevation: 3,
          transform: 'translateY(-2px)',
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ color: `${metric.color || 'primary'}.main` }}>
            {getIcon(metric.icon)}
          </Box>
          <Typography variant="body2" color="text.secondary" fontWeight="medium">
            {metric.label}
          </Typography>
        </Box>
        
        {metric.status && (
          <Chip
            size="small"
            label={metric.status.toUpperCase()}
            color={getStatusColor(metric.status)}
            variant="outlined"
          />
        )}
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 1 }}>
        <Typography variant="h4" fontWeight="bold" color={`${metric.color || 'primary'}.main`}>
          {metric.value}
        </Typography>
        {metric.unit && (
          <Typography variant="body2" color="text.secondary">
            {metric.unit}
          </Typography>
        )}
      </Box>

      {metric.trend && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {getTrendIcon(metric.trend.direction)}
          <Typography
            variant="caption"
            color={
              metric.trend.direction === 'up' ? 'success.main' :
              metric.trend.direction === 'down' ? 'error.main' : 'text.secondary'
            }
            fontWeight="medium"
          >
            {metric.trend.direction === 'up' ? '+' : metric.trend.direction === 'down' ? '-' : ''}
            {metric.trend.percentage.toFixed(1)}% {metric.trend.period}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

const MetricSkeleton: React.FC = () => (
  <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
      <Skeleton variant="circular" width={24} height={24} />
      <Skeleton variant="text" width={100} />
    </Box>
    <Skeleton variant="text" width={80} height={40} sx={{ mb: 1 }} />
    <Skeleton variant="text" width={120} height={20} />
  </Paper>
);

export const QuickMetricsBar: React.FC<QuickMetricsBarProps> = ({
  metrics,
  loading = false,
}) => {
  if (loading) {
    return (
      <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
        <Grid container spacing={2}>
          {[1, 2, 3, 4].map((index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <MetricSkeleton />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (!metrics || metrics.length === 0) {
    return (
      <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
        <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            No metrics available
          </Typography>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
      <Grid container spacing={2}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <MetricCard metric={metric} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default QuickMetricsBar;

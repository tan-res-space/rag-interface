/**
 * SER Metrics Chart Component
 * 
 * Interactive chart showing SER metrics trends over time
 * with quality distribution and performance indicators.
 */

import React, { useState } from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  Skeleton,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from 'recharts';
import {
  TrendingUp as TrendUpIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  ShowChart as ChartIcon,
} from '@mui/icons-material';
import { SERMetricsSummary } from '@/domain/types/dashboard';

interface SERMetricsChartProps {
  data?: SERMetricsSummary;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

type ChartType = 'trend' | 'improvement' | 'distribution';

export const SERMetricsChart: React.FC<SERMetricsChartProps> = ({
  data,
  loading = false,
  error,
  onRefresh,
}) => {
  const [chartType, setChartType] = useState<ChartType>('trend');

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            backgroundColor: 'background.paper',
            p: 1.5,
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            boxShadow: 2,
          }}
        >
          <Typography variant="body2" fontWeight="bold" gutterBottom>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Typography
              key={index}
              variant="body2"
              sx={{ color: entry.color }}
            >
              {entry.name}: {entry.value.toFixed(2)}
              {entry.dataKey.includes('percentage') ? '%' : ''}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  const renderChart = () => {
    if (!data) return null;

    switch (chartType) {
      case 'trend':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trends.daily_calculations}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <RechartsTooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="average_score"
                stroke="#2196f3"
                strokeWidth={2}
                dot={{ fill: '#2196f3', strokeWidth: 2, r: 4 }}
                name="Average SER Score"
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#4caf50"
                strokeWidth={2}
                dot={{ fill: '#4caf50', strokeWidth: 2, r: 4 }}
                name="Calculations Count"
                yAxisId="right"
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'improvement':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data.trends.quality_improvement_over_time}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <RechartsTooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="improvement_percentage"
                stroke="#ff9800"
                fill="#ff9800"
                fillOpacity={0.3}
                name="Quality Improvement"
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'distribution':
        const distributionData = Object.entries(data.summary.quality_distribution).map(([quality, count]) => ({
          quality: quality.charAt(0).toUpperCase() + quality.slice(1),
          count,
          percentage: ((count / data.summary.total_calculations) * 100).toFixed(1),
        }));

        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distributionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="quality" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <RechartsTooltip content={<CustomTooltip />} />
              <Bar
                dataKey="count"
                fill="#9c27b0"
                name="Count"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={<Skeleton variant="text" width={200} />}
          action={<Skeleton variant="circular" width={40} height={40} />}
        />
        <CardContent>
          <Skeleton variant="rectangular" width="100%" height={300} />
          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} variant="rectangular" width={100} height={40} />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="SER Metrics Trends" />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader title="SER Metrics Trends" />
        <CardContent>
          <Alert severity="info">No SER metrics data available</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title="SER Metrics Trends"
        subheader={`${data.summary.total_calculations.toLocaleString()} total calculations`}
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {onRefresh && (
              <Tooltip title="Refresh">
                <IconButton onClick={onRefresh} size="small">
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        }
      />
      
      <CardContent>
        {/* Chart Type Toggle */}
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
          <ToggleButtonGroup
            value={chartType}
            exclusive
            onChange={(_, newType) => newType && setChartType(newType)}
            size="small"
          >
            <ToggleButton value="trend">
              <ChartIcon sx={{ mr: 1 }} />
              Trends
            </ToggleButton>
            <ToggleButton value="improvement">
              <TrendUpIcon sx={{ mr: 1 }} />
              Improvement
            </ToggleButton>
            <ToggleButton value="distribution">
              <AssessmentIcon sx={{ mr: 1 }} />
              Distribution
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Chart */}
        <Box sx={{ mb: 3 }}>
          {renderChart()}
        </Box>

        {/* Summary Statistics */}
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight="bold" color="primary.main">
                {data.summary.average_ser_score.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Average SER Score
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight="bold" color="success.main">
                {data.summary.improvement_rate.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Improvement Rate
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight="bold" color="info.main">
                {data.performance.calculation_speed_ms}ms
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Avg Calculation Speed
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight="bold" color="warning.main">
                {data.performance.error_rate.toFixed(2)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Error Rate
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Performance Indicators */}
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            icon={<SpeedIcon />}
            label={`${data.performance.batch_processing_efficiency.toFixed(1)}% Batch Efficiency`}
            color="info"
            variant="outlined"
            size="small"
          />
          
          {data.performance.error_rate < 1 && (
            <Chip
              label="Low Error Rate"
              color="success"
              variant="outlined"
              size="small"
            />
          )}
          
          {data.summary.improvement_rate > 10 && (
            <Chip
              icon={<TrendUpIcon />}
              label="High Improvement Rate"
              color="success"
              variant="outlined"
              size="small"
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default SERMetricsChart;

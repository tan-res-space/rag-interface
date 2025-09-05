/**
 * Bucket Progression Analytics Component
 * Displays analytics and visualizations for bucket progression
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Divider,
  useTheme
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import type { BucketStatistics, BucketChangeLog } from '@domain/types';
import { speakerProfileService, bucketProgressionHelpers } from '@infrastructure/services/speakerProfileService';

interface BucketProgressionAnalyticsProps {
  speakerId?: string;
  showGlobalStats?: boolean;
}

export const BucketProgressionAnalytics: React.FC<BucketProgressionAnalyticsProps> = ({
  speakerId,
  showGlobalStats = true
}) => {
  const theme = useTheme();

  // Fetch global bucket statistics
  const {
    data: bucketStats,
    isLoading: statsLoading
  } = useQuery({
    queryKey: ['bucketStatistics'],
    queryFn: () => speakerProfileService.getBucketStatistics(),
    enabled: showGlobalStats,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Fetch speaker-specific bucket history
  const {
    data: bucketHistory,
    isLoading: historyLoading
  } = useQuery({
    queryKey: ['bucketHistory', speakerId],
    queryFn: () => speakerProfileService.getBucketChangeHistory(speakerId!, 50),
    enabled: !!speakerId,
    staleTime: 5 * 60 * 1000,
  });

  // Prepare data for charts
  const preparePieChartData = () => {
    if (!bucketStats) return [];
    
    return Object.entries(bucketStats.bucket_distribution).map(([bucket, data]) => ({
      name: data.info.label,
      value: data.count,
      percentage: data.percentage,
      color: data.info.color,
      icon: data.info.icon
    }));
  };

  const prepareProgressionTrendData = () => {
    if (!bucketHistory) return [];
    
    // Group changes by month
    const monthlyData: Record<string, { promotions: number; demotions: number; month: string }> = {};
    
    bucketHistory.history.forEach(change => {
      const date = new Date(change.changed_at);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = {
          month: date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' }),
          promotions: 0,
          demotions: 0
        };
      }
      
      const isPromotion = bucketProgressionHelpers.isPromotion(
        change.old_bucket.type as any,
        change.new_bucket.type as any
      );
      
      if (isPromotion) {
        monthlyData[monthKey].promotions++;
      } else {
        monthlyData[monthKey].demotions++;
      }
    });
    
    return Object.values(monthlyData).sort((a, b) => a.month.localeCompare(b.month));
  };

  const pieChartData = preparePieChartData();
  const trendData = prepareProgressionTrendData();

  return (
    <Box>
      {/* Global Statistics */}
      {showGlobalStats && bucketStats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Bucket Distribution Analytics
            </Typography>
          </Grid>
          
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="primary" gutterBottom>
                  {bucketStats.total_profiles}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Speakers
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="success.main" gutterBottom>
                  {bucketStats.change_statistics.total_bucket_changes}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Progressions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="info.main" gutterBottom>
                  {bucketStats.change_statistics.recent_bucket_changes}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Recent Changes (30d)
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="warning.main" gutterBottom>
                  {bucketStats.change_statistics.average_changes_per_profile.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Changes/Speaker
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Bucket Distribution Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Speaker Distribution by Bucket
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, name) => [`${value} speakers`, name]} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Bucket Level Breakdown */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Bucket Level Breakdown
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {Object.entries(bucketStats.bucket_distribution).map(([bucket, data]) => (
                    <Box key={bucket} sx={{ mb: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2">
                            {data.info.icon} {data.info.label}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {data.count} ({data.percentage.toFixed(1)}%)
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={data.percentage}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: theme.palette.grey[200],
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: data.info.color,
                            borderRadius: 4
                          }
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Speaker-Specific Analytics */}
      {speakerId && bucketHistory && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Speaker Progression History
            </Typography>
          </Grid>

          {/* Progression Trend Chart */}
          {trendData.length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Monthly Progression Trend
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="promotions" fill={theme.palette.success.main} name="Promotions" />
                      <Bar dataKey="demotions" fill={theme.palette.warning.main} name="Demotions" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Recent Changes Timeline */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Bucket Changes
                </Typography>
                {bucketHistory.history.length > 0 ? (
                  <Box>
                    {bucketHistory.history.slice(0, 10).map((change, index) => (
                      <Box key={change.change_id}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" py={2}>
                          <Box display="flex" alignItems="center" gap={2}>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Chip
                                label={`${bucketProgressionHelpers.getBucketIcon(change.old_bucket.type)} ${change.old_bucket.label}`}
                                size="small"
                                variant="outlined"
                              />
                              <Typography variant="body2" color="text.secondary">→</Typography>
                              <Chip
                                label={`${bucketProgressionHelpers.getBucketIcon(change.new_bucket.type)} ${change.new_bucket.label}`}
                                size="small"
                                sx={{
                                  backgroundColor: change.new_bucket.info?.color || bucketProgressionHelpers.getBucketColor(change.new_bucket.type),
                                  color: 'white'
                                }}
                              />
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                              {change.change_reason}
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(change.changed_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                        {index < Math.min(bucketHistory.history.length - 1, 9) && <Divider />}
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No bucket changes recorded yet.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

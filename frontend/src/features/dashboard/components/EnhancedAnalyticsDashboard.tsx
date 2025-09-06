/**
 * Enhanced Analytics Dashboard Component
 * 
 * Provides comprehensive analytics for the quality-based bucket management
 * system with enhanced metadata insights.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,

  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
} from 'recharts';

interface BucketDistribution {
  bucketType: string;
  speakerCount: number;
  percentage: number;
  avgRectificationRate: number;
  avgDaysInBucket: number;
}

interface MetadataInsights {
  totalErrorsAnalyzed: number;
  audioQualityDistribution: Record<string, { count: number; percentage: number }>;
  speakerClarityDistribution: Record<string, { count: number; percentage: number }>;
  backgroundNoiseDistribution: Record<string, { count: number; percentage: number }>;
  speakerCountDistribution: Record<string, { count: number; percentage: number }>;
  overlappingSpeechFrequency: number;
  specializedKnowledgeFrequency: number;
  complexityScoreDistribution: Record<string, { count: number; percentage: number }>;
}

interface PerformanceMetrics {
  performanceTrends: Record<string, Record<string, { avgRectificationRate: number; speakerCount: number }>>;
  highPerformersCount: number;
  speakersNeedingAttentionCount: number;
  speakersForReassessmentCount: number;
  averagePerformanceByBucket: Record<string, { avgRectificationRate: number; avgTotalErrors: number; speakerCount: number }>;
}

interface VerificationMetrics {
  totalJobs: number;
  verifiedJobs: number;
  pendingJobs: number;
  rectifiedCount: number;
  notRectifiedCount: number;
  partiallyRectifiedCount: number;
  rectificationRate: number;
  averageCorrectionsPerJob: number;
  averageConfidence: number;
  jobsNeedingReview: number;
}

interface EnhancedAnalyticsDashboardProps {
  bucketDistribution: BucketDistribution[];
  metadataInsights: MetadataInsights;
  performanceMetrics: PerformanceMetrics;
  verificationMetrics: VerificationMetrics;
  timePeriod: string;
  onTimePeriodChange: (period: string) => void;
  loading?: boolean;
}

const BUCKET_COLORS = {
  no_touch: '#4caf50',
  low_touch: '#2196f3',
  medium_touch: '#ff9800',
  high_touch: '#f44336',
};

const TIME_PERIODS = [
  { value: 'last_7_days', label: 'Last 7 Days' },
  { value: 'last_30_days', label: 'Last 30 Days' },
  { value: 'last_90_days', label: 'Last 90 Days' },
  { value: 'last_6_months', label: 'Last 6 Months' },
  { value: 'last_year', label: 'Last Year' },
];

export const EnhancedAnalyticsDashboard: React.FC<EnhancedAnalyticsDashboardProps> = ({
  bucketDistribution,
  metadataInsights,
  performanceMetrics,
  verificationMetrics,
  timePeriod,
  onTimePeriodChange,
  loading = false,
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

  const prepareBucketDistributionData = () => {
    return bucketDistribution.map(bucket => ({
      name: bucket.bucketType.replace('_', ' ').toUpperCase(),
      speakers: bucket.speakerCount,
      percentage: bucket.percentage,
      rectificationRate: bucket.avgRectificationRate * 100,
      fill: BUCKET_COLORS[bucket.bucketType as keyof typeof BUCKET_COLORS],
    }));
  };

  const prepareMetadataDistributionData = (distribution: Record<string, { count: number; percentage: number }>) => {
    return Object.entries(distribution).map(([key, value]) => ({
      name: key.replace('_', ' ').toUpperCase(),
      count: value.count,
      percentage: value.percentage,
    }));
  };

  const preparePerformanceTrendsData = () => {
    const trends = performanceMetrics.performanceTrends;
    return Object.entries(trends).map(([week, buckets]) => ({
      week: new Date(week).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      ...Object.fromEntries(
        Object.entries(buckets).map(([bucket, data]) => [
          bucket.replace('_', ' '),
          data.avgRectificationRate * 100
        ])
      ),
    }));
  };

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 1 }}>
          Loading analytics dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header Controls */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Enhanced Analytics Dashboard</Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Time Period</InputLabel>
          <Select
            value={timePeriod}
            onChange={(e) => onTimePeriodChange(e.target.value)}
            label="Time Period"
          >
            {TIME_PERIODS.map((period) => (
              <MenuItem key={period.value} value={period.value}>
                {period.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Total Speakers
              </Typography>
              <Typography variant="h3">
                {bucketDistribution.reduce((sum, bucket) => sum + bucket.speakerCount, 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Errors Analyzed
              </Typography>
              <Typography variant="h3">
                {metadataInsights.totalErrorsAnalyzed.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                High Performers
              </Typography>
              <Typography variant="h3">
                {performanceMetrics.highPerformersCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Verification Rate
              </Typography>
              <Typography variant="h3">
                {formatPercentage(verificationMetrics.rectificationRate * 100)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for Different Views */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label="Bucket Overview" />
            <Tab label="Metadata Insights" />
            <Tab label="Performance Trends" />
            <Tab label="Verification Metrics" />
          </Tabs>
        </Box>

        <CardContent>
          {/* Bucket Overview Tab */}
          {activeTab === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Bucket Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={prepareBucketDistributionData()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="speakers"
                    >
                      {prepareBucketDistributionData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Rectification Rates by Bucket
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prepareBucketDistributionData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Rectification Rate']} />
                    <Bar dataKey="rectificationRate" fill="#2196f3" />
                  </BarChart>
                </ResponsiveContainer>
              </Grid>
            </Grid>
          )}

          {/* Metadata Insights Tab */}
          {activeTab === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Audio Quality Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={prepareMetadataDistributionData(metadataInsights.audioQualityDistribution)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="percentage" fill="#4caf50" />
                  </BarChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Speaker Clarity Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={prepareMetadataDistributionData(metadataInsights.speakerClarityDistribution)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="percentage" fill="#2196f3" />
                  </BarChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Enhanced Metadata Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="warning.main">
                        {formatPercentage(metadataInsights.overlappingSpeechFrequency)}
                      </Typography>
                      <Typography variant="body2">
                        Overlapping Speech
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {formatPercentage(metadataInsights.specializedKnowledgeFrequency)}
                      </Typography>
                      <Typography variant="body2">
                        Specialized Knowledge
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          )}

          {/* Performance Trends Tab */}
          {activeTab === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Performance Trends Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={preparePerformanceTrendsData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="week" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Rectification Rate']} />
                    <Legend />
                    <Line type="monotone" dataKey="no touch" stroke="#4caf50" strokeWidth={2} />
                    <Line type="monotone" dataKey="low touch" stroke="#2196f3" strokeWidth={2} />
                    <Line type="monotone" dataKey="medium touch" stroke="#ff9800" strokeWidth={2} />
                    <Line type="monotone" dataKey="high touch" stroke="#f44336" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Performance Alerts
                </Typography>
                <Grid container spacing={2}>
                  {performanceMetrics.speakersNeedingAttentionCount > 0 && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Alert severity="warning">
                        <Typography variant="subtitle2">
                          {performanceMetrics.speakersNeedingAttentionCount} speakers need attention
                        </Typography>
                      </Alert>
                    </Grid>
                  )}
                  {performanceMetrics.speakersForReassessmentCount > 0 && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Alert severity="info">
                        <Typography variant="subtitle2">
                          {performanceMetrics.speakersForReassessmentCount} speakers ready for reassessment
                        </Typography>
                      </Alert>
                    </Grid>
                  )}
                </Grid>
              </Grid>
            </Grid>
          )}

          {/* Verification Metrics Tab */}
          {activeTab === 3 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Verification Status
                </Typography>
                <Box mb={2}>
                  <Typography variant="body2">
                    Verified Jobs: {verificationMetrics.verifiedJobs} / {verificationMetrics.totalJobs}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(verificationMetrics.verifiedJobs / verificationMetrics.totalJobs) * 100}
                    sx={{ mt: 1 }}
                  />
                </Box>
                <Box mb={2}>
                  <Typography variant="body2">
                    Rectification Rate: {formatPercentage(verificationMetrics.rectificationRate * 100)}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={verificationMetrics.rectificationRate * 100}
                    color="success"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Verification Quality
                </Typography>
                <Box mb={2}>
                  <Typography variant="body2">
                    Average Confidence: {formatPercentage(verificationMetrics.averageConfidence * 100)}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={verificationMetrics.averageConfidence * 100}
                    color="info"
                    sx={{ mt: 1 }}
                  />
                </Box>
                <Box mb={2}>
                  <Typography variant="body2">
                    Jobs Needing Review: {verificationMetrics.jobsNeedingReview}
                  </Typography>
                  {verificationMetrics.jobsNeedingReview > 0 && (
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      {verificationMetrics.jobsNeedingReview} jobs require manual review
                    </Alert>
                  )}
                </Box>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

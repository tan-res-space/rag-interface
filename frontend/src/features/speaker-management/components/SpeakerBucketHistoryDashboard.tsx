/**
 * Speaker Bucket History Dashboard Component
 * 
 * Displays comprehensive speaker bucket history with transitions,
 * performance metrics, and quality trends.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  Assignment as AssignmentIcon,
  AutoMode as AutoModeIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

interface BucketHistoryEntry {
  historyId: string;
  bucketType: string;
  previousBucket?: string;
  assignedDate: string;
  assignedBy: string;
  assignmentReason: string;
  assignmentType: 'manual' | 'automatic' | 'system';
  transitionDescription: string;
  daysSinceAssignment: number;
  confidenceScore?: number;
}

interface PerformanceMetrics {
  speakerId: string;
  currentBucket: string;
  performanceScore: number;
  rectificationRate: number;
  totalErrorsReported: number;
  errorsRectified: number;
  qualityTrend?: 'improving' | 'stable' | 'declining';
  recommendedBucket: string;
  needsAttention: boolean;
  shouldReassess: boolean;
  daysInCurrentBucket: number;
  lastAssessmentDate?: string;
}

interface SpeakerBucketHistoryDashboardProps {
  speakerId: string;
  history: BucketHistoryEntry[];
  performanceMetrics: PerformanceMetrics;
  onAssignBucket?: (bucketType: string, reason: string) => void;
  loading?: boolean;
}

const BUCKET_COLORS = {
  no_touch: '#4caf50',
  low_touch: '#2196f3',
  medium_touch: '#ff9800',
  high_touch: '#f44336',
};

const BUCKET_LABELS = {
  no_touch: 'No Touch',
  low_touch: 'Low Touch',
  medium_touch: 'Medium Touch',
  high_touch: 'High Touch',
};

export const SpeakerBucketHistoryDashboard: React.FC<SpeakerBucketHistoryDashboardProps> = ({
  speakerId,
  history,
  performanceMetrics,
  onAssignBucket,
  loading = false,
}) => {
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [newBucketType, setNewBucketType] = useState('');
  const [assignmentReason, setAssignmentReason] = useState('');

  const getBucketColor = (bucketType: string) => {
    return BUCKET_COLORS[bucketType as keyof typeof BUCKET_COLORS] || '#757575';
  };

  const getBucketLabel = (bucketType: string) => {
    return BUCKET_LABELS[bucketType as keyof typeof BUCKET_LABELS] || bucketType;
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUpIcon color="success" />;
      case 'declining':
        return <TrendingDownIcon color="error" />;
      case 'stable':
        return <TrendingFlatIcon color="info" />;
      default:
        return null;
    }
  };

  const getAssignmentIcon = (type: string) => {
    switch (type) {
      case 'manual':
        return <PersonIcon />;
      case 'automatic':
        return <AutoModeIcon />;
      case 'system':
        return <AssignmentIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const handleAssignBucket = () => {
    if (onAssignBucket && newBucketType && assignmentReason) {
      onAssignBucket(newBucketType, assignmentReason);
      setAssignDialogOpen(false);
      setNewBucketType('');
      setAssignmentReason('');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 1 }}>
          Loading speaker bucket history...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Performance Overview */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Performance
              </Typography>
              
              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Current Bucket
                </Typography>
                <Chip
                  label={getBucketLabel(performanceMetrics.currentBucket)}
                  sx={{
                    backgroundColor: getBucketColor(performanceMetrics.currentBucket),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Performance Score
                </Typography>
                <Box display="flex" alignItems="center">
                  <Typography variant="h4" color="primary">
                    {performanceMetrics.performanceScore.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    / 10.0
                  </Typography>
                  {getTrendIcon(performanceMetrics.qualityTrend)}
                </Box>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Rectification Rate
                </Typography>
                <Typography variant="h5">
                  {(performanceMetrics.rectificationRate * 100).toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={performanceMetrics.rectificationRate * 100}
                  sx={{ mt: 1 }}
                />
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Total Errors: {performanceMetrics.totalErrorsReported} | 
                  Rectified: {performanceMetrics.errorsRectified}
                </Typography>
              </Box>

              {performanceMetrics.needsAttention && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  This speaker needs attention
                </Alert>
              )}

              {performanceMetrics.shouldReassess && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Bucket reassessment recommended
                </Alert>
              )}

              {performanceMetrics.recommendedBucket !== performanceMetrics.currentBucket && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Recommended bucket: {getBucketLabel(performanceMetrics.recommendedBucket)}
                </Alert>
              )}

              {onAssignBucket && (
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => setAssignDialogOpen(true)}
                  startIcon={<AssignmentIcon />}
                >
                  Assign New Bucket
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Bucket History Timeline */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Bucket Assignment History
              </Typography>
              
              <Timeline>
                {history.map((entry, index) => (
                  <TimelineItem key={entry.historyId}>
                    <TimelineSeparator>
                      <TimelineDot
                        sx={{
                          backgroundColor: getBucketColor(entry.bucketType),
                          color: 'white',
                        }}
                      >
                        {getAssignmentIcon(entry.assignmentType)}
                      </TimelineDot>
                      {index < history.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent>
                      <Paper elevation={1} sx={{ p: 2, mb: 1 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {entry.transitionDescription}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {entry.daysSinceAssignment} days ago
                          </Typography>
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" mb={1}>
                          {formatDate(entry.assignedDate)}
                        </Typography>
                        
                        <Typography variant="body2" mb={1}>
                          {entry.assignmentReason}
                        </Typography>
                        
                        <Box display="flex" gap={1} flexWrap="wrap">
                          <Chip
                            label={getBucketLabel(entry.bucketType)}
                            size="small"
                            sx={{
                              backgroundColor: getBucketColor(entry.bucketType),
                              color: 'white',
                            }}
                          />
                          <Chip
                            label={entry.assignmentType}
                            size="small"
                            variant="outlined"
                          />
                          {entry.confidenceScore && (
                            <Chip
                              label={`Confidence: ${(entry.confidenceScore * 100).toFixed(0)}%`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Paper>
                    </TimelineContent>
                  </TimelineItem>
                ))}
              </Timeline>
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed History Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed History
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Bucket</TableCell>
                      <TableCell>Previous</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Assigned By</TableCell>
                      <TableCell>Confidence</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {history.map((entry) => (
                      <TableRow key={entry.historyId}>
                        <TableCell>
                          {formatDate(entry.assignedDate)}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={getBucketLabel(entry.bucketType)}
                            size="small"
                            sx={{
                              backgroundColor: getBucketColor(entry.bucketType),
                              color: 'white',
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          {entry.previousBucket ? (
                            <Chip
                              label={getBucketLabel(entry.previousBucket)}
                              size="small"
                              variant="outlined"
                            />
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={entry.assignmentType}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{entry.assignmentReason}</TableCell>
                        <TableCell>{entry.assignedBy}</TableCell>
                        <TableCell>
                          {entry.confidenceScore ? 
                            `${(entry.confidenceScore * 100).toFixed(0)}%` : 
                            '-'
                          }
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Assign Bucket Dialog */}
      <Dialog open={assignDialogOpen} onClose={() => setAssignDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Assign New Bucket</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Bucket Type</InputLabel>
              <Select
                value={newBucketType}
                onChange={(e) => setNewBucketType(e.target.value)}
                label="Bucket Type"
              >
                {Object.entries(BUCKET_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Assignment Reason"
              value={assignmentReason}
              onChange={(e) => setAssignmentReason(e.target.value)}
              placeholder="Explain the reason for this bucket assignment..."
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAssignBucket}
            variant="contained"
            disabled={!newBucketType || !assignmentReason}
          >
            Assign Bucket
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

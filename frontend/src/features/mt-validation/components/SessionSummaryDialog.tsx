/**
 * Session Summary Dialog Component
 * 
 * Comprehensive summary dialog showing validation session results,
 * statistics, and recommendations.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  IconButton,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as ExportIcon,
  Assessment as AssessmentIcon,
  TrendingUp as ImprovementIcon,
  Person as PersonIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { ValidationSession, ImprovementAssessment } from '@/domain/types/mt-validation';

interface SessionSummaryDialogProps {
  session: ValidationSession;
  open: boolean;
  onClose: () => void;
  onExport?: () => void;
}

// Mock summary data - in real app, this would come from API
const mockSummaryData = {
  total_feedback_items: 20,
  average_rating: 4.2,
  improvement_distribution: {
    [ImprovementAssessment.SIGNIFICANT]: 8,
    [ImprovementAssessment.MODERATE]: 7,
    [ImprovementAssessment.MINIMAL]: 3,
    [ImprovementAssessment.NONE]: 2,
    [ImprovementAssessment.WORSE]: 0,
  },
  bucket_change_recommendations: 1,
  average_review_time_minutes: 2.5,
  quality_insights: {
    significant_improvements: 8,
    areas_for_improvement: [
      'Medical terminology accuracy',
      'Numeric value corrections',
      'Punctuation consistency'
    ],
    overall_assessment: 'Strong performance with consistent quality improvements. Recommend bucket transition.',
  },
  detailed_feedback: [
    {
      item_number: 1,
      rating: 5,
      improvement: ImprovementAssessment.SIGNIFICANT,
      review_time: 180,
      bucket_recommendation: false,
    },
    {
      item_number: 2,
      rating: 4,
      improvement: ImprovementAssessment.MODERATE,
      review_time: 150,
      bucket_recommendation: false,
    },
    // ... more items
  ],
};

export const SessionSummaryDialog: React.FC<SessionSummaryDialogProps> = ({
  session,
  open,
  onClose,
  onExport,
}) => {
  const [summaryData] = useState(mockSummaryData);

  const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${Math.round(minutes)}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = Math.round(minutes % 60);
    return `${hours}h ${remainingMinutes}m`;
  };

  const getImprovementColor = (assessment: ImprovementAssessment) => {
    switch (assessment) {
      case ImprovementAssessment.SIGNIFICANT: return 'success';
      case ImprovementAssessment.MODERATE: return 'info';
      case ImprovementAssessment.MINIMAL: return 'warning';
      case ImprovementAssessment.NONE: return 'default';
      case ImprovementAssessment.WORSE: return 'error';
      default: return 'default';
    }
  };

  const getImprovementLabel = (assessment: ImprovementAssessment) => {
    return assessment.replace('_', ' ').toLowerCase();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{ sx: { height: '90vh' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssessmentIcon color="primary" />
            <Typography variant="h6">Validation Session Summary</Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {/* Session Overview */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Session Overview
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Session Name
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {session.session_name}
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Duration
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {formatDuration(session.duration_minutes || 0)}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Items Reviewed
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {summaryData.total_feedback_items}
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Completion Rate
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {session.progress_percentage.toFixed(1)}%
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Key Metrics */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="primary.main">
                  {summaryData.average_rating.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average Rating
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {summaryData.quality_insights.significant_improvements}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Significant Improvements
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="info.main">
                  {summaryData.bucket_change_recommendations}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Bucket Recommendations
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  {formatDuration(summaryData.average_review_time_minutes)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Review Time
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Improvement Distribution */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Improvement Assessment Distribution
            </Typography>
            
            <Grid container spacing={2}>
              {Object.entries(summaryData.improvement_distribution).map(([assessment, count]) => (
                <Grid item xs={12} sm={6} md={4} key={assessment}>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Chip
                        label={getImprovementLabel(assessment as ImprovementAssessment)}
                        color={getImprovementColor(assessment as ImprovementAssessment)}
                        size="small"
                        sx={{ textTransform: 'capitalize' }}
                      />
                      <Typography variant="body2" fontWeight="medium">
                        {count} items
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(count / summaryData.total_feedback_items) * 100}
                      color={getImprovementColor(assessment as ImprovementAssessment)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>

        {/* Quality Insights */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quality Insights & Recommendations
            </Typography>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              {summaryData.quality_insights.overall_assessment}
            </Alert>
            
            <Typography variant="subtitle2" gutterBottom>
              Areas for Improvement:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {summaryData.quality_insights.areas_for_improvement.map((area, index) => (
                <Chip
                  key={index}
                  label={area}
                  size="small"
                  variant="outlined"
                  color="warning"
                />
              ))}
            </Box>
            
            {summaryData.bucket_change_recommendations > 0 && (
              <Alert severity="success">
                <Typography variant="body2">
                  <strong>Recommendation:</strong> This speaker shows consistent quality improvements 
                  and is recommended for bucket transition to reduce touch requirements.
                </Typography>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Detailed Feedback Table */}
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Detailed Feedback Summary
            </Typography>
            
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell>Rating</TableCell>
                    <TableCell>Improvement</TableCell>
                    <TableCell>Review Time</TableCell>
                    <TableCell>Bucket Rec.</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {summaryData.detailed_feedback.slice(0, 10).map((item) => (
                    <TableRow key={item.item_number}>
                      <TableCell>{item.item_number}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {item.rating}/5
                          <LinearProgress
                            variant="determinate"
                            value={(item.rating / 5) * 100}
                            sx={{ width: 40, height: 4 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getImprovementLabel(item.improvement)}
                          color={getImprovementColor(item.improvement)}
                          size="small"
                          sx={{ textTransform: 'capitalize' }}
                        />
                      </TableCell>
                      <TableCell>{Math.round(item.review_time / 60)}m</TableCell>
                      <TableCell>
                        {item.bucket_recommendation ? (
                          <Chip label="Yes" color="success" size="small" />
                        ) : (
                          <Chip label="No" color="default" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            {summaryData.detailed_feedback.length > 10 && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Showing first 10 items. Export for complete data.
              </Typography>
            )}
          </CardContent>
        </Card>
      </DialogContent>

      <DialogActions>
        {onExport && (
          <Button
            startIcon={<ExportIcon />}
            onClick={onExport}
            variant="outlined"
          >
            Export Report
          </Button>
        )}
        
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SessionSummaryDialog;

/**
 * Speaker Details Dialog Component
 * 
 * Comprehensive dialog for viewing detailed speaker information
 * including statistics, trends, and action buttons.
 */

import React, { useEffect, useState } from 'react';
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
  Avatar,
  Divider,
  IconButton,
  Tooltip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  CircularProgress,
} from '@mui/material';
import {
  Close as CloseIcon,
  Edit as EditIcon,
  Assessment as AssessmentIcon,
  SwapHoriz as TransitionIcon,
  History as HistoryIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  DataUsage as DataIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  getComprehensiveSpeakerView,
  selectComprehensiveView,
  selectSpeakersLoading,
} from '../speaker-slice';
import { Speaker, SpeakerBucket, QualityTrend } from '@/domain/types/speaker';

interface SpeakerDetailsDialogProps {
  speaker: Speaker;
  open: boolean;
  onClose: () => void;
  onEdit?: () => void;
  onAssess?: () => void;
  onTransitionRequest?: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`speaker-details-tabpanel-${index}`}
      aria-labelledby={`speaker-details-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

export const SpeakerDetailsDialog: React.FC<SpeakerDetailsDialogProps> = ({
  speaker,
  open,
  onClose,
  onEdit,
  onAssess,
  onTransitionRequest,
}) => {
  const dispatch = useAppDispatch();
  
  // Redux state
  const comprehensiveView = useAppSelector(selectComprehensiveView);
  const loading = useAppSelector(selectSpeakersLoading);
  
  // Local state
  const [currentTab, setCurrentTab] = useState(0);

  // Load comprehensive view when dialog opens
  useEffect(() => {
    if (open && speaker) {
      dispatch(getComprehensiveSpeakerView({
        speakerId: speaker.speaker_id,
        options: {
          include_ser_analysis: true,
          include_error_patterns: true,
          include_transition_history: true,
        },
      }));
    }
  }, [dispatch, open, speaker]);

  // Get bucket color
  const getBucketColor = (bucket: SpeakerBucket): 'error' | 'warning' | 'info' | 'success' => {
    switch (bucket) {
      case SpeakerBucket.HIGH_TOUCH: return 'error';
      case SpeakerBucket.MEDIUM_TOUCH: return 'warning';
      case SpeakerBucket.LOW_TOUCH: return 'info';
      case SpeakerBucket.NO_TOUCH: return 'success';
      default: return 'info';
    }
  };

  // Get trend icon
  const getTrendIcon = (trend: QualityTrend) => {
    switch (trend) {
      case QualityTrend.IMPROVING:
        return <TrendingUpIcon color="success" />;
      case QualityTrend.DECLINING:
        return <TrendingDownIcon color="error" />;
      case QualityTrend.STABLE:
        return <TrendingFlatIcon color="info" />;
      default:
        return <TrendingFlatIcon color="disabled" />;
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      {/* Dialog Header */}
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ width: 48, height: 48, fontSize: '1.25rem' }}>
              {speaker.speaker_name.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h6" component="div">
                {speaker.speaker_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {speaker.speaker_identifier}
              </Typography>
            </Box>
          </Box>
          
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      {/* Dialog Content */}
      <DialogContent sx={{ px: 0 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Quick Stats */}
            <Box sx={{ px: 3, mb: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Chip
                        label={speaker.current_bucket.replace('_', ' ')}
                        color={getBucketColor(speaker.current_bucket)}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption" display="block" color="text.secondary">
                        Current Bucket
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {speaker.note_count.toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Total Notes
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {speaker.average_ser_score.toFixed(1)}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Average SER
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        {getTrendIcon(speaker.quality_trend)}
                        <Typography variant="caption" color="text.secondary">
                          {speaker.quality_trend.replace('_', ' ').toUpperCase()}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>

            {/* Transition Recommendation */}
            {speaker.should_transition && (
              <Box sx={{ px: 3, mb: 2 }}>
                <Alert 
                  severity="info" 
                  action={
                    onTransitionRequest && (
                      <Button color="inherit" size="small" onClick={onTransitionRequest}>
                        Create Request
                      </Button>
                    )
                  }
                >
                  This speaker is recommended for bucket transition
                  {speaker.recommended_bucket && ` to ${speaker.recommended_bucket.replace('_', ' ')}`}.
                </Alert>
              </Box>
            )}

            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3 }}>
              <Tabs value={currentTab} onChange={handleTabChange}>
                <Tab label="Overview" />
                <Tab label="SER Analysis" />
                <Tab label="Error Patterns" />
                <Tab label="History" />
              </Tabs>
            </Box>

            {/* Tab Panels */}
            <Box sx={{ px: 3 }}>
              {/* Overview Tab */}
              <TabPanel value={currentTab} index={0}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Speaker Information
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Identifier
                      </Typography>
                      <Typography variant="body1">
                        {speaker.speaker_identifier}
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Current Bucket
                      </Typography>
                      <Chip
                        label={speaker.current_bucket.replace('_', ' ')}
                        color={getBucketColor(speaker.current_bucket)}
                        size="small"
                      />
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Data Sufficiency
                      </Typography>
                      <Chip
                        label={speaker.has_sufficient_data ? 'Sufficient' : 'Limited'}
                        color={speaker.has_sufficient_data ? 'success' : 'warning'}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Quality Metrics
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Average SER Score
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min(speaker.average_ser_score, 100)}
                          sx={{ 
                            flexGrow: 1,
                            height: 8,
                            backgroundColor: 'grey.200',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: speaker.average_ser_score > 25 ? 'error.main' : 
                                              speaker.average_ser_score > 15 ? 'warning.main' : 'success.main'
                            }
                          }}
                        />
                        <Typography variant="body2" fontWeight="medium">
                          {speaker.average_ser_score.toFixed(1)}%
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Quality Trend
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                        {getTrendIcon(speaker.quality_trend)}
                        <Typography variant="body1">
                          {speaker.quality_trend.replace('_', ' ').toUpperCase()}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </TabPanel>

              {/* SER Analysis Tab */}
              <TabPanel value={currentTab} index={1}>
                {comprehensiveView?.ser_analysis ? (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      SER Analysis
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Detailed SER analysis would be displayed here.
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <DataIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="body1" color="text.secondary">
                      SER analysis data not available
                    </Typography>
                  </Box>
                )}
              </TabPanel>

              {/* Error Patterns Tab */}
              <TabPanel value={currentTab} index={2}>
                {comprehensiveView?.error_patterns ? (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Error Patterns
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Error pattern analysis would be displayed here.
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <DataIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="body1" color="text.secondary">
                      Error pattern data not available
                    </Typography>
                  </Box>
                )}
              </TabPanel>

              {/* History Tab */}
              <TabPanel value={currentTab} index={3}>
                {comprehensiveView?.transition_history ? (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Transition History
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Transition history would be displayed here.
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <HistoryIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="body1" color="text.secondary">
                      No transition history available
                    </Typography>
                  </Box>
                )}
              </TabPanel>
            </Box>
          </>
        )}
      </DialogContent>

      {/* Dialog Actions */}
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose}>
          Close
        </Button>
        
        {onEdit && (
          <Button
            startIcon={<EditIcon />}
            onClick={onEdit}
            variant="outlined"
          >
            Edit
          </Button>
        )}
        
        {onAssess && (
          <Button
            startIcon={<AssessmentIcon />}
            onClick={onAssess}
            variant="contained"
            color="primary"
          >
            Start Assessment
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default SpeakerDetailsDialog;

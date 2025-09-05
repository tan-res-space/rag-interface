/**
 * Speaker Profile Dashboard Component
 * Displays speaker bucket status, progression history, and analytics
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  LinearProgress,
  Divider,
  Button,
  Alert,
  CircularProgress,
  useTheme
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { SpeakerProfile, BucketChangeLog } from '@domain/types';
import { speakerProfileService, bucketProgressionHelpers } from '@infrastructure/services/speakerProfileService';

interface SpeakerProfileDashboardProps {
  speakerId: string;
  onBucketChange?: (oldBucket: string, newBucket: string, reason: string) => void;
}

export const SpeakerProfileDashboard: React.FC<SpeakerProfileDashboardProps> = ({
  speakerId,
  onBucketChange
}) => {
  const theme = useTheme();
  const queryClient = useQueryClient();

  // Fetch speaker profile
  const {
    data: profile,
    isLoading: profileLoading,
    error: profileError,
    refetch: refetchProfile
  } = useQuery({
    queryKey: ['speakerProfile', speakerId],
    queryFn: () => speakerProfileService.getSpeakerProfile(speakerId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch bucket change history
  const {
    data: bucketHistory,
    isLoading: historyLoading
  } = useQuery({
    queryKey: ['bucketHistory', speakerId],
    queryFn: () => speakerProfileService.getBucketChangeHistory(speakerId, 10),
    staleTime: 5 * 60 * 1000,
  });

  // Evaluate progression mutation
  const evaluateProgressionMutation = useMutation({
    mutationFn: (forceEvaluation: boolean = false) => 
      speakerProfileService.evaluateSpeakerProgression(speakerId, forceEvaluation),
    onSuccess: (data) => {
      if (data.bucket_changed && onBucketChange) {
        onBucketChange(
          data.old_bucket || '',
          data.new_bucket || '',
          data.change_reason || ''
        );
      }
      // Refetch profile and history
      queryClient.invalidateQueries({ queryKey: ['speakerProfile', speakerId] });
      queryClient.invalidateQueries({ queryKey: ['bucketHistory', speakerId] });
    }
  });

  const handleEvaluateProgression = () => {
    evaluateProgressionMutation.mutate(false);
  };

  const handleForceEvaluation = () => {
    evaluateProgressionMutation.mutate(true);
  };

  if (profileLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  if (profileError || !profile) {
    return (
      <Alert severity="error">
        Failed to load speaker profile. Please try again.
      </Alert>
    );
  }

  const nextBucket = bucketProgressionHelpers.getNextBucket(profile.current_bucket);
  const progressPercentage = bucketProgressionHelpers.calculateProgressPercentage(
    profile.bucket_info.level,
    profile.statistics.average_error_rate,
    profile.bucket_info.level < 3 ? 0.05 : 0.02 // Target error rates
  );

  return (
    <Box>
      {/* Current Bucket Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
            <Box>
              <Typography variant="h6" gutterBottom>
                Current Bucket Level
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Chip
                  label={`${profile.bucket_info.icon} ${profile.bucket_info.label}`}
                  size="large"
                  sx={{
                    backgroundColor: profile.bucket_info.color,
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '1.1rem',
                    height: 40
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  Level {profile.bucket_info.level + 1} of 4
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {profile.bucket_info.description}
              </Typography>
            </Box>
            
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<RefreshIcon />}
                onClick={() => refetchProfile()}
                disabled={profileLoading}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                size="small"
                startIcon={<AssessmentIcon />}
                onClick={handleEvaluateProgression}
                disabled={evaluateProgressionMutation.isPending}
              >
                {evaluateProgressionMutation.isPending ? 'Evaluating...' : 'Evaluate Progress'}
              </Button>
            </Box>
          </Box>

          {/* Progress to Next Level */}
          {nextBucket && (
            <Box sx={{ mt: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" fontWeight="medium">
                  Progress to {bucketProgressionHelpers.getBucketDisplayName(nextBucket)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {Math.round(progressPercentage)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progressPercentage}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: theme.palette.grey[200],
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: bucketProgressionHelpers.getBucketColor(nextBucket),
                    borderRadius: 4
                  }
                }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                Keep improving your error rate and correction accuracy to advance!
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Statistics Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary" gutterBottom>
                {profile.statistics.total_reports}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Reports
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="error" gutterBottom>
                {(profile.statistics.average_error_rate * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average Error Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="success.main" gutterBottom>
                {(profile.statistics.average_correction_accuracy * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Correction Accuracy
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="info.main" gutterBottom>
                {profile.statistics.days_in_current_bucket}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Days in Current Bucket
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Bucket Changes */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <HistoryIcon color="action" />
            <Typography variant="h6">
              Recent Bucket Changes
            </Typography>
          </Box>
          
          {historyLoading ? (
            <Box display="flex" justifyContent="center" py={2}>
              <CircularProgress size={24} />
            </Box>
          ) : bucketHistory && bucketHistory.history.length > 0 ? (
            <Box>
              {bucketHistory.history.slice(0, 5).map((change, index) => (
                <Box key={change.change_id}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
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
                  {index < bucketHistory.history.length - 1 && index < 4 && <Divider />}
                </Box>
              ))}
              
              {bucketHistory.total_changes > 5 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Showing 5 of {bucketHistory.total_changes} total changes
                </Typography>
              )}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No bucket changes yet. Keep submitting quality error reports to advance!
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Evaluation Results */}
      {evaluateProgressionMutation.data && (
        <Alert 
          severity={evaluateProgressionMutation.data.bucket_changed ? "success" : "info"}
          sx={{ mt: 2 }}
        >
          {evaluateProgressionMutation.data.bucket_changed ? (
            <Typography>
              🎉 Bucket level updated! {evaluateProgressionMutation.data.change_reason}
            </Typography>
          ) : (
            <Typography>
              Evaluation completed. {evaluateProgressionMutation.data.recommendation?.reason || 'No bucket change recommended at this time.'}
            </Typography>
          )}
        </Alert>
      )}
    </Box>
  );
};

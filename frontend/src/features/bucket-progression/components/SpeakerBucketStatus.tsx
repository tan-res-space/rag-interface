/**
 * Speaker Bucket Status Component
 * Displays current bucket status in the error reporting form
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Skeleton,
  Alert,
  useTheme
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useState, useEffect } from 'react';
import type { SpeakerProfile } from '@domain/types';
import { speakerProfileService, bucketProgressionHelpers } from '@infrastructure/services/speakerProfileService';

interface SpeakerBucketStatusProps {
  speakerId: string;
  compact?: boolean;
}

export const SpeakerBucketStatus: React.FC<SpeakerBucketStatusProps> = ({
  speakerId,
  compact = false
}) => {
  const theme = useTheme();
  const [profile, setProfile] = useState<SpeakerProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!speakerId) return;

    const fetchProfile = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const profileData = await speakerProfileService.getSpeakerProfile(speakerId);
        setProfile(profileData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch profile');
        console.error('Error fetching speaker profile:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [speakerId]);

  if (!speakerId) {
    return null;
  }

  if (isLoading) {
    return (
      <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
        <CardContent sx={{ py: compact ? 1 : 2 }}>
          <Box display="flex" alignItems="center" gap={2}>
            <Skeleton variant="rectangular" width={120} height={32} />
            <Box flex={1}>
              <Skeleton variant="text" width="60%" />
              <Skeleton variant="text" width="40%" />
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error || !profile) {
    return (
      <Alert severity="info" variant="outlined" sx={{ bgcolor: 'info.light' }}>
        <Box display="flex" alignItems="center" gap={1}>
          <InfoIcon fontSize="small" />
          <Typography variant="body2">
            Speaker bucket status will be displayed once the speaker ID is validated.
          </Typography>
        </Box>
      </Alert>
    );
  }

  const nextBucket = profile ? bucketProgressionHelpers.getNextBucket(profile.current_bucket) : null;
  const progressPercentage = profile ? bucketProgressionHelpers.calculateProgressPercentage(
    profile.bucket_info.level,
    profile.statistics.average_error_rate,
    profile.bucket_info.level < 3 ? 0.05 : 0.02
  ) : 0;

  return (
    <Card variant="outlined" sx={{ bgcolor: 'primary.light', borderColor: 'primary.main' }}>
      <CardContent sx={{ py: compact ? 1.5 : 2 }}>
        <Box display="flex" alignItems="center" gap={2} mb={compact ? 1 : 2}>
          <Chip
            label={`${profile.bucket_info.icon} ${profile.bucket_info.label}`}
            sx={{
              backgroundColor: profile.bucket_info.color,
              color: 'white',
              fontWeight: 'bold',
              fontSize: compact ? '0.875rem' : '1rem'
            }}
          />
          <Box flex={1}>
            <Typography variant={compact ? "body2" : "body1"} fontWeight="medium">
              Current Speaker Level
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {profile.bucket_info.description}
            </Typography>
          </Box>
        </Box>

        {!compact && (
          <Box sx={{ mb: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" color="text.secondary">
                Performance Summary
              </Typography>
            </Box>
            <Box display="flex" gap={3}>
              <Box>
                <Typography variant="h6" color="primary">
                  {profile.statistics.total_reports}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Reports
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="error.main">
                  {(profile.statistics.average_error_rate * 100).toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Error Rate
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="success.main">
                  {(profile.statistics.average_correction_accuracy * 100).toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Accuracy
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

        {nextBucket && (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Box display="flex" alignItems="center" gap={1}>
                <TrendingUpIcon fontSize="small" color="action" />
                <Typography variant="body2" fontWeight="medium">
                  Progress to {nextBucket ? bucketProgressionHelpers.getBucketDisplayName(nextBucket) : 'Next Level'}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {Math.round(progressPercentage)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progressPercentage}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: theme.palette.grey[200],
                '& .MuiLinearProgress-bar': {
                  backgroundColor: nextBucket ? bucketProgressionHelpers.getBucketColor(nextBucket) : '#ff9800',
                  borderRadius: 3
                }
              }}
            />
            {!compact && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                Keep submitting quality error reports to advance to the next level!
              </Typography>
            )}
          </Box>
        )}

        {profile.current_bucket === 'expert' && (
          <Box display="flex" alignItems="center" gap={1} mt={1}>
            <Typography variant="body2" color="success.main" fontWeight="medium">
              🏆 Expert Level Achieved!
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

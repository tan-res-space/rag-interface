/**
 * Feedback Panel Component
 * 
 * Interactive panel for MT feedback collection with rating,
 * comments, improvement assessment, and bucket recommendations.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Rating,
  Button,
  Chip,
  Alert,
  Divider,
  Switch,
  Slider,
  Card,
  CardContent,
  LinearProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Save as SaveIcon,
  Send as SubmitIcon,
  Clear as ClearIcon,
  Timer as TimerIcon,
  Lightbulb as SuggestionIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  submitMTFeedback,
  updateCurrentFeedback,
  clearCurrentFeedback,
  selectCurrentFeedback,
  selectValidationLoading,
  selectValidationError,
  selectUserPreferences,
} from '../mt-validation-slice';
import {
  ValidationTestData,
  ImprovementAssessment,
  SubmitMTFeedbackRequest,
} from '@/domain/types/mt-validation';

interface FeedbackPanelProps {
  sessionId: string;
  currentItem: ValidationTestData;
  onFeedbackSubmitted?: () => void;
  autoAdvance?: boolean;
}

export const FeedbackPanel: React.FC<FeedbackPanelProps> = ({
  sessionId,
  currentItem,
  onFeedbackSubmitted,
  autoAdvance = true,
}) => {
  const dispatch = useAppDispatch();
  
  // Redux state
  const currentFeedback = useAppSelector(selectCurrentFeedback);
  const loading = useAppSelector(selectValidationLoading);
  const error = useAppSelector(selectValidationError);
  const userPreferences = useAppSelector(selectUserPreferences);
  
  // Local state
  const [reviewStartTime] = useState(Date.now());
  const [reviewTime, setReviewTime] = useState(0);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Timer for review time tracking
  useEffect(() => {
    if (!userPreferences.review_time_tracking) return;

    const interval = setInterval(() => {
      setReviewTime(Math.floor((Date.now() - reviewStartTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [reviewStartTime, userPreferences.review_time_tracking]);

  // Auto-save functionality
  useEffect(() => {
    if (!userPreferences.auto_save_feedback) return;

    const autoSaveInterval = setInterval(() => {
      if (Object.keys(currentFeedback).length > 0) {
        // Auto-save logic would go here
        console.log('Auto-saving feedback...');
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearInterval(autoSaveInterval);
  }, [currentFeedback, userPreferences.auto_save_feedback]);

  // Form validation
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!currentFeedback.mt_feedback_rating || currentFeedback.mt_feedback_rating < 1) {
      errors.rating = 'Please provide a rating';
    }

    if (!currentFeedback.improvement_assessment) {
      errors.improvement_assessment = 'Please select an improvement assessment';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form field changes
  const handleFieldChange = (field: keyof SubmitMTFeedbackRequest, value: any) => {
    dispatch(updateCurrentFeedback({ [field]: value }));
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    const feedbackData: SubmitMTFeedbackRequest = {
      session_id: sessionId,
      historical_data_id: currentItem.data_id,
      original_asr_text: currentItem.original_asr_text,
      rag_corrected_text: currentItem.rag_corrected_text,
      final_reference_text: currentItem.final_reference_text,
      mt_feedback_rating: currentFeedback.mt_feedback_rating || 1,
      mt_comments: currentFeedback.mt_comments || '',
      improvement_assessment: currentFeedback.improvement_assessment || ImprovementAssessment.NONE,
      recommended_for_bucket_change: currentFeedback.recommended_for_bucket_change || false,
      feedback_metadata: {
        review_time_seconds: reviewTime,
        auto_advance: autoAdvance,
        ...currentFeedback.feedback_metadata,
      },
    };

    try {
      await dispatch(submitMTFeedback({ sessionId, feedback: feedbackData })).unwrap();
      dispatch(clearCurrentFeedback());
      onFeedbackSubmitted?.();
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  // Handle clear form
  const handleClear = () => {
    dispatch(clearCurrentFeedback());
    setValidationErrors({});
  };

  // Get improvement assessment color
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

  // Format review time
  const formatReviewTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Paper elevation={1} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">MT Feedback</Typography>
          
          {userPreferences.review_time_tracking && (
            <Chip
              icon={<TimerIcon />}
              label={formatReviewTime(reviewTime)}
              size="small"
              variant="outlined"
            />
          )}
        </Box>
      </Box>

      {/* Error Alert */}
      {error.feedback && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error.feedback}
        </Alert>
      )}

      {/* Form Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {/* Rating */}
        <Box sx={{ mb: 3 }}>
          <FormLabel component="legend" sx={{ mb: 1 }}>
            Overall Quality Rating *
          </FormLabel>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Rating
              value={currentFeedback.mt_feedback_rating || 0}
              onChange={(_, value) => handleFieldChange('mt_feedback_rating', value)}
              size="large"
              precision={1}
              max={5}
            />
            <Typography variant="body2" color="text.secondary">
              {currentFeedback.mt_feedback_rating ? `${currentFeedback.mt_feedback_rating}/5` : 'Not rated'}
            </Typography>
          </Box>
          {validationErrors.rating && (
            <Typography variant="caption" color="error">
              {validationErrors.rating}
            </Typography>
          )}
        </Box>

        {/* Improvement Assessment */}
        <Box sx={{ mb: 3 }}>
          <FormControl component="fieldset" error={!!validationErrors.improvement_assessment}>
            <FormLabel component="legend" sx={{ mb: 1 }}>
              Improvement Assessment *
            </FormLabel>
            <RadioGroup
              value={currentFeedback.improvement_assessment || ''}
              onChange={(e) => handleFieldChange('improvement_assessment', e.target.value)}
            >
              {Object.values(ImprovementAssessment).map((assessment) => (
                <FormControlLabel
                  key={assessment}
                  value={assessment}
                  control={<Radio />}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {assessment.replace('_', ' ')}
                      </Typography>
                      <Chip
                        label={assessment.toUpperCase()}
                        size="small"
                        color={getImprovementColor(assessment)}
                        variant="outlined"
                      />
                    </Box>
                  }
                />
              ))}
            </RadioGroup>
            {validationErrors.improvement_assessment && (
              <Typography variant="caption" color="error">
                {validationErrors.improvement_assessment}
              </Typography>
            )}
          </FormControl>
        </Box>

        {/* Bucket Change Recommendation */}
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={currentFeedback.recommended_for_bucket_change || false}
                onChange={(e) => handleFieldChange('recommended_for_bucket_change', e.target.checked)}
              />
            }
            label="Recommend for bucket change"
          />
          <Typography variant="caption" color="text.secondary" display="block">
            Check if this speaker should be moved to a different bucket based on quality improvements
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Comments */}
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Comments (Optional)"
            placeholder="Provide specific feedback about the correction quality, accuracy, and any observations..."
            value={currentFeedback.mt_comments || ''}
            onChange={(e) => handleFieldChange('mt_comments', e.target.value)}
            variant="outlined"
          />
        </Box>

        {/* Suggestions */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle2">
                AI Suggestions
              </Typography>
              <IconButton size="small" onClick={() => setShowSuggestions(!showSuggestions)}>
                <SuggestionIcon />
              </IconButton>
            </Box>
            
            {showSuggestions && (
              <Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Based on SER metrics analysis:
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {currentItem.improvement_metrics.is_significant_improvement && (
                    <Chip
                      label="Significant improvement detected"
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  )}
                  {currentItem.corrected_ser_metrics.quality_level === 'high' && (
                    <Chip
                      label="High quality correction"
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  )}
                  {currentItem.improvement_metrics.improvement > 10 && (
                    <Chip
                      label="Consider bucket promotion"
                      size="small"
                      color="info"
                      variant="outlined"
                    />
                  )}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Progress Indicator */}
        {loading.feedback && (
          <Box sx={{ mb: 2 }}>
            <LinearProgress />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              Submitting feedback...
            </Typography>
          </Box>
        )}
      </Box>

      {/* Actions */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
          <Button
            startIcon={<ClearIcon />}
            onClick={handleClear}
            disabled={loading.feedback}
            variant="outlined"
            color="secondary"
          >
            Clear
          </Button>
          
          <Button
            startIcon={<SubmitIcon />}
            onClick={handleSubmit}
            disabled={loading.feedback}
            variant="contained"
            color="primary"
          >
            {loading.feedback ? 'Submitting...' : 'Submit & Next'}
          </Button>
        </Box>
        
        {autoAdvance && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Will automatically advance to next item after submission
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default FeedbackPanel;

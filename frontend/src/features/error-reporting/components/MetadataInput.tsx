/**
 * Enhanced Metadata Input Component
 * Captures contextual information about error conditions
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  TextField,
  FormControl,
  FormLabel,
  FormHelperText,
  Select,
  MenuItem,
  Slider,
  Typography,
  Chip,
  Rating,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  useTheme,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  VolumeUp as VolumeIcon,
  Hearing as HearingIcon,
  RecordVoiceOver as VoiceIcon,
  Speed as SpeedIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import type { ErrorMetadata, AudioQualityIndicator, NoiseLevel, ClarityLevel, UrgencyLevel, BucketType } from '@domain/types';
import { SpeakerBucketStatus } from '@features/bucket-progression/components/SpeakerBucketStatus';

export interface MetadataInputProps {
  value: ErrorMetadata;
  onChange: (metadata: ErrorMetadata) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  showAdvanced?: boolean;
  speakerId?: string;
  clientId?: string;
  bucketType?: BucketType | '';
  onSpeakerIdChange?: (speakerId: string) => void;
  onClientIdChange?: (clientId: string) => void;
  onBucketTypeChange?: (bucketType: BucketType | '') => void;
}

const audioQualityOptions: { value: AudioQualityIndicator; label: string; description: string }[] = [
  { value: 'excellent', label: 'Excellent', description: 'Crystal clear audio, no distortion' },
  { value: 'good', label: 'Good', description: 'Clear audio with minor imperfections' },
  { value: 'fair', label: 'Fair', description: 'Audible but with noticeable quality issues' },
  { value: 'poor', label: 'Poor', description: 'Difficult to understand, significant quality issues' },
];

const noiseLevelOptions: { value: NoiseLevel; label: string; icon: React.ReactNode }[] = [
  { value: 'none', label: 'No Background Noise', icon: <VolumeIcon color="success" /> },
  { value: 'low', label: 'Low Background Noise', icon: <VolumeIcon color="primary" /> },
  { value: 'moderate', label: 'Moderate Background Noise', icon: <VolumeIcon color="warning" /> },
  { value: 'high', label: 'High Background Noise', icon: <VolumeIcon color="error" /> },
];

const clarityLevelOptions: { value: ClarityLevel; label: string; description: string }[] = [
  { value: 'very-clear', label: 'Very Clear', description: 'Speaker articulates clearly, easy to understand' },
  { value: 'clear', label: 'Clear', description: 'Generally clear speech with minor unclear moments' },
  { value: 'somewhat-unclear', label: 'Somewhat Unclear', description: 'Some words difficult to understand' },
  { value: 'unclear', label: 'Unclear', description: 'Frequently difficult to understand speaker' },
];

const urgencyLevelOptions: { value: UrgencyLevel; label: string; color: 'success' | 'warning' | 'error' }[] = [
  { value: 'low', label: 'Low Priority', color: 'success' },
  { value: 'medium', label: 'Medium Priority', color: 'warning' },
  { value: 'high', label: 'High Priority', color: 'error' },
];

const bucketTypeOptions: { value: BucketType; label: string; description: string }[] = [
  { value: 'no_touch', label: 'No Touch', description: 'Very high quality ASR draft, no corrections needed' },
  { value: 'low_touch', label: 'Low Touch', description: 'High quality ASR draft, minimal corrections required' },
  { value: 'medium_touch', label: 'Medium Touch', description: 'Medium quality ASR draft, some corrections needed' },
  { value: 'high_touch', label: 'High Touch', description: 'Low quality ASR draft, significant corrections required' },
];

export const MetadataInput: React.FC<MetadataInputProps> = ({
  value,
  onChange,
  disabled = false,
  required = false,
  error,
  showAdvanced = true,
  speakerId = '',
  clientId = '',
  bucketType = '',
  onSpeakerIdChange,
  onClientIdChange,
  onBucketTypeChange,
}) => {
  const theme = useTheme();
  const [expandedSections, setExpandedSections] = useState<string[]>(['required', 'basic']);

  // Handle section expansion
  const handleSectionToggle = useCallback((section: string) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  }, []);

  // Handle field changes
  const handleFieldChange = useCallback((field: keyof ErrorMetadata, fieldValue: any) => {
    onChange({
      ...value,
      [field]: fieldValue,
    });
  }, [value, onChange]);

  // Handle contextual tags
  const handleTagAdd = useCallback((tag: string) => {
    const currentTags = value.contextualTags || [];
    if (!currentTags.includes(tag)) {
      handleFieldChange('contextualTags', [...currentTags, tag]);
    }
  }, [value.contextualTags, handleFieldChange]);

  const handleTagRemove = useCallback((tag: string) => {
    const currentTags = value.contextualTags || [];
    handleFieldChange('contextualTags', currentTags.filter(t => t !== tag));
  }, [value.contextualTags, handleFieldChange]);

  // Predefined contextual tags
  const predefinedTags = [
    'Medical Terminology',
    'Technical Jargon',
    'Accent/Dialect',
    'Fast Speech',
    'Mumbling',
    'Interruption',
    'Multiple Speakers',
    'Phone Quality',
    'Echo/Reverb',
    'Distortion',
  ];

  return (
    <FormControl
      component="fieldset"
      error={!!error}
      disabled={disabled}
      fullWidth
    >
      <FormLabel
        component="legend"
        sx={{ mb: 2 }}
        role="group"
        aria-label="Error metadata"
      >
        Contextual Information
        {required && (
          <Typography component="span" color="error" sx={{ ml: 0.5 }}>
            *
          </Typography>
        )}
      </FormLabel>

      {/* Required Information */}
      <Accordion
        expanded={expandedSections.includes('required')}
        onChange={() => handleSectionToggle('required')}
        disabled={disabled}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon color="error" />
            <Typography variant="h6">Required Information</Typography>
            <Typography component="span" color="error" sx={{ ml: 0.5 }}>
              *
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            {/* Speaker ID */}
            <Grid item xs={12} md={6}>
              <TextField
                label="Speaker ID"
                value={speakerId}
                onChange={(e) => onSpeakerIdChange?.(e.target.value)}
                disabled={disabled}
                required
                fullWidth
                size="small"
                error={!speakerId && required}
                helperText={!speakerId && required ? "Speaker ID is required" : "Unique identifier for the speaker"}
                placeholder="e.g., speaker-456"
              />
            </Grid>

            {/* Speaker Bucket Status */}
            {speakerId && (
              <Grid item xs={12}>
                <SpeakerBucketStatus speakerId={speakerId} compact />
              </Grid>
            )}

            {/* Client ID */}
            <Grid item xs={12} md={6}>
              <TextField
                label="Client ID"
                value={clientId}
                onChange={(e) => onClientIdChange?.(e.target.value)}
                disabled={disabled}
                required
                fullWidth
                size="small"
                error={!clientId && required}
                helperText={!clientId && required ? "Client ID is required" : "Unique identifier for the client"}
                placeholder="e.g., client-789"
              />
            </Grid>

            {/* Bucket Type */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required error={!bucketType && required}>
                <FormLabel sx={{ mb: 1 }}>
                  Speaker Bucket Type
                  <Typography component="span" color="error" sx={{ ml: 0.5 }}>
                    *
                  </Typography>
                </FormLabel>
                <Select
                  value={bucketType || ''}
                  onChange={(e) => onBucketTypeChange?.(e.target.value as BucketType)}
                  disabled={disabled}
                  size="small"
                  displayEmpty
                >
                  <MenuItem value="" disabled>
                    <em>Select ASR output quality bucket</em>
                  </MenuItem>
                  {bucketTypeOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {option.label}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>
                  {!bucketType && required
                    ? "Bucket type is required"
                    : "Categorizes speaker by transcription proficiency level for tracking progression"
                  }
                </FormHelperText>
              </FormControl>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Basic Information */}
      <Accordion
        expanded={expandedSections.includes('basic')}
        onChange={() => handleSectionToggle('basic')}
        disabled={disabled}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <HearingIcon color="primary" />
            <Typography variant="h6">Audio Quality Assessment</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            {/* Audio Quality */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <FormLabel sx={{ mb: 1 }}>Overall Audio Quality</FormLabel>
                <Select
                  value={value.audioQuality || 'good'}
                  onChange={(e) => handleFieldChange('audioQuality', e.target.value)}
                  disabled={disabled}
                  size="small"
                >
                  {audioQualityOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box>
                        <Typography variant="body2">{option.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Background Noise */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <FormLabel sx={{ mb: 1 }}>Background Noise Level</FormLabel>
                <Select
                  value={value.backgroundNoise || 'low'}
                  onChange={(e) => handleFieldChange('backgroundNoise', e.target.value)}
                  disabled={disabled}
                  size="small"
                >
                  {noiseLevelOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {option.icon}
                        <Typography variant="body2">{option.label}</Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Speaker Clarity */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <FormLabel sx={{ mb: 1 }}>Speaker Clarity</FormLabel>
                <Select
                  value={value.speakerClarity || 'clear'}
                  onChange={(e) => handleFieldChange('speakerClarity', e.target.value)}
                  disabled={disabled}
                  size="small"
                >
                  {clarityLevelOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box>
                        <Typography variant="body2">{option.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Urgency Level */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <FormLabel sx={{ mb: 1 }}>Priority Level</FormLabel>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {urgencyLevelOptions.map((option) => (
                    <Chip
                      key={option.value}
                      label={option.label}
                      variant={value.urgencyLevel === option.value ? 'filled' : 'outlined'}
                      color={value.urgencyLevel === option.value ? option.color : 'default'}
                      clickable
                      onClick={() => handleFieldChange('urgencyLevel', option.value)}
                      disabled={disabled}
                      icon={option.value === 'high' ? <WarningIcon /> : undefined}
                    />
                  ))}
                </Box>
              </FormControl>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Advanced Information */}
      {showAdvanced && (
        <Accordion 
          expanded={expandedSections.includes('advanced')}
          onChange={() => handleSectionToggle('advanced')}
          disabled={disabled}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <VoiceIcon color="primary" />
              <Typography variant="h6">Advanced Context</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Speech Rate */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <FormLabel sx={{ mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SpeedIcon fontSize="small" />
                      Speech Rate
                    </Box>
                  </FormLabel>
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={value.speechRate || 5}
                      onChange={(_, newValue) => handleFieldChange('speechRate', newValue)}
                      disabled={disabled}
                      min={1}
                      max={10}
                      step={1}
                      marks={[
                        { value: 1, label: 'Very Slow' },
                        { value: 5, label: 'Normal' },
                        { value: 10, label: 'Very Fast' },
                      ]}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => {
                        if (value <= 3) return 'Slow';
                        if (value <= 7) return 'Normal';
                        return 'Fast';
                      }}
                    />
                  </Box>
                </FormControl>
              </Grid>

              {/* Confidence Rating */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <FormLabel sx={{ mb: 1 }}>Transcription Confidence</FormLabel>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Rating
                      value={value.confidenceRating || 3}
                      onChange={(_, newValue) => handleFieldChange('confidenceRating', newValue)}
                      disabled={disabled}
                      max={5}
                      precision={1}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {value.confidenceRating || 3}/5
                    </Typography>
                  </Box>
                </FormControl>
              </Grid>

              {/* Contextual Tags */}
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <FormLabel sx={{ mb: 1 }}>Contextual Tags</FormLabel>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Select relevant tags or add custom ones:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      {predefinedTags.map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          variant={(value.contextualTags || []).includes(tag) ? 'filled' : 'outlined'}
                          clickable
                          onClick={() => 
                            (value.contextualTags || []).includes(tag) 
                              ? handleTagRemove(tag) 
                              : handleTagAdd(tag)
                          }
                          disabled={disabled}
                          size="small"
                        />
                      ))}
                    </Box>
                    
                    {/* Selected Tags */}
                    {(value.contextualTags || []).length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" gutterBottom>
                          Selected Tags:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {(value.contextualTags || []).map((tag) => (
                            <Chip
                              key={tag}
                              label={tag}
                              onDelete={() => handleTagRemove(tag)}
                              disabled={disabled}
                              size="small"
                              color="primary"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </Box>
                </FormControl>
              </Grid>

              {/* Additional Notes */}
              <Grid item xs={12}>
                <TextField
                  label="Additional Notes"
                  value={value.contextualNotes || ''}
                  onChange={(e) => handleFieldChange('contextualNotes', e.target.value)}
                  disabled={disabled}
                  multiline
                  rows={3}
                  fullWidth
                  placeholder="Describe any additional context that might help understand the error..."
                  inputProps={{
                    maxLength: 500,
                  }}
                  helperText={`${(value.contextualNotes || '').length}/500 characters`}
                />
              </Grid>

              {/* Technical Flags */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={value.hasMultipleSpeakers || false}
                        onChange={(e) => handleFieldChange('hasMultipleSpeakers', e.target.checked)}
                        disabled={disabled}
                      />
                    }
                    label="Multiple Speakers Present"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={value.hasOverlappingSpeech || false}
                        onChange={(e) => handleFieldChange('hasOverlappingSpeech', e.target.checked)}
                        disabled={disabled}
                      />
                    }
                    label="Overlapping Speech"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={value.requiresSpecializedKnowledge || false}
                        onChange={(e) => handleFieldChange('requiresSpecializedKnowledge', e.target.checked)}
                        disabled={disabled}
                      />
                    }
                    label="Requires Specialized Knowledge"
                  />
                </Box>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Error Message */}
      {error && (
        <FormHelperText error>
          {error}
        </FormHelperText>
      )}
    </FormControl>
  );
};

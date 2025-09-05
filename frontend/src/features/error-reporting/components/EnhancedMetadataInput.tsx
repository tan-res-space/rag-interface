/**
 * Enhanced Metadata Input Component
 * 
 * Provides comprehensive metadata input for quality-based bucket management
 * and enhanced error analysis.
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormGroup,
  Checkbox,
  TextField,
  Chip,
  Stack,
  Alert,
  Tooltip,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';

export interface EnhancedMetadata {
  // Core metadata
  audioQuality: 'good' | 'fair' | 'poor';
  speakerClarity: 'clear' | 'somewhat_clear' | 'unclear' | 'very_unclear';
  backgroundNoise: 'none' | 'low' | 'medium' | 'high';
  
  // Enhanced metadata
  numberOfSpeakers: 'one' | 'two' | 'three' | 'four' | 'five';
  overlappingSpeech: boolean;
  requiresSpecializedKnowledge: boolean;
  additionalNotes: string;
}

interface EnhancedMetadataInputProps {
  metadata: EnhancedMetadata;
  onChange: (metadata: EnhancedMetadata) => void;
  bucketType: string;
  onBucketTypeChange: (bucketType: string) => void;
  disabled?: boolean;
  showBucketRecommendation?: boolean;
}

const BUCKET_TYPES = [
  { value: 'no_touch', label: 'No Touch', description: 'Very high quality, no corrections needed' },
  { value: 'low_touch', label: 'Low Touch', description: 'High quality, minimal corrections' },
  { value: 'medium_touch', label: 'Medium Touch', description: 'Medium quality, some corrections needed' },
  { value: 'high_touch', label: 'High Touch', description: 'Low quality, significant corrections needed' },
];

const AUDIO_QUALITY_OPTIONS = [
  { value: 'good', label: 'Good', description: 'Clear audio with minimal distortion' },
  { value: 'fair', label: 'Fair', description: 'Acceptable audio with some issues' },
  { value: 'poor', label: 'Poor', description: 'Difficult to understand audio' },
];

const SPEAKER_CLARITY_OPTIONS = [
  { value: 'clear', label: 'Clear', description: 'Speaker is easy to understand' },
  { value: 'somewhat_clear', label: 'Somewhat Clear', description: 'Speaker is mostly understandable' },
  { value: 'unclear', label: 'Unclear', description: 'Speaker is difficult to understand' },
  { value: 'very_unclear', label: 'Very Unclear', description: 'Speaker is very difficult to understand' },
];

const BACKGROUND_NOISE_OPTIONS = [
  { value: 'none', label: 'None', description: 'No background noise' },
  { value: 'low', label: 'Low', description: 'Minimal background noise' },
  { value: 'medium', label: 'Medium', description: 'Noticeable background noise' },
  { value: 'high', label: 'High', description: 'Significant background noise' },
];

const NUMBER_OF_SPEAKERS_OPTIONS = [
  { value: 'one', label: '1 Speaker' },
  { value: 'two', label: '2 Speakers' },
  { value: 'three', label: '3 Speakers' },
  { value: 'four', label: '4 Speakers' },
  { value: 'five', label: '5+ Speakers' },
];

export const EnhancedMetadataInput: React.FC<EnhancedMetadataInputProps> = ({
  metadata,
  onChange,
  bucketType,
  onBucketTypeChange,
  disabled = false,
  showBucketRecommendation = true,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [recommendedBucket, setRecommendedBucket] = useState<string | null>(null);

  const handleMetadataChange = useCallback((field: keyof EnhancedMetadata, value: any) => {
    const updatedMetadata = { ...metadata, [field]: value };
    onChange(updatedMetadata);
    
    // Calculate recommended bucket based on metadata
    if (showBucketRecommendation) {
      const recommended = calculateRecommendedBucket(updatedMetadata);
      setRecommendedBucket(recommended);
    }
  }, [metadata, onChange, showBucketRecommendation]);

  const calculateRecommendedBucket = (meta: EnhancedMetadata): string => {
    let score = 0;
    
    // Audio quality impact
    if (meta.audioQuality === 'poor') score += 3;
    else if (meta.audioQuality === 'fair') score += 1;
    
    // Speaker clarity impact
    if (meta.speakerClarity === 'very_unclear') score += 3;
    else if (meta.speakerClarity === 'unclear') score += 2;
    else if (meta.speakerClarity === 'somewhat_clear') score += 1;
    
    // Background noise impact
    if (meta.backgroundNoise === 'high') score += 2;
    else if (meta.backgroundNoise === 'medium') score += 1;
    
    // Multiple speakers complexity
    if (meta.numberOfSpeakers !== 'one') score += 1;
    
    // Overlapping speech complexity
    if (meta.overlappingSpeech) score += 2;
    
    // Specialized knowledge requirement
    if (meta.requiresSpecializedKnowledge) score += 1;
    
    // Determine bucket based on score
    if (score >= 6) return 'high_touch';
    if (score >= 4) return 'medium_touch';
    if (score >= 2) return 'low_touch';
    return 'no_touch';
  };

  const getBucketColor = (bucket: string) => {
    switch (bucket) {
      case 'no_touch': return 'success';
      case 'low_touch': return 'info';
      case 'medium_touch': return 'warning';
      case 'high_touch': return 'error';
      default: return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Enhanced Metadata & Quality Assessment
        </Typography>
        
        {/* Quality-Based Bucket Selection */}
        <Box mb={3}>
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend">
              Quality-Based Bucket Assignment
              <Tooltip title="Select the appropriate bucket based on the quality and complexity of the audio">
                <IconButton size="small">
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </FormLabel>
            <RadioGroup
              value={bucketType}
              onChange={(e) => onBucketTypeChange(e.target.value)}
              disabled={disabled}
            >
              <Stack direction="row" spacing={2} flexWrap="wrap">
                {BUCKET_TYPES.map((bucket) => (
                  <FormControlLabel
                    key={bucket.value}
                    value={bucket.value}
                    control={<Radio />}
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {bucket.label}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {bucket.description}
                        </Typography>
                      </Box>
                    }
                  />
                ))}
              </Stack>
            </RadioGroup>
            
            {recommendedBucket && recommendedBucket !== bucketType && (
              <Alert severity="info" sx={{ mt: 1 }}>
                <Typography variant="body2">
                  Based on the metadata, we recommend: 
                  <Chip 
                    label={BUCKET_TYPES.find(b => b.value === recommendedBucket)?.label}
                    color={getBucketColor(recommendedBucket) as any}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </Typography>
              </Alert>
            )}
          </FormControl>
        </Box>

        {/* Core Audio Metadata */}
        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            Audio Quality Assessment
          </Typography>
          
          <Stack spacing={2}>
            {/* Audio Quality */}
            <FormControl component="fieldset">
              <FormLabel component="legend">Audio Quality</FormLabel>
              <RadioGroup
                row
                value={metadata.audioQuality}
                onChange={(e) => handleMetadataChange('audioQuality', e.target.value)}
                disabled={disabled}
              >
                {AUDIO_QUALITY_OPTIONS.map((option) => (
                  <Tooltip key={option.value} title={option.description}>
                    <FormControlLabel
                      value={option.value}
                      control={<Radio />}
                      label={option.label}
                    />
                  </Tooltip>
                ))}
              </RadioGroup>
            </FormControl>

            {/* Speaker Clarity */}
            <FormControl component="fieldset">
              <FormLabel component="legend">Speaker Clarity</FormLabel>
              <RadioGroup
                row
                value={metadata.speakerClarity}
                onChange={(e) => handleMetadataChange('speakerClarity', e.target.value)}
                disabled={disabled}
              >
                {SPEAKER_CLARITY_OPTIONS.map((option) => (
                  <Tooltip key={option.value} title={option.description}>
                    <FormControlLabel
                      value={option.value}
                      control={<Radio />}
                      label={option.label}
                    />
                  </Tooltip>
                ))}
              </RadioGroup>
            </FormControl>

            {/* Background Noise */}
            <FormControl component="fieldset">
              <FormLabel component="legend">Background Noise</FormLabel>
              <RadioGroup
                row
                value={metadata.backgroundNoise}
                onChange={(e) => handleMetadataChange('backgroundNoise', e.target.value)}
                disabled={disabled}
              >
                {BACKGROUND_NOISE_OPTIONS.map((option) => (
                  <Tooltip key={option.value} title={option.description}>
                    <FormControlLabel
                      value={option.value}
                      control={<Radio />}
                      label={option.label}
                    />
                  </Tooltip>
                ))}
              </RadioGroup>
            </FormControl>
          </Stack>
        </Box>

        {/* Enhanced Metadata */}
        <Box mb={3}>
          <Box display="flex" alignItems="center" mb={2}>
            <Typography variant="subtitle1">
              Enhanced Metadata
            </Typography>
            <IconButton
              onClick={() => setShowAdvanced(!showAdvanced)}
              size="small"
              sx={{ ml: 1 }}
            >
              {showAdvanced ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
          
          <Collapse in={showAdvanced}>
            <Stack spacing={2}>
              {/* Number of Speakers */}
              <FormControl component="fieldset">
                <FormLabel component="legend">Number of Speakers</FormLabel>
                <RadioGroup
                  row
                  value={metadata.numberOfSpeakers}
                  onChange={(e) => handleMetadataChange('numberOfSpeakers', e.target.value)}
                  disabled={disabled}
                >
                  {NUMBER_OF_SPEAKERS_OPTIONS.map((option) => (
                    <FormControlLabel
                      key={option.value}
                      value={option.value}
                      control={<Radio />}
                      label={option.label}
                    />
                  ))}
                </RadioGroup>
              </FormControl>

              {/* Boolean Flags */}
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={metadata.overlappingSpeech}
                      onChange={(e) => handleMetadataChange('overlappingSpeech', e.target.checked)}
                      disabled={disabled}
                    />
                  }
                  label="Overlapping Speech"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={metadata.requiresSpecializedKnowledge}
                      onChange={(e) => handleMetadataChange('requiresSpecializedKnowledge', e.target.checked)}
                      disabled={disabled}
                    />
                  }
                  label="Requires Specialized Knowledge"
                />
              </FormGroup>

              {/* Additional Notes */}
              <TextField
                label="Additional Notes"
                multiline
                rows={3}
                value={metadata.additionalNotes}
                onChange={(e) => handleMetadataChange('additionalNotes', e.target.value)}
                disabled={disabled}
                placeholder="Any additional context or observations about this error..."
                inputProps={{ maxLength: 1000 }}
                helperText={`${metadata.additionalNotes.length}/1000 characters`}
              />
            </Stack>
          </Collapse>
        </Box>

        {/* Metadata Summary */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Metadata Summary
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip label={`Audio: ${metadata.audioQuality}`} size="small" />
            <Chip label={`Clarity: ${metadata.speakerClarity}`} size="small" />
            <Chip label={`Noise: ${metadata.backgroundNoise}`} size="small" />
            <Chip label={`Speakers: ${metadata.numberOfSpeakers}`} size="small" />
            {metadata.overlappingSpeech && (
              <Chip label="Overlapping Speech" size="small" color="warning" />
            )}
            {metadata.requiresSpecializedKnowledge && (
              <Chip label="Specialized Knowledge" size="small" color="info" />
            )}
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};

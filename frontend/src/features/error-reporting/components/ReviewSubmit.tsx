/**
 * ReviewSubmit Component
 * Final step of error reporting workflow - review and submit the error report
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  TextFields as TextFieldsIcon,
  Category as CategoryIcon,
  Edit as EditIcon,
  Info as InfoIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import type { 
  TextSelection, 
  ErrorCategory, 
  ErrorMetadata,
  SubmitErrorReportRequest 
} from '@domain/types';

export interface ReviewSubmitProps {
  /** Job ID for the error report */
  jobId: string;
  /** Speaker ID for the error report */
  speakerId: string;
  /** Client ID for the error report */
  clientId: string;
  /** Selected text segments */
  textSelections: TextSelection[];
  /** Selected error categories */
  selectedCategories: ErrorCategory[];
  /** Correction text provided by user */
  correctionText: string;
  /** Metadata information */
  metadata: ErrorMetadata;
  /** Whether the form is currently submitting */
  isSubmitting?: boolean;
  /** Validation errors to display */
  errors?: string[];
  /** Additional className for styling */
  className?: string;
}

export const ReviewSubmit: React.FC<ReviewSubmitProps> = ({
  jobId,
  speakerId,
  clientId,
  textSelections,
  selectedCategories,
  correctionText,
  metadata,
  isSubmitting = false,
  errors = [],
  className,
}) => {
  // Format metadata for display
  const formatMetadataValue = (key: string, value: any): string => {
    switch (key) {
      case 'audioQuality':
        return value.charAt(0).toUpperCase() + value.slice(1);
      case 'backgroundNoise':
        return `${value.charAt(0).toUpperCase() + value.slice(1)} noise level`;
      case 'speakerClarity':
        return value.replace('_', ' ').charAt(0).toUpperCase() + value.slice(1).replace('_', ' ');
      case 'urgencyLevel':
        return `${value.charAt(0).toUpperCase() + value.slice(1)} priority`;
      case 'speechRate':
        return `${value}/10`;
      case 'confidenceRating':
        return `${value}/5 stars`;
      case 'contextualTags':
        return Array.isArray(value) ? value.join(', ') : 'None';
      default:
        return String(value);
    }
  };

  // Get priority color
  const getPriorityColor = (level: string) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box className={className}>
      <Typography variant="h5" gutterBottom>
        Review Your Error Report
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Please review all information below before submitting your error report.
      </Typography>

      {/* Validation Errors */}
      {errors.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Please fix the following errors:
          </Typography>
          <List dense>
            {errors.map((error, index) => (
              <ListItem key={index} sx={{ py: 0 }}>
                <ListItemText primary={`• ${error}`} />
              </ListItem>
            ))}
          </List>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Error Details */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AssignmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Error Details
              </Typography>

              {/* Text Selections */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <TextFieldsIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                  Selected Text ({textSelections.length} selection{textSelections.length !== 1 ? 's' : ''})
                </Typography>
                {textSelections.map((selection, index) => (
                  <Paper key={selection.selectionId} variant="outlined" sx={{ p: 2, mb: 1 }}>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 1 }}>
                      "{selection.text}"
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Position: {selection.startPosition}-{selection.endPosition}
                      {selection.confidence && ` • Confidence: ${Math.round(selection.confidence * 100)}%`}
                    </Typography>
                  </Paper>
                ))}
              </Box>

              {/* Error Categories */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <CategoryIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                  Error Categories ({selectedCategories.length} selected)
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {selectedCategories.map((category) => (
                    <Chip
                      key={category.id}
                      label={category.name}
                      variant="outlined"
                      size="small"
                      icon={<CategoryIcon />}
                    />
                  ))}
                </Box>
              </Box>

              {/* Correction Text */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <EditIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                  Corrected Text
                </Typography>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    "{correctionText}"
                  </Typography>
                </Paper>
              </Box>

              {/* Metadata Summary */}
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  <InfoIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                  Context Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Audio Quality:</strong> {formatMetadataValue('audioQuality', metadata.audioQuality)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Background Noise:</strong> {formatMetadataValue('backgroundNoise', metadata.backgroundNoise)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Speaker Clarity:</strong> {formatMetadataValue('speakerClarity', metadata.speakerClarity)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Priority:</strong>{' '}
                      <Chip
                        label={formatMetadataValue('urgencyLevel', metadata.urgencyLevel)}
                        size="small"
                        color={getPriorityColor(metadata.urgencyLevel) as any}
                        variant="outlined"
                      />
                    </Typography>
                  </Grid>
                  {metadata.speechRate && (
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Speech Rate:</strong> {formatMetadataValue('speechRate', metadata.speechRate)}
                      </Typography>
                    </Grid>
                  )}
                  {metadata.confidenceRating && (
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Confidence:</strong> {formatMetadataValue('confidenceRating', metadata.confidenceRating)}
                      </Typography>
                    </Grid>
                  )}
                  {metadata.contextualTags && metadata.contextualTags.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="body2">
                        <strong>Tags:</strong> {formatMetadataValue('contextualTags', metadata.contextualTags)}
                      </Typography>
                    </Grid>
                  )}
                  {metadata.contextualNotes && (
                    <Grid item xs={12}>
                      <Typography variant="body2">
                        <strong>Notes:</strong> {metadata.contextualNotes}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Submission Details */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Submission Details
              </Typography>

              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <AssignmentIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Job ID"
                    secondary={jobId}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <PersonIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Speaker ID"
                    secondary={speakerId}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <PersonIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Client ID"
                    secondary={clientId}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <ScheduleIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Timestamp"
                    secondary={new Date().toLocaleString()}
                  />
                </ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>
                Validation Status
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Text selection provided" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Error categories selected" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Correction text provided" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="All required fields completed" />
                </ListItem>
              </List>

              {isSubmitting && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Submitting your error report...
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

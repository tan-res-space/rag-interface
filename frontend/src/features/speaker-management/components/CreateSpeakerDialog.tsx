/**
 * Create/Edit Speaker Dialog Component
 * 
 * Dialog for creating new speakers or editing existing ones
 * with form validation and error handling.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
  Grid,
  IconButton,
} from '@mui/material';
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useAppDispatch } from '@/app/hooks';
import { createSpeaker, updateSpeaker } from '../speaker-slice';
import { Speaker, SpeakerBucket, SpeakerFormData } from '@/domain/types/speaker';

interface CreateSpeakerDialogProps {
  speaker?: Speaker | null; // null for create, speaker object for edit
  open: boolean;
  onClose: () => void;
  onSpeakerCreated: (speaker: Speaker) => void;
}

interface FormErrors {
  speaker_identifier?: string;
  speaker_name?: string;
  initial_bucket?: string;
}

export const CreateSpeakerDialog: React.FC<CreateSpeakerDialogProps> = ({
  speaker,
  open,
  onClose,
  onSpeakerCreated,
}) => {
  const dispatch = useAppDispatch();
  
  // Form state
  const [formData, setFormData] = useState<SpeakerFormData>({
    speaker_identifier: '',
    speaker_name: '',
    initial_bucket: SpeakerBucket.HIGH_TOUCH,
    metadata: {},
  });
  
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Initialize form data when speaker changes
  useEffect(() => {
    if (speaker) {
      // Edit mode
      setFormData({
        speaker_identifier: speaker.speaker_identifier,
        speaker_name: speaker.speaker_name,
        initial_bucket: speaker.current_bucket,
        metadata: speaker.metadata || {},
      });
    } else {
      // Create mode
      setFormData({
        speaker_identifier: '',
        speaker_name: '',
        initial_bucket: SpeakerBucket.HIGH_TOUCH,
        metadata: {},
      });
    }
    
    // Clear errors when dialog opens/closes
    setErrors({});
    setSubmitError(null);
  }, [speaker, open]);

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.speaker_identifier.trim()) {
      newErrors.speaker_identifier = 'Speaker identifier is required';
    } else if (!/^[A-Z0-9_]+$/.test(formData.speaker_identifier)) {
      newErrors.speaker_identifier = 'Speaker identifier must contain only uppercase letters, numbers, and underscores';
    }

    if (!formData.speaker_name.trim()) {
      newErrors.speaker_name = 'Speaker name is required';
    } else if (formData.speaker_name.trim().length < 2) {
      newErrors.speaker_name = 'Speaker name must be at least 2 characters long';
    }

    if (!formData.initial_bucket) {
      newErrors.initial_bucket = 'Initial bucket is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form field changes
  const handleFieldChange = (field: keyof SpeakerFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));

    // Clear field error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setSubmitError(null);

    try {
      let result;
      
      if (speaker) {
        // Edit mode
        result = await dispatch(updateSpeaker({
          speakerId: speaker.speaker_id,
          speakerData: formData,
        })).unwrap();
      } else {
        // Create mode
        result = await dispatch(createSpeaker(formData)).unwrap();
      }

      onSpeakerCreated(result);
    } catch (error: any) {
      setSubmitError(error.message || 'Failed to save speaker');
    } finally {
      setLoading(false);
    }
  };

  // Handle dialog close
  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const isEditMode = !!speaker;
  const dialogTitle = isEditMode ? 'Edit Speaker' : 'Create New Speaker';

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        component: 'form',
        onSubmit: (e: React.FormEvent) => {
          e.preventDefault();
          handleSubmit();
        },
      }}
    >
      {/* Dialog Header */}
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PersonIcon color="primary" />
            <Typography variant="h6">{dialogTitle}</Typography>
          </Box>
          
          <IconButton onClick={handleClose} size="small" disabled={loading}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      {/* Dialog Content */}
      <DialogContent>
        {submitError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {submitError}
          </Alert>
        )}

        <Grid container spacing={2}>
          {/* Speaker Identifier */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Speaker Identifier"
              value={formData.speaker_identifier}
              onChange={(e) => handleFieldChange('speaker_identifier', e.target.value.toUpperCase())}
              error={!!errors.speaker_identifier}
              helperText={errors.speaker_identifier || 'Unique identifier (e.g., SPEAKER_001)'}
              required
              disabled={loading || isEditMode} // Don't allow editing identifier
              placeholder="SPEAKER_001"
            />
          </Grid>

          {/* Speaker Name */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Speaker Name"
              value={formData.speaker_name}
              onChange={(e) => handleFieldChange('speaker_name', e.target.value)}
              error={!!errors.speaker_name}
              helperText={errors.speaker_name || 'Full name of the speaker'}
              required
              disabled={loading}
              placeholder="Dr. John Smith"
            />
          </Grid>

          {/* Initial/Current Bucket */}
          <Grid item xs={12}>
            <FormControl fullWidth error={!!errors.initial_bucket} disabled={loading}>
              <InputLabel required>
                {isEditMode ? 'Current Bucket' : 'Initial Bucket'}
              </InputLabel>
              <Select
                value={formData.initial_bucket}
                onChange={(e) => handleFieldChange('initial_bucket', e.target.value)}
                label={isEditMode ? 'Current Bucket' : 'Initial Bucket'}
              >
                {Object.values(SpeakerBucket).map((bucket) => (
                  <MenuItem key={bucket} value={bucket}>
                    {bucket.replace('_', ' ')}
                  </MenuItem>
                ))}
              </Select>
              {errors.initial_bucket && (
                <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                  {errors.initial_bucket}
                </Typography>
              )}
            </FormControl>
          </Grid>

          {/* Additional Information */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Department (Optional)"
              value={formData.metadata?.department || ''}
              onChange={(e) => handleFieldChange('metadata', {
                ...formData.metadata,
                department: e.target.value,
              })}
              disabled={loading}
              placeholder="Cardiology"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Location (Optional)"
              value={formData.metadata?.location || ''}
              onChange={(e) => handleFieldChange('metadata', {
                ...formData.metadata,
                location: e.target.value,
              })}
              disabled={loading}
              placeholder="Main Hospital"
            />
          </Grid>

          {/* Notes */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Notes (Optional)"
              value={formData.metadata?.notes || ''}
              onChange={(e) => handleFieldChange('metadata', {
                ...formData.metadata,
                notes: e.target.value,
              })}
              disabled={loading}
              placeholder="Additional notes about this speaker..."
            />
          </Grid>
        </Grid>

        {/* Information Box */}
        <Box sx={{ mt: 2 }}>
          <Alert severity="info">
            <Typography variant="body2">
              {isEditMode 
                ? 'Changes will be saved immediately. The speaker identifier cannot be modified.'
                : 'New speakers will be created with the specified initial bucket. Quality metrics will be calculated as data becomes available.'
              }
            </Typography>
          </Alert>
        </Box>
      </DialogContent>

      {/* Dialog Actions */}
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button 
          onClick={handleClose} 
          disabled={loading}
        >
          Cancel
        </Button>
        
        <Button
          type="submit"
          variant="contained"
          startIcon={<SaveIcon />}
          disabled={loading}
          sx={{ minWidth: 120 }}
        >
          {loading ? 'Saving...' : (isEditMode ? 'Update' : 'Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateSpeakerDialog;

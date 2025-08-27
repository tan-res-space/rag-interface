/**
 * Session Setup Dialog Component
 * 
 * Dialog for creating new MT validation sessions with
 * speaker selection, test data configuration, and settings.
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
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  Autocomplete,
  Switch,
  FormControlLabel,
  Stepper,
  Step,
  StepLabel,
  IconButton,
} from '@mui/material';
import {
  Close as CloseIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { StartValidationSessionRequest } from '@/domain/types/mt-validation';
import { Speaker } from '@/domain/types/speaker';

interface SessionSetupDialogProps {
  open: boolean;
  onClose: () => void;
  onCreateSession: (sessionData: StartValidationSessionRequest) => void;
}

interface SessionFormData {
  session_name: string;
  speaker_id: string;
  speaker_name: string;
  test_data_count: number;
  mt_user_id: string;
  priority: 'low' | 'medium' | 'high';
  auto_advance: boolean;
  include_ser_metrics: boolean;
  randomize_order: boolean;
}

const steps = ['Speaker Selection', 'Test Data', 'Settings'];

// Mock data - in real app, this would come from API
const mockSpeakers: Speaker[] = [
  {
    speaker_id: '1',
    speaker_identifier: 'SPEAKER_001',
    speaker_name: 'Dr. John Smith',
    current_bucket: 'HIGH_TOUCH' as any,
    note_count: 150,
    average_ser_score: 18.5,
    quality_trend: 'improving' as any,
    should_transition: true,
    has_sufficient_data: true,
    created_at: '2025-01-01',
    updated_at: '2025-01-01',
  },
  {
    speaker_id: '2',
    speaker_identifier: 'SPEAKER_002',
    speaker_name: 'Dr. Sarah Johnson',
    current_bucket: 'MEDIUM_TOUCH' as any,
    note_count: 89,
    average_ser_score: 12.3,
    quality_trend: 'stable' as any,
    should_transition: false,
    has_sufficient_data: true,
    created_at: '2025-01-01',
    updated_at: '2025-01-01',
  },
];

export const SessionSetupDialog: React.FC<SessionSetupDialogProps> = ({
  open,
  onClose,
  onCreateSession,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<SessionFormData>({
    session_name: '',
    speaker_id: '',
    speaker_name: '',
    test_data_count: 20,
    mt_user_id: 'current-user', // Would come from auth context
    priority: 'medium',
    auto_advance: true,
    include_ser_metrics: true,
    randomize_order: false,
  });
  const [selectedSpeaker, setSelectedSpeaker] = useState<Speaker | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      setActiveStep(0);
      setFormData({
        session_name: '',
        speaker_id: '',
        speaker_name: '',
        test_data_count: 20,
        mt_user_id: 'current-user',
        priority: 'medium',
        auto_advance: true,
        include_ser_metrics: true,
        randomize_order: false,
      });
      setSelectedSpeaker(null);
      setErrors({});
    }
  }, [open]);

  // Validation
  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 0: // Speaker Selection
        if (!formData.speaker_id) {
          newErrors.speaker_id = 'Please select a speaker';
        }
        if (!formData.session_name.trim()) {
          newErrors.session_name = 'Session name is required';
        }
        break;
      case 1: // Test Data
        if (formData.test_data_count < 1 || formData.test_data_count > 100) {
          newErrors.test_data_count = 'Test data count must be between 1 and 100';
        }
        break;
      case 2: // Settings
        // No validation needed for settings step
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle field changes
  const handleFieldChange = (field: keyof SessionFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Handle speaker selection
  const handleSpeakerSelect = (speaker: Speaker | null) => {
    setSelectedSpeaker(speaker);
    if (speaker) {
      handleFieldChange('speaker_id', speaker.speaker_id);
      handleFieldChange('speaker_name', speaker.speaker_name);
      
      // Auto-generate session name
      if (!formData.session_name) {
        const timestamp = new Date().toLocaleDateString();
        handleFieldChange('session_name', `Validation - ${speaker.speaker_name} - ${timestamp}`);
      }
    } else {
      handleFieldChange('speaker_id', '');
      handleFieldChange('speaker_name', '');
    }
  };

  // Navigation
  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  // Handle form submission
  const handleSubmit = () => {
    if (!validateStep(activeStep)) return;

    const sessionData: StartValidationSessionRequest = {
      speaker_id: formData.speaker_id,
      session_name: formData.session_name,
      test_data_ids: [], // Would be populated based on speaker and criteria
      mt_user_id: formData.mt_user_id,
      session_metadata: {
        priority: formData.priority,
        auto_advance: formData.auto_advance,
        include_ser_metrics: formData.include_ser_metrics,
        randomize_order: formData.randomize_order,
        test_data_count: formData.test_data_count,
      },
    };

    onCreateSession(sessionData);
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Select Speaker and Session Details
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Session Name"
                  value={formData.session_name}
                  onChange={(e) => handleFieldChange('session_name', e.target.value)}
                  error={!!errors.session_name}
                  helperText={errors.session_name}
                  placeholder="e.g., Quality Review - Dr. Smith - Jan 2025"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Autocomplete
                  options={mockSpeakers}
                  getOptionLabel={(option) => `${option.speaker_name} (${option.speaker_identifier})`}
                  value={selectedSpeaker}
                  onChange={(_, value) => handleSpeakerSelect(value)}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Select Speaker"
                      error={!!errors.speaker_id}
                      helperText={errors.speaker_id || 'Choose the speaker to validate'}
                    />
                  )}
                  renderOption={(props, option) => (
                    <Box component="li" {...props}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                        <PersonIcon color="primary" />
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="body1">{option.speaker_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {option.speaker_identifier} • {option.note_count} notes • 
                            SER: {option.average_ser_score.toFixed(1)}%
                          </Typography>
                        </Box>
                        <Chip
                          label={option.current_bucket.replace('_', ' ')}
                          size="small"
                          color={option.should_transition ? 'warning' : 'default'}
                        />
                      </Box>
                    </Box>
                  )}
                />
              </Grid>

              {selectedSpeaker && (
                <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        Speaker Summary
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Current Bucket
                          </Typography>
                          <Typography variant="body1">
                            {selectedSpeaker.current_bucket.replace('_', ' ')}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Average SER Score
                          </Typography>
                          <Typography variant="body1">
                            {selectedSpeaker.average_ser_score.toFixed(1)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Total Notes
                          </Typography>
                          <Typography variant="body1">
                            {selectedSpeaker.note_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Quality Trend
                          </Typography>
                          <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                            {selectedSpeaker.quality_trend.replace('_', ' ')}
                          </Typography>
                        </Grid>
                      </Grid>
                      
                      {selectedSpeaker.should_transition && (
                        <Alert severity="info" sx={{ mt: 2 }}>
                          This speaker is recommended for bucket transition based on quality improvements.
                        </Alert>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Configure Test Data
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Number of Test Items"
                  value={formData.test_data_count}
                  onChange={(e) => handleFieldChange('test_data_count', parseInt(e.target.value))}
                  error={!!errors.test_data_count}
                  helperText={errors.test_data_count || 'Recommended: 15-25 items'}
                  inputProps={{ min: 1, max: 100 }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={formData.priority}
                    onChange={(e) => handleFieldChange('priority', e.target.value)}
                    label="Priority"
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.randomize_order}
                      onChange={(e) => handleFieldChange('randomize_order', e.target.checked)}
                    />
                  }
                  label="Randomize item order"
                />
                <Typography variant="caption" color="text.secondary" display="block">
                  Randomizing helps reduce bias in validation results
                </Typography>
              </Grid>
            </Grid>
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Validation Settings
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.auto_advance}
                      onChange={(e) => handleFieldChange('auto_advance', e.target.checked)}
                    />
                  }
                  label="Auto-advance to next item after feedback submission"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.include_ser_metrics}
                      onChange={(e) => handleFieldChange('include_ser_metrics', e.target.checked)}
                    />
                  }
                  label="Show SER metrics panel by default"
                />
              </Grid>
            </Grid>

            <Alert severity="info" sx={{ mt: 2 }}>
              These settings can be changed during the validation session.
            </Alert>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ sx: { height: '80vh' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Create Validation Session</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Stepper activeStep={activeStep}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>

        {renderStepContent(activeStep)}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Cancel
        </Button>
        
        {activeStep > 0 && (
          <Button onClick={handleBack}>
            Back
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button
            onClick={handleNext}
            variant="contained"
            disabled={!formData.speaker_id && activeStep === 0}
          >
            Next
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            variant="contained"
            color="primary"
          >
            Create Session
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default SessionSetupDialog;

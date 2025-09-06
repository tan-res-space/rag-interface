/**
 * Enhanced Error Reporting Form Component
 * Integrates all error reporting components with step-by-step workflow
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Divider,
  TextField,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
  Send as SubmitIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { TextSelection } from './TextSelection';
import { ErrorCategorization } from './ErrorCategorization';
import { CorrectionInput } from './CorrectionInput';
import { EnhancedMetadataInput } from './EnhancedMetadataInput';
import { VectorSimilarity } from './VectorSimilarity';
import { ReviewSubmit } from './ReviewSubmit';
import type {
  TextSelection as TextSelectionType,
  ErrorCategory,
  ErrorMetadata,
  SimilarityResult,
  SubmitErrorReportRequest,
  ValidationError,
  BucketType
} from '@domain/types';
import type { EnhancedMetadata } from './EnhancedMetadataInput';

export interface ErrorReportingFormProps {
  jobId: string;
  speakerId: string;
  documentText: string;
  onSubmit: (report: SubmitErrorReportRequest) => Promise<void>;
  onCancel: () => void;
  isValid?: boolean;
  errors?: ValidationError[];
  isSubmitting?: boolean;
  categories?: ErrorCategory[];
  similarPatterns?: SimilarityResult[];
  onSimilaritySearch?: (text: string) => void;
}

interface FormData {
  textSelections: TextSelectionType[];
  selectedCategories: string[];
  correctionText: string;
  metadata: EnhancedMetadata;
  speakerId: string;
  clientId: string;
  bucketType: string;
}

const steps = [
  {
    label: 'Select Error Text',
    description: 'Highlight the text segments that contain errors',
    key: 'textSelection',
  },
  {
    label: 'Categorize Errors',
    description: 'Choose the types of errors found',
    key: 'categorization',
  },
  {
    label: 'Provide Correction',
    description: 'Enter the corrected text',
    key: 'correction',
  },
  {
    label: 'Add Context',
    description: 'Provide additional contextual information',
    key: 'metadata',
  },
  {
    label: 'Review & Submit',
    description: 'Review your error report before submission',
    key: 'review',
  },
];

export const ErrorReportingForm: React.FC<ErrorReportingFormProps> = ({
  jobId,
  speakerId,
  documentText,
  onSubmit,
  onCancel,
  isValid = true,
  errors = [],
  isSubmitting = false,
  categories = [],
  similarPatterns = [],
  onSimilaritySearch,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Form state
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    textSelections: [],
    selectedCategories: [],
    correctionText: '',
    metadata: {
      audioQuality: 'good',
      backgroundNoise: 'low',
      speakerClarity: 'clear',
      numberOfSpeakers: 'one',
      overlappingSpeech: false,
      requiresSpecializedKnowledge: false,
      additionalNotes: '',
    },
    speakerId: speakerId || '',
    clientId: '',
    bucketType: '',
  });

  // Step validation
  const [stepValidation, setStepValidation] = useState<boolean[]>([false, false, false, false, true]);

  // Update step validation
  useEffect(() => {
    const newValidation = [
      formData.textSelections.length > 0, // Text selection required
      formData.selectedCategories.length > 0, // At least one category required
      formData.correctionText.trim().length > 0, // Correction text required
      formData.speakerId.trim().length > 0 && formData.clientId.trim().length > 0 && formData.bucketType !== '', // Speaker ID, Client ID, and Bucket Type required
      true, // Review step is always valid
    ];
    setStepValidation(newValidation);
  }, [formData]);

  // Handle form data updates
  const updateFormData = useCallback((field: keyof FormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  // Handle step navigation
  const handleNext = useCallback(() => {
    if (activeStep < steps.length - 1) {
      setActiveStep(prev => prev + 1);
    }
  }, [activeStep]);

  const handleBack = useCallback(() => {
    if (activeStep > 0) {
      setActiveStep(prev => prev - 1);
    }
  }, [activeStep]);

  const handleStepClick = useCallback((stepIndex: number) => {
    // Allow navigation to previous steps or next step if current is valid
    if (stepIndex <= activeStep || stepValidation[activeStep]) {
      setActiveStep(stepIndex);
    }
  }, [activeStep, stepValidation]);

  // Handle form submission
  const handleSubmit = useCallback(async () => {
    const report: SubmitErrorReportRequest = {
      jobId,
      speakerId: formData.speakerId,
      clientId: formData.clientId,
      bucketType: formData.bucketType as BucketType,
      textSelections: formData.textSelections,
      selectedCategories: formData.selectedCategories.map(id =>
        categories.find(cat => cat.id === id)!
      ),
      correctionText: formData.correctionText,
      metadata: formData.metadata,
    };

    try {
      await onSubmit(report);
    } catch (error) {
      console.error('Error submitting report:', error);
    }
  }, [jobId, formData, categories, onSubmit]);

  // Handle similarity pattern selection
  const handlePatternSelect = useCallback((pattern: SimilarityResult) => {
    updateFormData('correctionText', pattern.suggestedCorrection);
  }, [updateFormData]);

  // Get step content
  const getStepContent = useCallback((stepIndex: number) => {
    switch (stepIndex) {
      case 0:
        return (
          <TextSelection
            text={documentText}
            selections={formData.textSelections}
            onSelectionChange={(selections) => updateFormData('textSelections', selections)}
            disabled={isSubmitting}
            maxSelections={10}
            allowOverlapping={false}
          />
        );

      case 1:
        return (
          <ErrorCategorization
            categories={categories}
            selectedCategories={formData.selectedCategories}
            onCategoriesChange={(categories) => updateFormData('selectedCategories', categories)}
            disabled={isSubmitting}
            required
            maxSelections={5}
            searchable
            showHierarchy
          />
        );

      case 2:
        return (
          <Box>
            <CorrectionInput
              value={formData.correctionText}
              onChange={(value) => updateFormData('correctionText', value)}
              originalText={formData.textSelections.map(sel => sel.text).join(' ')}
              similarPatterns={similarPatterns}
              onSimilaritySearch={onSimilaritySearch}
              disabled={isSubmitting}
              required
              voiceInputEnabled
              aiSuggestionsEnabled
            />
            
            {/* Vector Similarity Results */}
            {similarPatterns.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <VectorSimilarity
                  similarityResults={similarPatterns}
                  onPatternSelect={handlePatternSelect}
                  disabled={isSubmitting}
                  showPatternAnalysis
                  maxResults={5}
                />
              </Box>
            )}
          </Box>
        );

      case 3:
        return (
          <Box>
            {/* Speaker and Client Information */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Speaker Information
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  label="Speaker ID"
                  value={formData.speakerId}
                  onChange={(e) => updateFormData('speakerId', e.target.value)}
                  disabled={isSubmitting}
                  required
                  fullWidth
                  size="small"
                />
                <TextField
                  label="Client ID"
                  value={formData.clientId}
                  onChange={(e) => updateFormData('clientId', e.target.value)}
                  disabled={isSubmitting}
                  required
                  fullWidth
                  size="small"
                />
              </Box>
            </Box>

            {/* Enhanced Metadata Input */}
            <EnhancedMetadataInput
              metadata={formData.metadata}
              onChange={(metadata) => updateFormData('metadata', metadata)}
              bucketType={formData.bucketType}
              onBucketTypeChange={(bucketType) => updateFormData('bucketType', bucketType)}
              disabled={isSubmitting}
              showBucketRecommendation={true}
            />
          </Box>
        );

      case 4:
        return (
          <ReviewSubmit
            jobId={jobId}
            speakerId={formData.speakerId}
            clientId={formData.clientId}
            textSelections={formData.textSelections}
            selectedCategories={formData.selectedCategories.map(categoryId =>
              categories.find(cat => cat.id === categoryId)!
            ).filter(Boolean)}
            correctionText={formData.correctionText}
            metadata={formData.metadata}
            isSubmitting={isSubmitting}
            errors={errors?.map(err => err.message) || []}
          />
        );

      default:
        return null;
    }
  }, [
    documentText,
    formData,
    categories,
    similarPatterns,
    isSubmitting,
    theme,
    updateFormData,
    onSimilaritySearch,
    handlePatternSelect,
  ]);

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Report ASR Error
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Help improve transcription accuracy by reporting errors and providing corrections.
      </Typography>

      {/* Error Display */}
      {errors.length > 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="body2">
            Please fix the following errors:
          </Typography>
          <ul>
            {errors.map((error, index) => (
              <li key={index}>{error.message}</li>
            ))}
          </ul>
        </Alert>
      )}

      {/* Stepper */}
      <Stepper 
        activeStep={activeStep} 
        orientation={isMobile ? 'vertical' : 'horizontal'}
        sx={{ mb: 3 }}
      >
        {steps.map((step, index) => (
          <Step 
            key={step.key}
            completed={index < activeStep || stepValidation[index]}
          >
            <StepLabel
              onClick={() => handleStepClick(index)}
              sx={{ cursor: 'pointer' }}
              icon={stepValidation[index] ? <CheckIcon color="success" /> : undefined}
            >
              <Typography variant="subtitle2">{step.label}</Typography>
              <Typography variant="caption" color="text.secondary">
                {step.description}
              </Typography>
            </StepLabel>
            {isMobile && (
              <StepContent>
                <Box sx={{ mt: 2, mb: 1 }}>
                  {getStepContent(index)}
                </Box>
              </StepContent>
            )}
          </Step>
        ))}
      </Stepper>

      {/* Step Content (Desktop) */}
      {!isMobile && (
        <Paper sx={{ p: 3, mb: 3 }}>
          {getStepContent(activeStep)}
        </Paper>
      )}

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          onClick={onCancel}
          disabled={isSubmitting}
          variant="outlined"
        >
          Cancel
        </Button>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            onClick={handleBack}
            disabled={activeStep === 0 || isSubmitting}
            startIcon={<BackIcon />}
          >
            Back
          </Button>

          {activeStep === steps.length - 1 ? (
            <Button
              onClick={handleSubmit}
              disabled={!isValid || isSubmitting}
              variant="contained"
              startIcon={isSubmitting ? <CircularProgress size={16} /> : <SubmitIcon />}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Report'}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              disabled={!stepValidation[activeStep] || isSubmitting}
              variant="contained"
              endIcon={<NextIcon />}
            >
              Next
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

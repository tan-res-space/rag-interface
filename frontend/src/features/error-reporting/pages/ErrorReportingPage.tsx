/**
 * Complete Error Reporting Page
 * Implements the full 5-step workflow with backend integration
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Container,
  Alert,
  Snackbar,
  CircularProgress,
  Backdrop,
} from '@mui/material';
import { ErrorReportingForm } from '../components/ErrorReportingForm';
import { useSubmitErrorReportMutation } from '@infrastructure/api/error-report-api';
import type {
  TextSelection as TextSelectionType,
  ErrorCategory,
  SimilarityResult,
  SubmitErrorReportRequest,
  ValidationError
} from '@domain/types';

// Sample document text for demonstration
const sampleDocumentText = `The patient has a history of hypertension and diabetes. The doctor prescribed medication for the condition. During the examination, the patient complained of chest pain and shortness of breath. Blood pressure readings were elevated at 160/95 mmHg. Laboratory results showed glucose levels of 180 mg/dL, indicating poor glycemic control. The physician recommended lifestyle modifications including dietary changes and regular exercise. A follow-up appointment was scheduled for next month to monitor progress and adjust treatment as needed.`;

// Mock API functions
const mockApiDelay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const fetchErrorCategories = async (): Promise<ErrorCategory[]> => {
  await mockApiDelay(500);
  return [
    {
      id: 'pronunciation',
      name: 'Pronunciation',
      description: 'Pronunciation errors and mispronunciations',
      isActive: true,
    },
    {
      id: 'grammar',
      name: 'Grammar',
      description: 'Grammatical errors including subject-verb agreement and tense issues',
      isActive: true,
    },
    {
      id: 'medical',
      name: 'Medical Terminology',
      description: 'Medical term errors and terminology issues',
      parentCategory: 'pronunciation',
      isActive: true,
    },
    {
      id: 'spelling',
      name: 'Spelling',
      description: 'Spelling mistakes and typos',
      isActive: true,
    },
    {
      id: 'punctuation',
      name: 'Punctuation',
      description: 'Missing or incorrect punctuation marks',
      parentCategory: 'grammar',
      isActive: true,
    },
    {
      id: 'terminology',
      name: 'Technical Terminology',
      description: 'Technical terms and domain-specific vocabulary errors',
      isActive: true,
    },
    {
      id: 'formatting',
      name: 'Formatting',
      description: 'Text formatting and structure issues',
      isActive: true,
    },
    {
      id: 'context',
      name: 'Contextual',
      description: 'Context-dependent errors and misinterpretations',
      isActive: true,
    },
  ];
};

const searchSimilarPatterns = async (text: string): Promise<SimilarityResult[]> => {
  await mockApiDelay(800);

  // Mock similarity results based on common medical terms
  const mockPatterns: Record<string, SimilarityResult[]> = {
    'hypertension': [
      {
        patternId: 'pattern-1',
        similarText: 'hypertension',
        confidence: 0.95,
        frequency: 12,
        suggestedCorrection: 'high blood pressure',
        speakerIds: ['speaker-1', 'speaker-3'],
        category: 'medical',
      },
      {
        patternId: 'pattern-2',
        similarText: 'hypertension',
        confidence: 0.87,
        frequency: 8,
        suggestedCorrection: 'elevated blood pressure',
        speakerIds: ['speaker-2'],
        category: 'medical',
      },
    ],
    'diabetes': [
      {
        patternId: 'pattern-3',
        similarText: 'diabetes',
        confidence: 0.92,
        frequency: 15,
        suggestedCorrection: 'diabetes mellitus',
        speakerIds: ['speaker-1', 'speaker-4'],
        category: 'medical',
      },
      {
        patternId: 'pattern-4',
        similarText: 'diabetes',
        confidence: 0.89,
        frequency: 6,
        suggestedCorrection: 'type 2 diabetes',
        speakerIds: ['speaker-3'],
        category: 'medical',
      },
    ],
    'mmHg': [
      {
        patternId: 'pattern-5',
        similarText: 'mmHg',
        confidence: 0.98,
        frequency: 20,
        suggestedCorrection: 'millimeters of mercury',
        speakerIds: ['speaker-1', 'speaker-2', 'speaker-3'],
        category: 'medical',
      },
    ],
  };

  // Find patterns for the search text
  const searchLower = text.toLowerCase();
  for (const [key, patterns] of Object.entries(mockPatterns)) {
    if (searchLower.includes(key.toLowerCase())) {
      return patterns;
    }
  }

  return [];
};

// Transform frontend data to backend format
const transformToBackendFormat = (report: SubmitErrorReportRequest, currentUserId: string) => {
  // Combine all text selections into original text
  const originalText = report.textSelections.map(sel => sel.text).join(' ');

  // Calculate start and end positions (use first and last selection)
  const startPosition = report.textSelections.length > 0 ? report.textSelections[0].startPosition : 0;
  const endPosition = report.textSelections.length > 0 ?
    report.textSelections[report.textSelections.length - 1].endPosition : 0;

  return {
    job_id: report.jobId,
    speaker_id: report.speakerId,
    bucket_type: report.bucketType,
    original_text: originalText,
    corrected_text: report.correctionText,
    error_categories: report.selectedCategories.map(cat => cat.name),
    severity_level: report.metadata.urgencyLevel, // Map urgency to severity
    start_position: startPosition,
    end_position: endPosition,
    reported_by: currentUserId,
    context_notes: report.metadata.contextualNotes,
    metadata: {
      audio_quality: report.metadata.audioQuality,
      background_noise: report.metadata.backgroundNoise,
      speaker_clarity: report.metadata.speakerClarity,
      urgency_level: report.metadata.urgencyLevel,
      client_id: report.clientId,
      ...report.metadata
    }
  };
};

const ErrorReportingPage: React.FC = () => {
  const navigate = useNavigate();

  // API hooks
  const [submitErrorReportMutation] = useSubmitErrorReportMutation();



  // State management
  const [categories, setCategories] = useState<ErrorCategory[]>([]);
  const [similarPatterns, setSimilarPatterns] = useState<SimilarityResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Load initial data
  useEffect(() => {
    const loadCategories = async () => {
      try {
        setIsLoading(true);
        const fetchedCategories = await fetchErrorCategories();
        setCategories(fetchedCategories);
      } catch (error) {
        console.error('Failed to load categories:', error);
        setErrorMessage('Failed to load error categories. Please refresh the page.');
      } finally {
        setIsLoading(false);
      }
    };

    loadCategories();
  }, []);

  // Handle similarity search
  const handleSimilaritySearch = useCallback(async (text: string) => {
    if (!text.trim()) {
      setSimilarPatterns([]);
      return;
    }

    try {
      const patterns = await searchSimilarPatterns(text);
      setSimilarPatterns(patterns);
    } catch (error) {
      console.error('Similarity search failed:', error);
      // Don't show error for similarity search failures
      setSimilarPatterns([]);
    }
  }, []);

  // Handle form submission
  const handleSubmit = useCallback(async (report: SubmitErrorReportRequest) => {
    try {
      setIsSubmitting(true);
      setValidationErrors([]);
      setErrorMessage('');

      // Transform frontend data to backend format
      const backendData = transformToBackendFormat(report, 'current-user-id'); // TODO: Get real user ID

      // Submit to real API
      const result = await submitErrorReportMutation(backendData).unwrap();



      // Navigate to success page with report details
      navigate('/error-reporting/success', {
        state: {
          reportId: result.errorId,
          submissionTime: new Date().toLocaleString(),
          speakerId: report.speakerId,
          clientId: report.clientId,
          jobId: report.jobId,
          bucketProgression: result.bucket_progression
        }
      });

    } catch (error) {
      console.error('Error submitting report:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to submit error report');
      setIsSubmitting(false);
    }
  }, [navigate, submitErrorReportMutation]);

  // Handle form cancellation
  const handleCancel = useCallback(() => {
    // In a real app, this might navigate back or show a confirmation dialog
    if (window.confirm('Are you sure you want to cancel? All progress will be lost.')) {
      window.location.reload();
    }
  }, []);

  // Close success message
  const handleCloseSuccess = useCallback(() => {
    setSuccessMessage('');
  }, []);

  // Close error message
  const handleCloseError = useCallback(() => {
    setErrorMessage('');
  }, []);

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
          <CircularProgress size={48} />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Loading Error Reporting Interface...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 3 }}>
        <Typography variant="h3" gutterBottom align="center">
          ASR Error Reporting System
        </Typography>

        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
          Report transcription errors to help improve our ASR system accuracy.
          Follow the 5-step process to identify, categorize, and correct errors.
        </Typography>

        {/* Main Error Reporting Form */}
        <ErrorReportingForm
          jobId="demo-job-123"
          speakerId="demo-speaker-456"
          documentText={sampleDocumentText}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
          categories={categories}
          similarPatterns={similarPatterns}
          onSimilaritySearch={handleSimilaritySearch}
          errors={validationErrors}
        />

        {/* Loading Backdrop */}
        <Backdrop
          sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
          open={isSubmitting}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <CircularProgress color="inherit" size={48} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              Submitting Error Report...
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Please wait while we process your submission
            </Typography>
          </Box>
        </Backdrop>

        {/* Success Message */}
        <Snackbar
          open={!!successMessage}
          autoHideDuration={6000}
          onClose={handleCloseSuccess}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseSuccess} severity="success" sx={{ width: '100%' }}>
            {successMessage}
          </Alert>
        </Snackbar>

        {/* Error Message */}
        <Snackbar
          open={!!errorMessage}
          autoHideDuration={8000}
          onClose={handleCloseError}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
            {errorMessage}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
};

export default ErrorReportingPage;

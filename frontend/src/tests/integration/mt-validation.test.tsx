/**
 * Integration tests for MT validation workflow
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { configureStore } from '@reduxjs/toolkit';

import theme from '@/shared/theme/theme';
import mtValidationReducer from '@/features/mt-validation/mt-validation-slice';
import uiReducer from '@/shared/slices/ui-slice';
import { MTValidationPage } from '@/features/mt-validation';
import { 
  ValidationSession, 
  ValidationTestData, 
  SessionStatus, 
  ImprovementAssessment 
} from '@/domain/types/mt-validation';

// Mock validation session data
const mockValidationSession: ValidationSession = {
  session_id: 'session-1',
  speaker_id: 'speaker-1',
  session_name: 'Test Validation Session',
  test_data_ids: ['data-1', 'data-2', 'data-3'],
  mt_user_id: 'user-1',
  status: SessionStatus.ACTIVE,
  progress_percentage: 33.33,
  current_item_index: 1,
  total_items: 3,
  created_at: '2024-01-01T10:00:00Z',
  updated_at: '2024-01-01T10:30:00Z',
  session_metadata: {
    priority: 'medium',
    auto_advance: true,
    include_ser_metrics: true
  }
};

const mockValidationData: ValidationTestData[] = [
  {
    data_id: 'data-1',
    speaker_id: 'speaker-1',
    historical_data_id: 'hist-1',
    original_asr_text: 'The patient has diabetis and high blod pressure.',
    rag_corrected_text: 'The patient has diabetes and high blood pressure.',
    final_reference_text: 'The patient has diabetes and high blood pressure.',
    original_ser_metrics: {
      ser_score: 18.5,
      edit_distance: 8,
      insertions: 2,
      deletions: 1,
      substitutions: 3,
      moves: 2,
      quality_level: 'medium',
      is_acceptable_quality: false
    },
    corrected_ser_metrics: {
      ser_score: 2.1,
      edit_distance: 1,
      insertions: 0,
      deletions: 0,
      substitutions: 1,
      moves: 0,
      quality_level: 'high',
      is_acceptable_quality: true
    },
    improvement_metrics: {
      improvement: 16.4,
      improvement_percentage: 88.6,
      is_significant_improvement: true
    },
    priority: 'medium',
    is_used: false,
    created_at: '2024-01-01T09:00:00Z'
  },
  {
    data_id: 'data-2',
    speaker_id: 'speaker-1',
    historical_data_id: 'hist-2',
    original_asr_text: 'Patient complains of chest pain radiating to left arm.',
    rag_corrected_text: 'Patient complains of chest pain radiating to left arm.',
    final_reference_text: 'Patient complains of chest pain radiating to left arm.',
    original_ser_metrics: {
      ser_score: 5.2,
      edit_distance: 2,
      insertions: 1,
      deletions: 0,
      substitutions: 1,
      moves: 0,
      quality_level: 'high',
      is_acceptable_quality: true
    },
    corrected_ser_metrics: {
      ser_score: 5.2,
      edit_distance: 2,
      insertions: 1,
      deletions: 0,
      substitutions: 1,
      moves: 0,
      quality_level: 'high',
      is_acceptable_quality: true
    },
    improvement_metrics: {
      improvement: 0.0,
      improvement_percentage: 0.0,
      is_significant_improvement: false
    },
    priority: 'low',
    is_used: false,
    created_at: '2024-01-01T09:15:00Z'
  }
];

// Mock API
jest.mock('@/infrastructure/api/mt-validation-api', () => ({
  mtValidationApi: {
    getValidationSession: jest.fn(() => Promise.resolve(mockValidationSession)),
    getValidationTestData: jest.fn(() => Promise.resolve({
      items: mockValidationData,
      current_index: 0,
      total_items: mockValidationData.length
    })),
    submitMTFeedback: jest.fn(() => Promise.resolve({
      feedback_id: 'feedback-1',
      session_id: 'session-1',
      mt_feedback_rating: 5,
      improvement_assessment: ImprovementAssessment.SIGNIFICANT,
      created_at: new Date().toISOString()
    })),
    startValidationSession: jest.fn(() => Promise.resolve(mockValidationSession)),
    completeValidationSession: jest.fn(() => Promise.resolve({
      ...mockValidationSession,
      status: SessionStatus.COMPLETED,
      progress_percentage: 100
    })),
    getValidationSessions: jest.fn(() => Promise.resolve({
      sessions: [mockValidationSession],
      total: 1
    })),
  }
}));

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const store = configureStore({
    reducer: {
      mtValidation: mtValidationReducer,
      ui: uiReducer,
    },
  });

  return (
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          {children}
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
};

describe('MT Validation Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should load validation session and display first item', async () => {
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Verify validation interface is displayed
    expect(screen.getByText(/original asr text/i)).toBeInTheDocument();
    expect(screen.getByText(/rag corrected text/i)).toBeInTheDocument();
    expect(screen.getByText(/final reference text/i)).toBeInTheDocument();

    // Verify first item content
    expect(screen.getByText(/diabetis and high blod pressure/i)).toBeInTheDocument();
    expect(screen.getByText(/diabetes and high blood pressure/i)).toBeInTheDocument();
  });

  test('should display text differences highlighting', async () => {
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Toggle differences highlighting
    const differencesToggle = screen.getByRole('button', { name: /toggle differences/i });
    await userEvent.click(differencesToggle);

    // Verify differences are highlighted
    await waitFor(() => {
      expect(screen.getByTestId('text-differences')).toBeInTheDocument();
    });

    // Verify specific differences are marked
    expect(screen.getByText('diabetis')).toHaveClass('text-deletion');
    expect(screen.getByText('diabetes')).toHaveClass('text-insertion');
  });

  test('should display SER metrics panel', async () => {
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Verify SER metrics are displayed
    expect(screen.getByText(/ser metrics/i)).toBeInTheDocument();
    expect(screen.getByText('18.5')).toBeInTheDocument(); // Original SER score
    expect(screen.getByText('2.1')).toBeInTheDocument(); // Corrected SER score
    expect(screen.getByText('88.6%')).toBeInTheDocument(); // Improvement percentage
  });

  test('should submit feedback and advance to next item', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Rate the validation item
    const ratingStars = screen.getAllByRole('radio');
    await user.click(ratingStars[4]); // 5-star rating

    // Select improvement assessment
    const significantRadio = screen.getByRole('radio', { name: /significant/i });
    await user.click(significantRadio);

    // Add comments
    const commentsInput = screen.getByLabelText(/comments/i);
    await user.type(commentsInput, 'Excellent correction of medical terminology');

    // Submit feedback
    const submitButton = screen.getByRole('button', { name: /submit feedback/i });
    await user.click(submitButton);

    // Verify feedback was submitted and advanced to next item
    await waitFor(() => {
      expect(screen.getByText(/feedback submitted/i)).toBeInTheDocument();
    });

    // Verify progress updated
    expect(screen.getByText(/item 2 of 3/i)).toBeInTheDocument();
  });

  test('should navigate between validation items', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Navigate to next item
    const nextButton = screen.getByRole('button', { name: /next item/i });
    await user.click(nextButton);

    // Verify navigation to second item
    await waitFor(() => {
      expect(screen.getByText(/chest pain radiating/i)).toBeInTheDocument();
    });

    // Navigate back to previous item
    const prevButton = screen.getByRole('button', { name: /previous item/i });
    await user.click(prevButton);

    // Verify navigation back to first item
    await waitFor(() => {
      expect(screen.getByText(/diabetis and high blod pressure/i)).toBeInTheDocument();
    });
  });

  test('should use keyboard shortcuts for navigation', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Use keyboard shortcut to navigate next
    await user.keyboard('{ArrowRight}');

    // Verify navigation to next item
    await waitFor(() => {
      expect(screen.getByText(/chest pain radiating/i)).toBeInTheDocument();
    });

    // Use keyboard shortcut to navigate back
    await user.keyboard('{ArrowLeft}');

    // Verify navigation back to first item
    await waitFor(() => {
      expect(screen.getByText(/diabetis and high blod pressure/i)).toBeInTheDocument();
    });

    // Use keyboard shortcut for rating
    await user.keyboard('5');

    // Verify 5-star rating is selected
    const fiveStarRadio = screen.getByRole('radio', { name: /5 stars/i });
    expect(fiveStarRadio).toBeChecked();
  });

  test('should display keyboard shortcuts helper', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Open keyboard shortcuts helper
    await user.keyboard('?');

    // Verify shortcuts dialog is displayed
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/keyboard shortcuts/i)).toBeInTheDocument();
    });

    // Verify shortcuts are listed
    expect(screen.getByText(/arrow keys/i)).toBeInTheDocument();
    expect(screen.getByText(/1-5/i)).toBeInTheDocument();
    expect(screen.getByText(/ctrl\+enter/i)).toBeInTheDocument();
  });

  test('should handle session completion', async () => {
    const user = userEvent.setup();
    
    // Mock session with all items completed
    const completedSession = {
      ...mockValidationSession,
      progress_percentage: 100,
      current_item_index: 2
    };

    const mtValidationApi = require('@/infrastructure/api/mt-validation-api').mtValidationApi;
    mtValidationApi.getValidationSession.mockResolvedValueOnce(completedSession);
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Complete the session
    const completeButton = screen.getByRole('button', { name: /complete session/i });
    await user.click(completeButton);

    // Verify completion dialog
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/session completed/i)).toBeInTheDocument();
    });

    // Add completion notes
    const notesInput = screen.getByLabelText(/completion notes/i);
    await user.type(notesInput, 'Session completed successfully with high quality feedback');

    // Confirm completion
    const confirmButton = screen.getByRole('button', { name: /confirm completion/i });
    await user.click(confirmButton);

    // Verify session completion
    await waitFor(() => {
      expect(screen.getByText(/session completed successfully/i)).toBeInTheDocument();
    });
  });

  test('should display session summary', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Open session summary
    const summaryButton = screen.getByRole('button', { name: /session summary/i });
    await user.click(summaryButton);

    // Verify summary dialog
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/session summary/i)).toBeInTheDocument();
    });

    // Verify summary statistics
    expect(screen.getByText(/total items/i)).toBeInTheDocument();
    expect(screen.getByText(/average rating/i)).toBeInTheDocument();
    expect(screen.getByText(/improvement distribution/i)).toBeInTheDocument();
  });

  test('should handle auto-advance setting', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Disable auto-advance
    const autoAdvanceToggle = screen.getByRole('switch', { name: /auto advance/i });
    await user.click(autoAdvanceToggle);

    // Submit feedback
    const ratingStars = screen.getAllByRole('radio');
    await user.click(ratingStars[3]); // 4-star rating

    const submitButton = screen.getByRole('button', { name: /submit feedback/i });
    await user.click(submitButton);

    // Verify feedback submitted but didn't auto-advance
    await waitFor(() => {
      expect(screen.getByText(/feedback submitted/i)).toBeInTheDocument();
    });

    // Should still be on the same item
    expect(screen.getByText(/diabetis and high blod pressure/i)).toBeInTheDocument();
  });

  test('should handle validation errors gracefully', async () => {
    const user = userEvent.setup();
    
    // Mock API error
    const mtValidationApi = require('@/infrastructure/api/mt-validation-api').mtValidationApi;
    mtValidationApi.submitMTFeedback.mockRejectedValueOnce(new Error('Network error'));
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Try to submit feedback
    const ratingStars = screen.getAllByRole('radio');
    await user.click(ratingStars[4]); // 5-star rating

    const submitButton = screen.getByRole('button', { name: /submit feedback/i });
    await user.click(submitButton);

    // Verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/failed to submit feedback/i)).toBeInTheDocument();
    });

    // Verify retry option is available
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  test('should save feedback as draft', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <MTValidationPage />
      </TestWrapper>
    );

    // Wait for session to load
    await waitFor(() => {
      expect(screen.getByText('Test Validation Session')).toBeInTheDocument();
    });

    // Fill in partial feedback
    const ratingStars = screen.getAllByRole('radio');
    await user.click(ratingStars[3]); // 4-star rating

    const commentsInput = screen.getByLabelText(/comments/i);
    await user.type(commentsInput, 'Work in progress feedback');

    // Save as draft
    const saveButton = screen.getByRole('button', { name: /save draft/i });
    await user.click(saveButton);

    // Verify draft saved
    await waitFor(() => {
      expect(screen.getByText(/draft saved/i)).toBeInTheDocument();
    });

    // Navigate away and back
    const nextButton = screen.getByRole('button', { name: /next item/i });
    await user.click(nextButton);

    const prevButton = screen.getByRole('button', { name: /previous item/i });
    await user.click(prevButton);

    // Verify draft is restored
    await waitFor(() => {
      const fourStarRadio = screen.getByRole('radio', { name: /4 stars/i });
      expect(fourStarRadio).toBeChecked();
      expect(commentsInput).toHaveValue('Work in progress feedback');
    });
  });
});

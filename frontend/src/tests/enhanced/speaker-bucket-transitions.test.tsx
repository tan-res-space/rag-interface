/**
 * Enhanced tests for speaker bucket transitions and CRUD operations
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { configureStore } from '@reduxjs/toolkit';

import theme from '@/shared/theme/theme';
import speakerReducer from '@/features/speaker-management/speaker-slice';
import uiReducer from '@/shared/slices/ui-slice';
import { SpeakerManagementPage } from '@/features/speaker-management';
import { Speaker, SpeakerBucket, QualityTrend } from '@/domain/types/speaker';

// Mock speakers with different bucket scenarios
const mockSpeakersForTransition: Speaker[] = [
  {
    speaker_id: '1',
    speaker_identifier: 'SPEAKER_TRANSITION_1',
    speaker_name: 'Dr. Ready For Transition',
    current_bucket: SpeakerBucket.HIGH_TOUCH,
    note_count: 200,
    average_ser_score: 5.2, // Low score, should transition to LOW_TOUCH
    quality_trend: QualityTrend.IMPROVING,
    should_transition: true,
    has_sufficient_data: true,
    created_at: '2024-01-01',
    updated_at: '2024-01-15',
  },
  {
    speaker_id: '2',
    speaker_identifier: 'SPEAKER_STABLE',
    speaker_name: 'Dr. Stable Speaker',
    current_bucket: SpeakerBucket.MEDIUM_TOUCH,
    note_count: 150,
    average_ser_score: 12.5,
    quality_trend: QualityTrend.STABLE,
    should_transition: false,
    has_sufficient_data: true,
    created_at: '2024-01-01',
    updated_at: '2024-01-10',
  },
  {
    speaker_id: '3',
    speaker_identifier: 'SPEAKER_INSUFFICIENT_DATA',
    speaker_name: 'Dr. New Speaker',
    current_bucket: SpeakerBucket.MEDIUM_TOUCH,
    note_count: 15, // Insufficient data
    average_ser_score: 0,
    quality_trend: QualityTrend.STABLE,
    should_transition: false,
    has_sufficient_data: false,
    created_at: '2024-01-20',
    updated_at: '2024-01-20',
  },
];

// Mock API with enhanced functionality
jest.mock('@/infrastructure/api/speaker-api', () => ({
  speakerApi: {
    getSpeakers: jest.fn(() => Promise.resolve({ 
      speakers: mockSpeakersForTransition, 
      total: 3,
      page: 1,
      per_page: 10,
      total_pages: 1
    })),
    getSpeaker: jest.fn((id: string) => 
      Promise.resolve(mockSpeakersForTransition.find(s => s.speaker_id === id))
    ),
    createSpeaker: jest.fn((data) => 
      Promise.resolve({ 
        ...data, 
        speaker_id: '4', 
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        note_count: 0,
        average_ser_score: 0,
        quality_trend: QualityTrend.STABLE,
        should_transition: false,
        has_sufficient_data: false
      })
    ),
    updateSpeaker: jest.fn((id: string, data) => 
      Promise.resolve({ 
        ...mockSpeakersForTransition.find(s => s.speaker_id === id), 
        ...data,
        updated_at: new Date().toISOString()
      })
    ),
    deleteSpeaker: jest.fn(() => Promise.resolve()),
    transitionSpeaker: jest.fn((id: string, newBucket: SpeakerBucket) => 
      Promise.resolve({
        ...mockSpeakersForTransition.find(s => s.speaker_id === id),
        current_bucket: newBucket,
        should_transition: false,
        updated_at: new Date().toISOString()
      })
    ),
    bulkTransition: jest.fn((speakerIds: string[], newBucket: SpeakerBucket) => 
      Promise.resolve({
        success: true,
        updated_count: speakerIds.length,
        failed_count: 0
      })
    ),
    searchSpeakers: jest.fn((query: string) => 
      Promise.resolve({
        speakers: mockSpeakersForTransition.filter(s => 
          s.speaker_name.toLowerCase().includes(query.toLowerCase()) ||
          s.speaker_identifier.toLowerCase().includes(query.toLowerCase())
        ),
        total: 1
      })
    ),
    getSpeakerAnalytics: jest.fn(() => Promise.resolve({
      performance_metrics: { 
        average_ser_score: 8.9, 
        total_notes: 365,
        speakers_needing_transition: 1
      },
      quality_trends: { improving: 1, stable: 2, declining: 0 },
      bucket_distribution: { 
        [SpeakerBucket.HIGH_TOUCH]: 1, 
        [SpeakerBucket.MEDIUM_TOUCH]: 2, 
        [SpeakerBucket.LOW_TOUCH]: 0 
      }
    })),
  }
}));

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const store = configureStore({
    reducer: {
      speakers: speakerReducer,
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

describe('Speaker Bucket Transitions - Enhanced Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Bucket Transition Detection', () => {
    test('should identify speakers needing transition', async () => {
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dr. Ready For Transition')).toBeInTheDocument();
      });

      // Check for transition indicator
      const transitionIndicator = screen.getByTestId('transition-indicator-1');
      expect(transitionIndicator).toBeInTheDocument();
      expect(transitionIndicator).toHaveAttribute('aria-label', 'Speaker needs bucket transition');
    });

    test('should not show transition indicator for stable speakers', async () => {
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dr. Stable Speaker')).toBeInTheDocument();
      });

      // Should not have transition indicator
      expect(screen.queryByTestId('transition-indicator-2')).not.toBeInTheDocument();
    });

    test('should handle insufficient data scenarios', async () => {
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dr. New Speaker')).toBeInTheDocument();
      });

      // Check for insufficient data indicator
      const insufficientDataIndicator = screen.getByTestId('insufficient-data-indicator-3');
      expect(insufficientDataIndicator).toBeInTheDocument();
      expect(insufficientDataIndicator).toHaveAttribute('aria-label', 'Insufficient data for analysis');
    });
  });

  describe('Manual Bucket Transitions', () => {
    test('should allow manual bucket transition', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dr. Ready For Transition')).toBeInTheDocument();
      });

      // Open speaker actions menu
      const speakerCard = screen.getByTestId('speaker-card-1');
      const actionsButton = within(speakerCard).getByLabelText(/more actions/i);
      await user.click(actionsButton);

      // Click transition option
      const transitionOption = screen.getByRole('menuitem', { name: /transition bucket/i });
      await user.click(transitionOption);

      // Verify transition dialog opens
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
        expect(screen.getByText('Transition Speaker Bucket')).toBeInTheDocument();
      });

      // Select new bucket
      const bucketSelect = screen.getByLabelText(/new bucket/i);
      await user.click(bucketSelect);
      
      const lowTouchOption = screen.getByRole('option', { name: /low touch/i });
      await user.click(lowTouchOption);

      // Add transition reason
      const reasonInput = screen.getByLabelText(/transition reason/i);
      await user.type(reasonInput, 'Low SER score indicates speaker improvement');

      // Confirm transition
      const confirmButton = screen.getByRole('button', { name: /confirm transition/i });
      await user.click(confirmButton);

      // Verify success message
      await waitFor(() => {
        expect(screen.getByText(/speaker bucket updated successfully/i)).toBeInTheDocument();
      });
    });

    test('should validate transition rules', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dr. New Speaker')).toBeInTheDocument();
      });

      // Try to transition speaker with insufficient data
      const speakerCard = screen.getByTestId('speaker-card-3');
      const actionsButton = within(speakerCard).getByLabelText(/more actions/i);
      await user.click(actionsButton);

      const transitionOption = screen.getByRole('menuitem', { name: /transition bucket/i });
      await user.click(transitionOption);

      // Should show warning about insufficient data
      await waitFor(() => {
        expect(screen.getByText(/insufficient data for reliable transition/i)).toBeInTheDocument();
      });

      // Transition should be disabled or require confirmation
      const confirmButton = screen.getByRole('button', { name: /confirm transition/i });
      expect(confirmButton).toBeDisabled();
    });
  });

  describe('Bulk Operations', () => {
    test('should support bulk bucket transitions', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dr. Ready For Transition')).toBeInTheDocument();
      });

      // Select multiple speakers
      const selectAllCheckbox = screen.getByRole('checkbox', { name: /select all/i });
      await user.click(selectAllCheckbox);

      // Open bulk actions
      const bulkActionsButton = screen.getByRole('button', { name: /bulk actions/i });
      await user.click(bulkActionsButton);

      // Select bulk transition
      const bulkTransitionOption = screen.getByRole('menuitem', { name: /bulk transition/i });
      await user.click(bulkTransitionOption);

      // Verify bulk transition dialog
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
        expect(screen.getByText('Bulk Bucket Transition')).toBeInTheDocument();
        expect(screen.getByText(/3 speakers selected/i)).toBeInTheDocument();
      });

      // Select target bucket
      const bucketSelect = screen.getByLabelText(/target bucket/i);
      await user.click(bucketSelect);
      
      const mediumTouchOption = screen.getByRole('option', { name: /medium touch/i });
      await user.click(mediumTouchOption);

      // Confirm bulk transition
      const confirmButton = screen.getByRole('button', { name: /apply to all/i });
      await user.click(confirmButton);

      // Verify success message
      await waitFor(() => {
        expect(screen.getByText(/bulk transition completed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle transition API errors', async () => {
      const user = userEvent.setup();
      
      // Mock API error
      const speakerApi = require('@/infrastructure/api/speaker-api').speakerApi;
      speakerApi.transitionSpeaker.mockRejectedValueOnce(new Error('Transition failed'));
      
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dr. Ready For Transition')).toBeInTheDocument();
      });

      // Attempt transition
      const speakerCard = screen.getByTestId('speaker-card-1');
      const actionsButton = within(speakerCard).getByLabelText(/more actions/i);
      await user.click(actionsButton);

      const transitionOption = screen.getByRole('menuitem', { name: /transition bucket/i });
      await user.click(transitionOption);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const bucketSelect = screen.getByLabelText(/new bucket/i);
      await user.click(bucketSelect);
      
      const lowTouchOption = screen.getByRole('option', { name: /low touch/i });
      await user.click(lowTouchOption);

      const confirmButton = screen.getByRole('button', { name: /confirm transition/i });
      await user.click(confirmButton);

      // Verify error message
      await waitFor(() => {
        expect(screen.getByText(/failed to transition speaker/i)).toBeInTheDocument();
      });
    });

    test('should handle network errors gracefully', async () => {
      // Mock network error
      const speakerApi = require('@/infrastructure/api/speaker-api').speakerApi;
      speakerApi.getSpeakers.mockRejectedValueOnce(new Error('Network error'));
      
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      // Verify error state
      await waitFor(() => {
        expect(screen.getByText(/failed to load speakers/i)).toBeInTheDocument();
      });

      // Verify retry functionality
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();
      
      // Reset mock for retry
      speakerApi.getSpeakers.mockResolvedValueOnce({ 
        speakers: mockSpeakersForTransition, 
        total: 3 
      });
      
      await userEvent.setup().click(retryButton);
      
      // Verify successful retry
      await waitFor(() => {
        expect(screen.getByText('Dr. Ready For Transition')).toBeInTheDocument();
      });
    });
  });

  describe('Analytics Integration', () => {
    test('should display transition analytics', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SpeakerManagementPage />
        </TestWrapper>
      );

      // Navigate to analytics tab
      const analyticsTab = screen.getByRole('tab', { name: /analytics/i });
      await user.click(analyticsTab);

      // Verify analytics data
      await waitFor(() => {
        expect(screen.getByText(/speakers needing transition/i)).toBeInTheDocument();
        expect(screen.getByText('1')).toBeInTheDocument(); // From mock data
      });

      // Verify bucket distribution
      expect(screen.getByText(/bucket distribution/i)).toBeInTheDocument();
      expect(screen.getByText(/high touch: 1/i)).toBeInTheDocument();
      expect(screen.getByText(/medium touch: 2/i)).toBeInTheDocument();
    });
  });
});

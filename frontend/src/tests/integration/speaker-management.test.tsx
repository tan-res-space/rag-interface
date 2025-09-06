/**
 * Integration tests for speaker management workflow
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

// Mock API responses
const mockSpeakers: Speaker[] = [
  {
    speaker_id: '1',
    speaker_identifier: 'SPEAKER_001',
    speaker_name: 'Dr. John Smith',
    current_bucket: SpeakerBucket.HIGH_TOUCH,
    note_count: 150,
    average_ser_score: 18.5,
    quality_trend: QualityTrend.IMPROVING,
    should_transition: true,
    has_sufficient_data: true,
    created_at: '2024-01-01',
    updated_at: '2024-01-15',
  },
  {
    speaker_id: '2',
    speaker_identifier: 'SPEAKER_002',
    speaker_name: 'Dr. Sarah Johnson',
    current_bucket: SpeakerBucket.MEDIUM_TOUCH,
    note_count: 89,
    average_ser_score: 12.3,
    quality_trend: QualityTrend.STABLE,
    should_transition: false,
    has_sufficient_data: true,
    created_at: '2024-01-01',
    updated_at: '2024-01-10',
  },
];

// Mock API
jest.mock('@/infrastructure/api/speaker-api', () => ({
  speakerApi: {
    getSpeakers: jest.fn(() => Promise.resolve({ speakers: mockSpeakers, total: 2 })),
    getSpeaker: jest.fn((id: string) => 
      Promise.resolve(mockSpeakers.find(s => s.speaker_id === id))
    ),
    createSpeaker: jest.fn((data) => 
      Promise.resolve({ ...data, speaker_id: '3', created_at: new Date().toISOString() })
    ),
    updateSpeaker: jest.fn((id: string, data) => 
      Promise.resolve({ ...mockSpeakers.find(s => s.speaker_id === id), ...data })
    ),
    deleteSpeaker: jest.fn(() => Promise.resolve()),
    searchSpeakers: jest.fn((query: string) => 
      Promise.resolve({
        speakers: mockSpeakers.filter(s => 
          s.speaker_name.toLowerCase().includes(query.toLowerCase())
        ),
        total: 1
      })
    ),
    getSpeakerAnalytics: jest.fn(() => Promise.resolve({
      performance_metrics: { average_ser_score: 15.4, total_notes: 239 },
      quality_trends: { improving: 1, stable: 1, declining: 0 },
      ser_distribution: { high: 0, medium: 2, low: 0 }
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

describe('Speaker Management Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should load and display speakers list', async () => {
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for speakers to load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
      expect(screen.getByText('Dr. Sarah Johnson')).toBeInTheDocument();
    });

    // Verify speaker details are displayed
    expect(screen.getByText('SPEAKER_001')).toBeInTheDocument();
    expect(screen.getByText('SPEAKER_002')).toBeInTheDocument();
    expect(screen.getByText('HIGH TOUCH')).toBeInTheDocument();
    expect(screen.getByText('MEDIUM TOUCH')).toBeInTheDocument();
  });

  test('should filter speakers by bucket', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    });

    // Open filter menu
    const filterButton = screen.getByLabelText(/filter speakers/i);
    await user.click(filterButton);

    // Select HIGH_TOUCH filter
    const highTouchFilter = screen.getByRole('checkbox', { name: /high touch/i });
    await user.click(highTouchFilter);

    // Apply filters
    const applyButton = screen.getByRole('button', { name: /apply filters/i });
    await user.click(applyButton);

    // Verify only HIGH_TOUCH speakers are shown
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
      expect(screen.queryByText('Dr. Sarah Johnson')).not.toBeInTheDocument();
    });
  });

  test('should search speakers by name', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    });

    // Enter search query
    const searchInput = screen.getByPlaceholderText(/search speakers/i);
    await user.type(searchInput, 'John');

    // Wait for search results
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
      expect(screen.queryByText('Dr. Sarah Johnson')).not.toBeInTheDocument();
    });
  });

  test('should open speaker details dialog', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for speakers to load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    });

    // Click on speaker card
    const speakerCard = screen.getByText('Dr. John Smith').closest('[data-testid="speaker-card"]');
    expect(speakerCard).toBeInTheDocument();
    await user.click(speakerCard!);

    // Verify details dialog opens
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Speaker Details')).toBeInTheDocument();
      expect(screen.getByText('SPEAKER_001')).toBeInTheDocument();
    });
  });

  test('should create new speaker', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Click add speaker button
    const addButton = screen.getByRole('button', { name: /add speaker/i });
    await user.click(addButton);

    // Verify create dialog opens
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Add New Speaker')).toBeInTheDocument();
    });

    // Fill in speaker details
    const nameInput = screen.getByLabelText(/speaker name/i);
    const identifierInput = screen.getByLabelText(/speaker identifier/i);
    
    await user.type(nameInput, 'Dr. Test Speaker');
    await user.type(identifierInput, 'SPEAKER_TEST');

    // Select bucket
    const bucketSelect = screen.getByLabelText(/current bucket/i);
    await user.click(bucketSelect);
    
    const mediumTouchOption = screen.getByRole('option', { name: /medium touch/i });
    await user.click(mediumTouchOption);

    // Submit form
    const submitButton = screen.getByRole('button', { name: /create speaker/i });
    await user.click(submitButton);

    // Verify success message
    await waitFor(() => {
      expect(screen.getByText(/speaker created successfully/i)).toBeInTheDocument();
    });
  });

  test('should handle speaker editing', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for speakers to load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    });

    // Open speaker menu
    const speakerCard = screen.getByText('Dr. John Smith').closest('[data-testid="speaker-card"]');
    const menuButton = within(speakerCard!).getByLabelText(/more actions/i);
    await user.click(menuButton);

    // Click edit option
    const editOption = screen.getByRole('menuitem', { name: /edit/i });
    await user.click(editOption);

    // Verify edit dialog opens
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Edit Speaker')).toBeInTheDocument();
    });

    // Update speaker name
    const nameInput = screen.getByDisplayValue('Dr. John Smith');
    await user.clear(nameInput);
    await user.type(nameInput, 'Dr. John Smith Updated');

    // Save changes
    const saveButton = screen.getByRole('button', { name: /save changes/i });
    await user.click(saveButton);

    // Verify success message
    await waitFor(() => {
      expect(screen.getByText(/speaker updated successfully/i)).toBeInTheDocument();
    });
  });

  test('should display speaker analytics', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for speakers to load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    });

    // Click analytics tab
    const analyticsTab = screen.getByRole('tab', { name: /analytics/i });
    await user.click(analyticsTab);

    // Verify analytics content loads
    await waitFor(() => {
      expect(screen.getByText(/speaker analytics/i)).toBeInTheDocument();
      expect(screen.getByText(/average ser score/i)).toBeInTheDocument();
      expect(screen.getByText('15.4')).toBeInTheDocument(); // Mock analytics data
    });
  });

  test('should handle bulk operations', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for speakers to load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    });

    // Select multiple speakers
    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[1]); // First speaker
    await user.click(checkboxes[2]); // Second speaker

    // Verify bulk actions appear
    await waitFor(() => {
      expect(screen.getByText(/2 speakers selected/i)).toBeInTheDocument();
    });

    // Open bulk actions menu
    const bulkActionsButton = screen.getByRole('button', { name: /bulk actions/i });
    await user.click(bulkActionsButton);

    // Select bulk update option
    const bulkUpdateOption = screen.getByRole('menuitem', { name: /bulk update/i });
    await user.click(bulkUpdateOption);

    // Verify bulk update dialog opens
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Bulk Update Speakers')).toBeInTheDocument();
    });
  });

  test('should handle error states gracefully', async () => {
    // Mock API error
    const speakerApi = require('@/infrastructure/api/speaker-api').speakerApi;
    speakerApi.getSpeakers.mockRejectedValueOnce(new Error('Network error'));
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/failed to load speakers/i)).toBeInTheDocument();
    });

    // Verify retry button is available
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  test('should handle loading states', async () => {
    // Mock delayed API response
    const speakerApi = require('@/infrastructure/api/speaker-api').speakerApi;
    speakerApi.getSpeakers.mockImplementationOnce(
      () => new Promise(resolve => setTimeout(() => resolve({ speakers: mockSpeakers, total: 2 }), 1000))
    );
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Verify loading state is displayed
    expect(screen.getByTestId('speakers-loading')).toBeInTheDocument();

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    }, { timeout: 2000 });

    // Verify loading state is removed
    expect(screen.queryByTestId('speakers-loading')).not.toBeInTheDocument();
  });

  test('should handle pagination', async () => {
    const user = userEvent.setup();
    
    // Mock paginated response
    const speakerApi = require('@/infrastructure/api/speaker-api').speakerApi;
    speakerApi.getSpeakers.mockResolvedValueOnce({
      speakers: mockSpeakers,
      total: 25,
      page: 1,
      per_page: 10,
      total_pages: 3
    });
    
    render(
      <TestWrapper>
        <SpeakerManagementPage />
      </TestWrapper>
    );

    // Wait for speakers to load
    await waitFor(() => {
      expect(screen.getByText('Dr. John Smith')).toBeInTheDocument();
    });

    // Verify pagination controls
    expect(screen.getByText(/page 1 of 3/i)).toBeInTheDocument();
    
    // Test next page
    const nextButton = screen.getByRole('button', { name: /next page/i });
    expect(nextButton).toBeInTheDocument();
    
    // Mock next page response
    speakerApi.getSpeakers.mockResolvedValueOnce({
      speakers: [],
      total: 25,
      page: 2,
      per_page: 10,
      total_pages: 3
    });
    
    await user.click(nextButton);
    
    // Verify page change
    await waitFor(() => {
      expect(screen.getByText(/page 2 of 3/i)).toBeInTheDocument();
    });
  });
});

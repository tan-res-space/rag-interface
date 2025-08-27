/**
 * Redux slice for MT validation state management
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { mtValidationApi } from '@/infrastructure/api/mt-validation-api';
import {
  ValidationSession,
  ValidationTestData,
  ValidationItem,
  MTFeedback,
  StartValidationSessionRequest,
  SubmitMTFeedbackRequest,
  CompleteValidationSessionRequest,
  ValidationWorkflowState,
  MTValidationFilters,
  ValidationSessionSummary,
  MTUserStatistics,
  SessionStatus,
  ValidationItemStatus,
  ImprovementAssessment,
  DifferenceHighlightOptions,
  ValidationPreferences,
  TextDifference
} from '@/domain/types/mt-validation';

// Async thunks
export const startValidationSession = createAsyncThunk(
  'mtValidation/startValidationSession',
  async (request: StartValidationSessionRequest) => {
    return await mtValidationApi.startValidationSession(request);
  }
);

export const getValidationSession = createAsyncThunk(
  'mtValidation/getValidationSession',
  async (sessionId: string) => {
    return await mtValidationApi.getValidationSession(sessionId);
  }
);

export const getValidationTestData = createAsyncThunk(
  'mtValidation/getValidationTestData',
  async ({ sessionId, limit }: { sessionId: string; limit?: number }) => {
    return await mtValidationApi.getValidationTestData(sessionId, limit);
  }
);

export const submitMTFeedback = createAsyncThunk(
  'mtValidation/submitMTFeedback',
  async ({ sessionId, feedback }: { sessionId: string; feedback: SubmitMTFeedbackRequest }) => {
    return await mtValidationApi.submitMTFeedback(sessionId, feedback);
  }
);

export const completeValidationSession = createAsyncThunk(
  'mtValidation/completeValidationSession',
  async ({ sessionId, request }: { sessionId: string; request: CompleteValidationSessionRequest }) => {
    return await mtValidationApi.completeValidationSession(sessionId, request);
  }
);

export const getValidationSessions = createAsyncThunk(
  'mtValidation/getValidationSessions',
  async (filters: MTValidationFilters) => {
    return await mtValidationApi.getValidationSessions(filters);
  }
);

export const getSessionSummary = createAsyncThunk(
  'mtValidation/getSessionSummary',
  async (sessionId: string) => {
    return await mtValidationApi.getValidationSessionSummary(sessionId);
  }
);

export const getMTUserStatistics = createAsyncThunk(
  'mtValidation/getMTUserStatistics',
  async (mtUserId: string) => {
    return await mtValidationApi.getMTUserStatistics(mtUserId);
  }
);

export const calculateTextDifferences = createAsyncThunk(
  'mtValidation/calculateTextDifferences',
  async ({ originalText, correctedText }: { originalText: string; correctedText: string }) => {
    return await mtValidationApi.calculateTextDifferences(originalText, correctedText);
  }
);

// State interface
interface MTValidationState {
  // Current session and workflow
  currentSession: ValidationSession | null;
  testDataItems: ValidationTestData[];
  currentItemIndex: number;
  currentItem: ValidationTestData | null;
  sessionProgress: number;
  
  // Feedback and validation
  currentFeedback: Partial<SubmitMTFeedbackRequest>;
  submittedFeedback: MTFeedback[];
  
  // UI state
  workflowState: ValidationWorkflowState;
  comparisonMode: 'side-by-side' | 'unified' | 'overlay';
  showDifferences: boolean;
  showSERMetrics: boolean;
  highlightOptions: DifferenceHighlightOptions;
  
  // Text differences
  textDifferences: TextDifference[];
  
  // Sessions management
  sessions: ValidationSession[];
  sessionSummary: ValidationSessionSummary | null;
  
  // User preferences and statistics
  userPreferences: ValidationPreferences;
  userStatistics: MTUserStatistics | null;
  
  // Filters and search
  sessionFilters: MTValidationFilters;
  
  // Loading states
  loading: {
    session: boolean;
    testData: boolean;
    feedback: boolean;
    sessions: boolean;
    summary: boolean;
    differences: boolean;
    statistics: boolean;
  };
  
  // Error states
  error: {
    session: string | null;
    testData: string | null;
    feedback: string | null;
    sessions: string | null;
    summary: string | null;
    differences: string | null;
    statistics: string | null;
    general: string | null;
  };
  
  // Real-time updates
  isConnected: boolean;
  lastUpdate: string | null;
}

// Initial state
const initialState: MTValidationState = {
  currentSession: null,
  testDataItems: [],
  currentItemIndex: 0,
  currentItem: null,
  sessionProgress: 0,
  
  currentFeedback: {},
  submittedFeedback: [],
  
  workflowState: {
    currentSession: null,
    currentItem: null,
    currentItemIndex: 0,
    totalItems: 0,
    sessionProgress: 0,
    isReviewing: false,
    showDifferences: true,
    showSERMetrics: true,
    comparisonMode: 'side-by-side',
  },
  
  comparisonMode: 'side-by-side',
  showDifferences: true,
  showSERMetrics: true,
  highlightOptions: {
    showInsertions: true,
    showDeletions: true,
    showSubstitutions: true,
    showMoves: true,
    highlightIntensity: 'medium',
    colorScheme: 'default',
  },
  
  textDifferences: [],
  
  sessions: [],
  sessionSummary: null,
  
  userPreferences: {
    auto_advance: true,
    show_ser_metrics_by_default: true,
    highlight_differences_by_default: true,
    default_comparison_mode: 'side-by-side',
    keyboard_shortcuts_enabled: true,
    auto_save_feedback: true,
    review_time_tracking: true,
  },
  userStatistics: null,
  
  sessionFilters: {},
  
  loading: {
    session: false,
    testData: false,
    feedback: false,
    sessions: false,
    summary: false,
    differences: false,
    statistics: false,
  },
  
  error: {
    session: null,
    testData: null,
    feedback: null,
    sessions: null,
    summary: null,
    differences: null,
    statistics: null,
    general: null,
  },
  
  isConnected: false,
  lastUpdate: null,
};

// Slice
const mtValidationSlice = createSlice({
  name: 'mtValidation',
  initialState,
  reducers: {
    // Navigation
    setCurrentItemIndex: (state, action: PayloadAction<number>) => {
      const index = Math.max(0, Math.min(action.payload, state.testDataItems.length - 1));
      state.currentItemIndex = index;
      state.currentItem = state.testDataItems[index] || null;
      state.workflowState.currentItemIndex = index;
      state.workflowState.currentItem = state.currentItem ? {
        item_id: `item_${index}`,
        session_id: state.currentSession?.session_id || '',
        test_data: state.currentItem,
        status: ValidationItemStatus.IN_REVIEW,
        differences: state.textDifferences,
        created_at: new Date().toISOString(),
      } : null;
    },
    
    nextItem: (state) => {
      if (state.currentItemIndex < state.testDataItems.length - 1) {
        const newIndex = state.currentItemIndex + 1;
        state.currentItemIndex = newIndex;
        state.currentItem = state.testDataItems[newIndex];
        state.workflowState.currentItemIndex = newIndex;
        // Clear current feedback for new item
        state.currentFeedback = {};
      }
    },
    
    previousItem: (state) => {
      if (state.currentItemIndex > 0) {
        const newIndex = state.currentItemIndex - 1;
        state.currentItemIndex = newIndex;
        state.currentItem = state.testDataItems[newIndex];
        state.workflowState.currentItemIndex = newIndex;
        // Clear current feedback for new item
        state.currentFeedback = {};
      }
    },
    
    // Feedback management
    updateCurrentFeedback: (state, action: PayloadAction<Partial<SubmitMTFeedbackRequest>>) => {
      state.currentFeedback = { ...state.currentFeedback, ...action.payload };
    },
    
    clearCurrentFeedback: (state) => {
      state.currentFeedback = {};
    },
    
    // UI state management
    setComparisonMode: (state, action: PayloadAction<'side-by-side' | 'unified' | 'overlay'>) => {
      state.comparisonMode = action.payload;
      state.workflowState.comparisonMode = action.payload;
    },
    
    toggleDifferences: (state) => {
      state.showDifferences = !state.showDifferences;
      state.workflowState.showDifferences = state.showDifferences;
    },
    
    toggleSERMetrics: (state) => {
      state.showSERMetrics = !state.showSERMetrics;
      state.workflowState.showSERMetrics = state.showSERMetrics;
    },
    
    setHighlightOptions: (state, action: PayloadAction<Partial<DifferenceHighlightOptions>>) => {
      state.highlightOptions = { ...state.highlightOptions, ...action.payload };
    },
    
    // Session management
    setSessionFilters: (state, action: PayloadAction<MTValidationFilters>) => {
      state.sessionFilters = action.payload;
    },
    
    clearSessionFilters: (state) => {
      state.sessionFilters = {};
    },
    
    // Workflow state
    setReviewingState: (state, action: PayloadAction<boolean>) => {
      state.workflowState.isReviewing = action.payload;
    },
    
    updateSessionProgress: (state) => {
      if (state.testDataItems.length > 0) {
        const completedItems = state.submittedFeedback.length;
        const progress = (completedItems / state.testDataItems.length) * 100;
        state.sessionProgress = progress;
        state.workflowState.sessionProgress = progress;
      }
    },
    
    // User preferences
    updateUserPreferences: (state, action: PayloadAction<Partial<ValidationPreferences>>) => {
      state.userPreferences = { ...state.userPreferences, ...action.payload };
    },
    
    // Real-time updates
    setConnectionStatus: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
    
    updateLastUpdate: (state) => {
      state.lastUpdate = new Date().toISOString();
    },
    
    // Error handling
    clearErrors: (state) => {
      state.error = {
        session: null,
        testData: null,
        feedback: null,
        sessions: null,
        summary: null,
        differences: null,
        statistics: null,
        general: null,
      };
    },
    
    clearError: (state, action: PayloadAction<keyof MTValidationState['error']>) => {
      state.error[action.payload] = null;
    },
    
    // Reset state
    resetValidationState: (state) => {
      state.currentSession = null;
      state.testDataItems = [];
      state.currentItemIndex = 0;
      state.currentItem = null;
      state.sessionProgress = 0;
      state.currentFeedback = {};
      state.submittedFeedback = [];
      state.textDifferences = [];
      state.workflowState = initialState.workflowState;
    },
  },
  
  extraReducers: (builder) => {
    // Start validation session
    builder
      .addCase(startValidationSession.pending, (state) => {
        state.loading.session = true;
        state.error.session = null;
      })
      .addCase(startValidationSession.fulfilled, (state, action) => {
        state.loading.session = false;
        state.currentSession = action.payload;
        state.workflowState.currentSession = action.payload;
        state.workflowState.totalItems = action.payload.test_data_count;
      })
      .addCase(startValidationSession.rejected, (state, action) => {
        state.loading.session = false;
        state.error.session = action.error.message || 'Failed to start validation session';
      });
    
    // Get validation test data
    builder
      .addCase(getValidationTestData.pending, (state) => {
        state.loading.testData = true;
        state.error.testData = null;
      })
      .addCase(getValidationTestData.fulfilled, (state, action) => {
        state.loading.testData = false;
        state.testDataItems = action.payload;
        state.currentItem = action.payload[0] || null;
        state.currentItemIndex = 0;
        state.workflowState.totalItems = action.payload.length;
        state.workflowState.currentItem = state.currentItem ? {
          item_id: 'item_0',
          session_id: state.currentSession?.session_id || '',
          test_data: state.currentItem,
          status: ValidationItemStatus.IN_REVIEW,
          differences: [],
          created_at: new Date().toISOString(),
        } : null;
      })
      .addCase(getValidationTestData.rejected, (state, action) => {
        state.loading.testData = false;
        state.error.testData = action.error.message || 'Failed to load test data';
      });
    
    // Submit MT feedback
    builder
      .addCase(submitMTFeedback.pending, (state) => {
        state.loading.feedback = true;
        state.error.feedback = null;
      })
      .addCase(submitMTFeedback.fulfilled, (state, action) => {
        state.loading.feedback = false;
        state.submittedFeedback.push(action.payload);
        state.currentFeedback = {};
        
        // Update progress
        const completedItems = state.submittedFeedback.length;
        const progress = (completedItems / state.testDataItems.length) * 100;
        state.sessionProgress = progress;
        state.workflowState.sessionProgress = progress;
        
        // Auto-advance if enabled
        if (state.userPreferences.auto_advance && state.currentItemIndex < state.testDataItems.length - 1) {
          const newIndex = state.currentItemIndex + 1;
          state.currentItemIndex = newIndex;
          state.currentItem = state.testDataItems[newIndex];
          state.workflowState.currentItemIndex = newIndex;
        }
      })
      .addCase(submitMTFeedback.rejected, (state, action) => {
        state.loading.feedback = false;
        state.error.feedback = action.error.message || 'Failed to submit feedback';
      });
    
    // Get validation sessions
    builder
      .addCase(getValidationSessions.pending, (state) => {
        state.loading.sessions = true;
        state.error.sessions = null;
      })
      .addCase(getValidationSessions.fulfilled, (state, action) => {
        state.loading.sessions = false;
        state.sessions = action.payload;
      })
      .addCase(getValidationSessions.rejected, (state, action) => {
        state.loading.sessions = false;
        state.error.sessions = action.error.message || 'Failed to load sessions';
      });
    
    // Calculate text differences
    builder
      .addCase(calculateTextDifferences.pending, (state) => {
        state.loading.differences = true;
        state.error.differences = null;
      })
      .addCase(calculateTextDifferences.fulfilled, (state, action) => {
        state.loading.differences = false;
        state.textDifferences = action.payload;
      })
      .addCase(calculateTextDifferences.rejected, (state, action) => {
        state.loading.differences = false;
        state.error.differences = action.error.message || 'Failed to calculate differences';
      });
    
    // Get session summary
    builder
      .addCase(getSessionSummary.fulfilled, (state, action) => {
        state.sessionSummary = action.payload;
      });
    
    // Get MT user statistics
    builder
      .addCase(getMTUserStatistics.fulfilled, (state, action) => {
        state.userStatistics = action.payload;
      });
  },
});

// Export actions
export const {
  setCurrentItemIndex,
  nextItem,
  previousItem,
  updateCurrentFeedback,
  clearCurrentFeedback,
  setComparisonMode,
  toggleDifferences,
  toggleSERMetrics,
  setHighlightOptions,
  setSessionFilters,
  clearSessionFilters,
  setReviewingState,
  updateSessionProgress,
  updateUserPreferences,
  setConnectionStatus,
  updateLastUpdate,
  clearErrors,
  clearError,
  resetValidationState,
} = mtValidationSlice.actions;

// Selectors
export const selectCurrentSession = (state: { mtValidation: MTValidationState }) => state.mtValidation.currentSession;
export const selectCurrentItem = (state: { mtValidation: MTValidationState }) => state.mtValidation.currentItem;
export const selectCurrentItemIndex = (state: { mtValidation: MTValidationState }) => state.mtValidation.currentItemIndex;
export const selectTestDataItems = (state: { mtValidation: MTValidationState }) => state.mtValidation.testDataItems;
export const selectCurrentFeedback = (state: { mtValidation: MTValidationState }) => state.mtValidation.currentFeedback;
export const selectSessionProgress = (state: { mtValidation: MTValidationState }) => state.mtValidation.sessionProgress;
export const selectComparisonMode = (state: { mtValidation: MTValidationState }) => state.mtValidation.comparisonMode;
export const selectShowDifferences = (state: { mtValidation: MTValidationState }) => state.mtValidation.showDifferences;
export const selectShowSERMetrics = (state: { mtValidation: MTValidationState }) => state.mtValidation.showSERMetrics;
export const selectTextDifferences = (state: { mtValidation: MTValidationState }) => state.mtValidation.textDifferences;
export const selectValidationLoading = (state: { mtValidation: MTValidationState }) => state.mtValidation.loading;
export const selectValidationError = (state: { mtValidation: MTValidationState }) => state.mtValidation.error;
export const selectUserPreferences = (state: { mtValidation: MTValidationState }) => state.mtValidation.userPreferences;
export const selectWorkflowState = (state: { mtValidation: MTValidationState }) => state.mtValidation.workflowState;

export default mtValidationSlice.reducer;

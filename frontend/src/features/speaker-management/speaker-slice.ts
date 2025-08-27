/**
 * Redux slice for speaker management state
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { speakerApi } from '@/infrastructure/api/speaker-api';
import {
  Speaker,
  SpeakerListResponse,
  SpeakerSearchParams,
  SpeakerSearchFilters,
  SpeakerBucketStats,
  BucketTransitionRequest,
  CreateTransitionRequest,
  ComprehensiveSpeakerView,
  SpeakerBucket,
  QuickFilterOption
} from '@/domain/types/speaker';

// Async thunks
export const searchSpeakers = createAsyncThunk(
  'speakers/searchSpeakers',
  async (params: SpeakerSearchParams) => {
    return await speakerApi.searchSpeakers(params);
  }
);

export const getSpeakerById = createAsyncThunk(
  'speakers/getSpeakerById',
  async (speakerId: string) => {
    return await speakerApi.getSpeakerById(speakerId);
  }
);

export const createSpeaker = createAsyncThunk(
  'speakers/createSpeaker',
  async (speakerData: any) => {
    return await speakerApi.createSpeaker(speakerData);
  }
);

export const updateSpeaker = createAsyncThunk(
  'speakers/updateSpeaker',
  async ({ speakerId, speakerData }: { speakerId: string; speakerData: any }) => {
    return await speakerApi.updateSpeaker(speakerId, speakerData);
  }
);

export const getBucketStatistics = createAsyncThunk(
  'speakers/getBucketStatistics',
  async () => {
    return await speakerApi.getBucketStatistics();
  }
);

export const getSpeakersNeedingTransition = createAsyncThunk(
  'speakers/getSpeakersNeedingTransition',
  async () => {
    return await speakerApi.getSpeakersNeedingTransition();
  }
);

export const createTransitionRequest = createAsyncThunk(
  'speakers/createTransitionRequest',
  async (requestData: CreateTransitionRequest) => {
    return await speakerApi.createTransitionRequest(requestData);
  }
);

export const getPendingTransitionRequests = createAsyncThunk(
  'speakers/getPendingTransitionRequests',
  async () => {
    return await speakerApi.getPendingTransitionRequests();
  }
);

export const approveTransitionRequest = createAsyncThunk(
  'speakers/approveTransitionRequest',
  async ({ requestId, approvalData }: { requestId: string; approvalData: any }) => {
    return await speakerApi.approveTransitionRequest(requestId, approvalData);
  }
);

export const getComprehensiveSpeakerView = createAsyncThunk(
  'speakers/getComprehensiveSpeakerView',
  async ({ speakerId, options }: { speakerId: string; options?: any }) => {
    return await speakerApi.getComprehensiveSpeakerView(speakerId, options);
  }
);

export const getQuickFilterOptions = createAsyncThunk(
  'speakers/getQuickFilterOptions',
  async () => {
    return await speakerApi.getQuickFilterOptions();
  }
);

// State interface
interface SpeakerState {
  // Speaker list and search
  speakers: Speaker[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  totalPages: number;
  searchFilters: SpeakerSearchFilters;
  quickFilters: QuickFilterOption[];
  
  // Selected speaker details
  selectedSpeaker: Speaker | null;
  comprehensiveView: ComprehensiveSpeakerView | null;
  
  // Statistics and analytics
  bucketStatistics: SpeakerBucketStats | null;
  speakersNeedingTransition: Speaker[];
  
  // Transition requests
  transitionRequests: BucketTransitionRequest[];
  pendingTransitions: BucketTransitionRequest[];
  
  // UI state
  selectedSpeakerIds: string[];
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  viewMode: 'table' | 'grid' | 'analytics';
  
  // Loading states
  loading: {
    speakers: boolean;
    speakerDetails: boolean;
    statistics: boolean;
    transitions: boolean;
    creating: boolean;
    updating: boolean;
  };
  
  // Error states
  error: {
    speakers: string | null;
    speakerDetails: string | null;
    statistics: string | null;
    transitions: string | null;
    general: string | null;
  };
}

// Initial state
const initialState: SpeakerState = {
  speakers: [],
  totalCount: 0,
  currentPage: 1,
  pageSize: 50,
  totalPages: 0,
  searchFilters: {},
  quickFilters: [],
  
  selectedSpeaker: null,
  comprehensiveView: null,
  
  bucketStatistics: null,
  speakersNeedingTransition: [],
  
  transitionRequests: [],
  pendingTransitions: [],
  
  selectedSpeakerIds: [],
  sortBy: 'speaker_name',
  sortOrder: 'asc',
  viewMode: 'table',
  
  loading: {
    speakers: false,
    speakerDetails: false,
    statistics: false,
    transitions: false,
    creating: false,
    updating: false,
  },
  
  error: {
    speakers: null,
    speakerDetails: null,
    statistics: null,
    transitions: null,
    general: null,
  },
};

// Slice
const speakerSlice = createSlice({
  name: 'speakers',
  initialState,
  reducers: {
    // Search and filtering
    setSearchFilters: (state, action: PayloadAction<SpeakerSearchFilters>) => {
      state.searchFilters = action.payload;
      state.currentPage = 1; // Reset to first page when filters change
    },
    
    clearSearchFilters: (state) => {
      state.searchFilters = {};
      state.currentPage = 1;
    },
    
    setCurrentPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
      state.currentPage = 1; // Reset to first page when page size changes
    },
    
    // Sorting
    setSorting: (state, action: PayloadAction<{ sortBy: string; sortOrder: 'asc' | 'desc' }>) => {
      state.sortBy = action.payload.sortBy;
      state.sortOrder = action.payload.sortOrder;
    },
    
    // Selection
    setSelectedSpeakerIds: (state, action: PayloadAction<string[]>) => {
      state.selectedSpeakerIds = action.payload;
    },
    
    toggleSpeakerSelection: (state, action: PayloadAction<string>) => {
      const speakerId = action.payload;
      const index = state.selectedSpeakerIds.indexOf(speakerId);
      
      if (index > -1) {
        state.selectedSpeakerIds.splice(index, 1);
      } else {
        state.selectedSpeakerIds.push(speakerId);
      }
    },
    
    selectAllSpeakers: (state) => {
      state.selectedSpeakerIds = state.speakers.map(speaker => speaker.speaker_id);
    },
    
    clearSelection: (state) => {
      state.selectedSpeakerIds = [];
    },
    
    // View mode
    setViewMode: (state, action: PayloadAction<'table' | 'grid' | 'analytics'>) => {
      state.viewMode = action.payload;
    },
    
    // Selected speaker
    setSelectedSpeaker: (state, action: PayloadAction<Speaker | null>) => {
      state.selectedSpeaker = action.payload;
    },
    
    // Clear errors
    clearErrors: (state) => {
      state.error = {
        speakers: null,
        speakerDetails: null,
        statistics: null,
        transitions: null,
        general: null,
      };
    },
    
    clearError: (state, action: PayloadAction<keyof SpeakerState['error']>) => {
      state.error[action.payload] = null;
    },
  },
  
  extraReducers: (builder) => {
    // Search speakers
    builder
      .addCase(searchSpeakers.pending, (state) => {
        state.loading.speakers = true;
        state.error.speakers = null;
      })
      .addCase(searchSpeakers.fulfilled, (state, action) => {
        state.loading.speakers = false;
        state.speakers = action.payload.speakers;
        state.totalCount = action.payload.total_count;
        state.currentPage = action.payload.page;
        state.pageSize = action.payload.page_size;
        state.totalPages = action.payload.total_pages;
      })
      .addCase(searchSpeakers.rejected, (state, action) => {
        state.loading.speakers = false;
        state.error.speakers = action.error.message || 'Failed to search speakers';
      });
    
    // Get speaker by ID
    builder
      .addCase(getSpeakerById.pending, (state) => {
        state.loading.speakerDetails = true;
        state.error.speakerDetails = null;
      })
      .addCase(getSpeakerById.fulfilled, (state, action) => {
        state.loading.speakerDetails = false;
        state.selectedSpeaker = action.payload;
      })
      .addCase(getSpeakerById.rejected, (state, action) => {
        state.loading.speakerDetails = false;
        state.error.speakerDetails = action.error.message || 'Failed to get speaker details';
      });
    
    // Create speaker
    builder
      .addCase(createSpeaker.pending, (state) => {
        state.loading.creating = true;
        state.error.general = null;
      })
      .addCase(createSpeaker.fulfilled, (state, action) => {
        state.loading.creating = false;
        state.speakers.unshift(action.payload);
        state.totalCount += 1;
      })
      .addCase(createSpeaker.rejected, (state, action) => {
        state.loading.creating = false;
        state.error.general = action.error.message || 'Failed to create speaker';
      });
    
    // Update speaker
    builder
      .addCase(updateSpeaker.pending, (state) => {
        state.loading.updating = true;
        state.error.general = null;
      })
      .addCase(updateSpeaker.fulfilled, (state, action) => {
        state.loading.updating = false;
        const index = state.speakers.findIndex(s => s.speaker_id === action.payload.speaker_id);
        if (index > -1) {
          state.speakers[index] = action.payload;
        }
        if (state.selectedSpeaker?.speaker_id === action.payload.speaker_id) {
          state.selectedSpeaker = action.payload;
        }
      })
      .addCase(updateSpeaker.rejected, (state, action) => {
        state.loading.updating = false;
        state.error.general = action.error.message || 'Failed to update speaker';
      });
    
    // Get bucket statistics
    builder
      .addCase(getBucketStatistics.pending, (state) => {
        state.loading.statistics = true;
        state.error.statistics = null;
      })
      .addCase(getBucketStatistics.fulfilled, (state, action) => {
        state.loading.statistics = false;
        state.bucketStatistics = action.payload;
      })
      .addCase(getBucketStatistics.rejected, (state, action) => {
        state.loading.statistics = false;
        state.error.statistics = action.error.message || 'Failed to get bucket statistics';
      });
    
    // Get speakers needing transition
    builder
      .addCase(getSpeakersNeedingTransition.fulfilled, (state, action) => {
        state.speakersNeedingTransition = action.payload;
      });
    
    // Get pending transition requests
    builder
      .addCase(getPendingTransitionRequests.pending, (state) => {
        state.loading.transitions = true;
        state.error.transitions = null;
      })
      .addCase(getPendingTransitionRequests.fulfilled, (state, action) => {
        state.loading.transitions = false;
        state.pendingTransitions = action.payload;
      })
      .addCase(getPendingTransitionRequests.rejected, (state, action) => {
        state.loading.transitions = false;
        state.error.transitions = action.error.message || 'Failed to get pending transitions';
      });
    
    // Get comprehensive speaker view
    builder
      .addCase(getComprehensiveSpeakerView.pending, (state) => {
        state.loading.speakerDetails = true;
        state.error.speakerDetails = null;
      })
      .addCase(getComprehensiveSpeakerView.fulfilled, (state, action) => {
        state.loading.speakerDetails = false;
        state.comprehensiveView = action.payload;
        state.selectedSpeaker = action.payload.speaker;
      })
      .addCase(getComprehensiveSpeakerView.rejected, (state, action) => {
        state.loading.speakerDetails = false;
        state.error.speakerDetails = action.error.message || 'Failed to get comprehensive view';
      });
    
    // Get quick filter options
    builder
      .addCase(getQuickFilterOptions.fulfilled, (state, action) => {
        state.quickFilters = action.payload;
      });
  },
});

// Export actions
export const {
  setSearchFilters,
  clearSearchFilters,
  setCurrentPage,
  setPageSize,
  setSorting,
  setSelectedSpeakerIds,
  toggleSpeakerSelection,
  selectAllSpeakers,
  clearSelection,
  setViewMode,
  setSelectedSpeaker,
  clearErrors,
  clearError,
} = speakerSlice.actions;

// Selectors
export const selectSpeakers = (state: { speakers: SpeakerState }) => state.speakers.speakers;
export const selectSpeakersLoading = (state: { speakers: SpeakerState }) => state.speakers.loading.speakers;
export const selectSpeakersError = (state: { speakers: SpeakerState }) => state.speakers.error.speakers;
export const selectSelectedSpeaker = (state: { speakers: SpeakerState }) => state.speakers.selectedSpeaker;
export const selectComprehensiveView = (state: { speakers: SpeakerState }) => state.speakers.comprehensiveView;
export const selectBucketStatistics = (state: { speakers: SpeakerState }) => state.speakers.bucketStatistics;
export const selectSearchFilters = (state: { speakers: SpeakerState }) => state.speakers.searchFilters;
export const selectSelectedSpeakerIds = (state: { speakers: SpeakerState }) => state.speakers.selectedSpeakerIds;
export const selectPagination = (state: { speakers: SpeakerState }) => ({
  currentPage: state.speakers.currentPage,
  pageSize: state.speakers.pageSize,
  totalCount: state.speakers.totalCount,
  totalPages: state.speakers.totalPages,
});
export const selectViewMode = (state: { speakers: SpeakerState }) => state.speakers.viewMode;
export const selectQuickFilters = (state: { speakers: SpeakerState }) => state.speakers.quickFilters;
export const selectPendingTransitions = (state: { speakers: SpeakerState }) => state.speakers.pendingTransitions;

export default speakerSlice.reducer;

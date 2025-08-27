/**
 * Speaker Management Feature Exports
 * 
 * Central export file for the speaker management feature
 */

// Pages
export { default as SpeakerManagementPage } from './pages/SpeakerManagementPage';

// Components
export { default as SpeakerSearchAndSelection } from './components/SpeakerSearchAndSelection';
export { default as SpeakerTable } from './components/SpeakerTable';
export { default as SpeakerStatistics } from './components/SpeakerStatistics';
export { default as SpeakerDetailsDialog } from './components/SpeakerDetailsDialog';
export { default as CreateSpeakerDialog } from './components/CreateSpeakerDialog';
export { default as BulkActionsToolbar } from './components/BulkActionsToolbar';

// Redux
export {
  default as speakerReducer,
  // Actions
  searchSpeakers,
  getSpeakerById,
  createSpeaker,
  updateSpeaker,
  getBucketStatistics,
  getSpeakersNeedingTransition,
  createTransitionRequest,
  getPendingTransitionRequests,
  approveTransitionRequest,
  getComprehensiveSpeakerView,
  getQuickFilterOptions,
  // Sync actions
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
  // Selectors
  selectSpeakers,
  selectSpeakersLoading,
  selectSpeakersError,
  selectSelectedSpeaker,
  selectComprehensiveView,
  selectBucketStatistics,
  selectSearchFilters,
  selectSelectedSpeakerIds,
  selectPagination,
  selectViewMode,
  selectQuickFilters,
  selectPendingTransitions,
} from './speaker-slice';

// API
export { speakerApi } from '@/infrastructure/api/speaker-api';

// Types (re-export from domain)
export type {
  Speaker,
  SpeakerBucket,
  QualityTrend,
  TransitionStatus,
  SpeakerSearchFilters,
  SpeakerSearchParams,
  SpeakerListResponse,
  BucketTransitionRequest,
  CreateTransitionRequest,
  SpeakerBucketStats,
  SERMetrics,
  SpeakerSERAnalysis,
  ComprehensiveSpeakerView,
  SpeakerTableColumn,
  SpeakerSelectionState,
  BucketVisualizationData,
  SpeakerFormData,
  TransitionRequestFormData,
  AdvancedSearchFilters,
  QuickFilterOption,
  DashboardMetrics,
} from '@/domain/types/speaker';

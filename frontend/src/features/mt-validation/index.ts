/**
 * MT Validation Feature Exports
 * 
 * Central export file for the MT validation feature
 */

// Pages
export { default as MTValidationPage } from './pages/MTValidationPage';

// Components
export { default as MTValidationInterface } from './components/MTValidationInterface';
export { default as TextComparisonPanel } from './components/TextComparisonPanel';
export { default as SERMetricsPanel } from './components/SERMetricsPanel';
export { default as FeedbackPanel } from './components/FeedbackPanel';
export { default as ValidationProgress } from './components/ValidationProgress';
export { default as KeyboardShortcutsHelper } from './components/KeyboardShortcutsHelper';
export { default as SessionSetupDialog } from './components/SessionSetupDialog';
export { default as SessionSummaryDialog } from './components/SessionSummaryDialog';

// Redux
export {
  default as mtValidationReducer,
  // Async actions
  startValidationSession,
  getValidationSession,
  getValidationTestData,
  submitMTFeedback,
  completeValidationSession,
  getValidationSessions,
  getSessionSummary,
  getMTUserStatistics,
  calculateTextDifferences,
  // Sync actions
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
  // Selectors
  selectCurrentSession,
  selectCurrentItem,
  selectCurrentItemIndex,
  selectTestDataItems,
  selectCurrentFeedback,
  selectSessionProgress,
  selectComparisonMode,
  selectShowDifferences,
  selectShowSERMetrics,
  selectTextDifferences,
  selectValidationLoading,
  selectValidationError,
  selectUserPreferences,
  selectWorkflowState,
} from './mt-validation-slice';

// API
export { mtValidationApi } from '@/infrastructure/api/mt-validation-api';

// Types (re-export from domain)
export type {
  ValidationSession,
  ValidationTestData,
  ValidationItem,
  MTFeedback,
  SERMetrics,
  SERComparison,
  TextDifference,
  SessionStatus,
  ImprovementAssessment,
  ValidationItemStatus,
  StartValidationSessionRequest,
  SubmitMTFeedbackRequest,
  CompleteValidationSessionRequest,
  ValidationWorkflowState,
  MTValidationFilters,
  ValidationSessionSummary,
  MTUserStatistics,
  DifferenceHighlightOptions,
  ValidationPreferences,
  ValidationKeyboardShortcuts,
  MTFeedbackFormData,
  ValidationAnalytics,
  ValidationExportData,
  ValidationUpdate,
} from '@/domain/types/mt-validation';

/**
 * UI slice for global UI state management
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { AppError, ErrorState, CreateErrorInput } from '@shared/types/error.types';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  duration?: number;
  persistent?: boolean;
}

interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'auto';
  notifications: Notification[];
  loading: {
    global: boolean;
    [key: string]: boolean;
  };
  modals: {
    [key: string]: {
      open: boolean;
      data?: any;
    };
  };
  errors: ErrorState;
}

const initialState: UIState = {
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
  loading: {
    global: false,
  },
  modals: {},
  errors: {
    errors: [],
    activeError: null,
    showErrorDetails: false,
    errorDetailsExpanded: false,
    errorHandlingEnabled: true,
    displayPreferences: {
      showTechnicalDetailsInProduction: false,
      autoDismissLowSeverity: true,
      autoDismissTimeout: 5000,
    },
  },
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload;
    },
    
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const notification: Notification = {
        id: Date.now().toString(),
        ...action.payload,
      };
      state.notifications.push(notification);
    },
    
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    setLoading: (state, action: PayloadAction<{ key: string; loading: boolean }>) => {
      const { key, loading } = action.payload;
      state.loading[key] = loading;
    },
    
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.global = action.payload;
    },
    
    openModal: (state, action: PayloadAction<{ key: string; data?: any }>) => {
      const { key, data } = action.payload;
      state.modals[key] = { open: true, data };
    },
    
    closeModal: (state, action: PayloadAction<string>) => {
      const key = action.payload;
      if (state.modals[key]) {
        state.modals[key].open = false;
        state.modals[key].data = undefined;
      }
    },

    // Error handling actions
    addError: (state, action: PayloadAction<AppError>) => {
      const error = action.payload;
      state.errors.errors.push(error);

      // Set as active error if none is active or if this is higher severity
      if (!state.errors.activeError ||
          getSeverityLevel(error.severity) > getSeverityLevel(state.errors.activeError.severity)) {
        state.errors.activeError = error;
      }

      // Limit error queue size
      if (state.errors.errors.length > 50) {
        state.errors.errors = state.errors.errors.slice(-50);
      }
    },

    removeError: (state, action: PayloadAction<string>) => {
      const errorId = action.payload;
      state.errors.errors = state.errors.errors.filter(error => error.id !== errorId);

      // Clear active error if it was removed
      if (state.errors.activeError?.id === errorId) {
        state.errors.activeError = state.errors.errors.length > 0 ? state.errors.errors[state.errors.errors.length - 1] : null;
      }
    },

    clearAllErrors: (state) => {
      state.errors.errors = [];
      state.errors.activeError = null;
      state.errors.showErrorDetails = false;
      state.errors.errorDetailsExpanded = false;
    },

    setActiveError: (state, action: PayloadAction<string | null>) => {
      const errorId = action.payload;
      if (errorId) {
        const error = state.errors.errors.find(e => e.id === errorId);
        state.errors.activeError = error || null;
      } else {
        state.errors.activeError = null;
      }
    },

    acknowledgeError: (state, action: PayloadAction<string>) => {
      const errorId = action.payload;
      const error = state.errors.errors.find(e => e.id === errorId);
      if (error) {
        error.acknowledged = true;
      }
    },

    toggleErrorDetails: (state, action: PayloadAction<string>) => {
      const errorId = action.payload;
      const error = state.errors.errors.find(e => e.id === errorId);
      if (error) {
        error.detailsVisible = !error.detailsVisible;
        state.errors.showErrorDetails = error.detailsVisible;
        if (!error.detailsVisible) {
          state.errors.errorDetailsExpanded = false;
        }
      }
    },

    setShowErrorDetails: (state, action: PayloadAction<boolean>) => {
      state.errors.showErrorDetails = action.payload;
      if (!action.payload) {
        state.errors.errorDetailsExpanded = false;
      }
    },

    setErrorDetailsExpanded: (state, action: PayloadAction<boolean>) => {
      state.errors.errorDetailsExpanded = action.payload;
    },

    setErrorHandlingEnabled: (state, action: PayloadAction<boolean>) => {
      state.errors.errorHandlingEnabled = action.payload;
    },

    updateErrorDisplayPreferences: (state, action: PayloadAction<Partial<ErrorState['displayPreferences']>>) => {
      state.errors.displayPreferences = {
        ...state.errors.displayPreferences,
        ...action.payload,
      };
    },
  },
});

// Helper function to get numeric severity level
function getSeverityLevel(severity: AppError['severity']): number {
  const levels = { low: 1, medium: 2, high: 3, critical: 4 };
  return levels[severity] || 1;
}

export const {
  toggleSidebar,
  setSidebarOpen,
  setTheme,
  addNotification,
  removeNotification,
  clearNotifications,
  setLoading,
  setGlobalLoading,
  openModal,
  closeModal,
  addError,
  removeError,
  clearAllErrors,
  setActiveError,
  acknowledgeError,
  toggleErrorDetails,
  setShowErrorDetails,
  setErrorDetailsExpanded,
  setErrorHandlingEnabled,
  updateErrorDisplayPreferences,
} = uiSlice.actions;

export default uiSlice.reducer;

// Selectors
export const selectSidebarOpen = (state: { ui: UIState }) => state.ui.sidebarOpen;
export const selectTheme = (state: { ui: UIState }) => state.ui.theme;
export const selectNotifications = (state: { ui: UIState }) => state.ui.notifications;
export const selectLoading = (state: { ui: UIState }) => state.ui.loading;
export const selectModals = (state: { ui: UIState }) => state.ui.modals;

// Error selectors
export const selectErrors = (state: { ui: UIState }) => state.ui.errors.errors;
export const selectActiveError = (state: { ui: UIState }) => state.ui.errors.activeError;
export const selectShowErrorDetails = (state: { ui: UIState }) => state.ui.errors.showErrorDetails;
export const selectErrorDetailsExpanded = (state: { ui: UIState }) => state.ui.errors.errorDetailsExpanded;
export const selectErrorHandlingEnabled = (state: { ui: UIState }) => state.ui.errors.errorHandlingEnabled;
export const selectErrorDisplayPreferences = (state: { ui: UIState }) => state.ui.errors.displayPreferences;
export const selectErrorState = (state: { ui: UIState }) => state.ui.errors;

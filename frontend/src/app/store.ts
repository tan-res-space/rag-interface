/**
 * Redux store configuration with RTK Query
 */

import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { authApi } from '@infrastructure/api/auth-api';
import { errorReportApi } from '@infrastructure/api/error-report-api';
import { verificationApi } from '@infrastructure/api/verification-api';
import { userApi } from '@infrastructure/api/user-api';
import { healthApi } from '@infrastructure/api/health-api';
import authReducer from '@features/auth/auth-slice';
import uiReducer from '@shared/slices/ui-slice';
import speakerReducer from '@features/speaker-management/speaker-slice';
import mtValidationReducer from '@features/mt-validation/mt-validation-slice';
import dashboardReducer from '@features/dashboard/dashboard-slice';

export const store = configureStore({
  reducer: {
    // Feature reducers
    auth: authReducer,
    ui: uiReducer,
    speakers: speakerReducer,
    mtValidation: mtValidationReducer,
    dashboard: dashboardReducer,
    
    // API reducers
    [authApi.reducerPath]: authApi.reducer,
    [errorReportApi.reducerPath]: errorReportApi.reducer,
    [verificationApi.reducerPath]: verificationApi.reducer,
    [userApi.reducerPath]: userApi.reducer,
    [healthApi.reducerPath]: healthApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [
          // Ignore these action types
          'persist/PERSIST',
          'persist/REHYDRATE',
        ],
      },
    })
      .concat(authApi.middleware)
      .concat(errorReportApi.middleware)
      .concat(verificationApi.middleware)
      .concat(userApi.middleware)
      .concat(healthApi.middleware),
  devTools: process.env.NODE_ENV !== 'production',
});

// Enable listener behavior for the store
setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

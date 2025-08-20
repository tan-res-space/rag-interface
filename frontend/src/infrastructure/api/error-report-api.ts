/**
 * Error Report API adapter
 * Implements Hexagonal Architecture adapter pattern for error reporting operations
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { SERVICE_ENDPOINTS } from './base-api';
import type {
  ErrorReport,
  SubmitErrorReportRequest,
  SearchErrorsRequest,
  UpdateErrorReportRequest,
  PaginatedResponse,
} from '@domain/types';

// Base query for error report API
const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as any).auth.token;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    headers.set('content-type', 'application/json');
    return headers;
  },
});

export const errorReportApi = createApi({
  reducerPath: 'errorReportApi',
  baseQuery,
  tagTypes: ['ErrorReport'],
  endpoints: (builder) => ({
    // Submit error report
    submitErrorReport: builder.mutation<{ errorId: string }, SubmitErrorReportRequest>({
      query: (errorReport) => ({
        url: `${SERVICE_ENDPOINTS.ERROR_REPORTING}`,
        method: 'POST',
        body: errorReport,
      }),
      invalidatesTags: ['ErrorReport'],
    }),

    // Search error reports
    searchErrorReports: builder.query<PaginatedResponse<ErrorReport>, SearchErrorsRequest>({
      query: (searchRequest) => ({
        url: `${SERVICE_ENDPOINTS.ERROR_REPORTING}/search`,
        method: 'POST',
        body: searchRequest,
      }),
      providesTags: ['ErrorReport'],
    }),

    // Get error report by ID
    getErrorReport: builder.query<ErrorReport, string>({
      query: (errorId) => ({
        url: `${SERVICE_ENDPOINTS.ERROR_REPORTING}/${errorId}`,
        method: 'GET',
      }),
      providesTags: ['ErrorReport'],
    }),

    // Update error report
    updateErrorReport: builder.mutation<ErrorReport, UpdateErrorReportRequest>({
      query: ({ errorId, ...updateData }) => ({
        url: `${SERVICE_ENDPOINTS.ERROR_REPORTING}/${errorId}`,
        method: 'PATCH',
        body: updateData,
      }),
      invalidatesTags: ['ErrorReport'],
    }),

    // Delete error report
    deleteErrorReport: builder.mutation<void, string>({
      query: (errorId) => ({
        url: `${SERVICE_ENDPOINTS.ERROR_REPORTING}/${errorId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['ErrorReport'],
    }),
  }),
});

export const {
  useSubmitErrorReportMutation,
  useSearchErrorReportsQuery,
  useGetErrorReportQuery,
  useUpdateErrorReportMutation,
  useDeleteErrorReportMutation,
} = errorReportApi;

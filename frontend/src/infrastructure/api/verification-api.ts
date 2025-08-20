/**
 * Verification API adapter
 * Implements Hexagonal Architecture adapter pattern for verification operations
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { SERVICE_ENDPOINTS } from './base-api';
import type {
  VerificationItem,
  VerificationRequest,
  VerificationResponse,
  DashboardSummary,
  BulkVerificationRequest,
  PaginatedResponse,
} from '@domain/types';

// Base query for verification API
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

export const verificationApi = createApi({
  reducerPath: 'verificationApi',
  baseQuery,
  tagTypes: ['Verification', 'Dashboard'],
  endpoints: (builder) => ({
    // Get verification items
    getVerificationItems: builder.query<PaginatedResponse<VerificationItem>, any>({
      query: (params) => ({
        url: `${SERVICE_ENDPOINTS.VERIFICATION}/items`,
        method: 'GET',
        params,
      }),
      providesTags: ['Verification'],
    }),

    // Submit verification
    submitVerification: builder.mutation<VerificationResponse, { itemId: string } & VerificationRequest>({
      query: ({ itemId, ...verification }) => ({
        url: `${SERVICE_ENDPOINTS.VERIFICATION}/items/${itemId}/verify`,
        method: 'POST',
        body: verification,
      }),
      invalidatesTags: ['Verification', 'Dashboard'],
    }),

    // Bulk verification
    bulkVerification: builder.mutation<{ processed: number }, BulkVerificationRequest>({
      query: (bulkRequest) => ({
        url: `${SERVICE_ENDPOINTS.VERIFICATION}/bulk`,
        method: 'POST',
        body: bulkRequest,
      }),
      invalidatesTags: ['Verification', 'Dashboard'],
    }),

    // Get dashboard summary
    getDashboardSummary: builder.query<DashboardSummary, { period?: string }>({
      query: ({ period = '7d' }) => ({
        url: `${SERVICE_ENDPOINTS.VERIFICATION}/dashboard`,
        method: 'GET',
        params: { period },
      }),
      providesTags: ['Dashboard'],
    }),

    // Get verification history
    getVerificationHistory: builder.query<PaginatedResponse<VerificationResponse>, any>({
      query: (params) => ({
        url: `${SERVICE_ENDPOINTS.VERIFICATION}/history`,
        method: 'GET',
        params,
      }),
      providesTags: ['Verification'],
    }),
  }),
});

export const {
  useGetVerificationItemsQuery,
  useSubmitVerificationMutation,
  useBulkVerificationMutation,
  useGetDashboardSummaryQuery,
  useGetVerificationHistoryQuery,
} = verificationApi;

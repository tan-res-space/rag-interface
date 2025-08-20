/**
 * Authentication API adapter
 * Implements Hexagonal Architecture adapter pattern for auth operations
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { SERVICE_ENDPOINTS } from './base-api';
import type {
  AuthenticationRequest,
  AuthenticationResponse,
  TokenValidationResponse,
  User,
} from '@domain/types';

// Base query for auth API
const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  prepareHeaders: (headers) => {
    headers.set('content-type', 'application/json');
    return headers;
  },
});

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery,
  tagTypes: ['Auth'],
  endpoints: (builder) => ({
    // Login endpoint
    login: builder.mutation<AuthenticationResponse, AuthenticationRequest>({
      query: (credentials) => ({
        url: `${SERVICE_ENDPOINTS.AUTH}/login`,
        method: 'POST',
        body: credentials,
      }),
      invalidatesTags: ['Auth'],
    }),

    // Logout endpoint
    logout: builder.mutation<void, void>({
      query: () => ({
        url: `${SERVICE_ENDPOINTS.AUTH}/logout`,
        method: 'POST',
      }),
      invalidatesTags: ['Auth'],
    }),

    // Refresh token endpoint
    refreshToken: builder.mutation<AuthenticationResponse, { refreshToken: string }>({
      query: ({ refreshToken }) => ({
        url: `${SERVICE_ENDPOINTS.AUTH}/refresh`,
        method: 'POST',
        body: { refreshToken },
      }),
      invalidatesTags: ['Auth'],
    }),

    // Validate token endpoint
    validateToken: builder.query<TokenValidationResponse, { token: string; requiredPermissions?: string[] }>({
      query: ({ token, requiredPermissions }) => ({
        url: `${SERVICE_ENDPOINTS.AUTH}/validate`,
        method: 'POST',
        body: { token, requiredPermissions },
      }),
      providesTags: ['Auth'],
    }),

    // Get current user profile
    getCurrentUser: builder.query<User, void>({
      query: () => ({
        url: `${SERVICE_ENDPOINTS.AUTH}/me`,
        method: 'GET',
      }),
      providesTags: ['Auth'],
    }),

    // Change password
    changePassword: builder.mutation<
      { success: boolean; message: string },
      { currentPassword: string; newPassword: string }
    >({
      query: (passwordData) => ({
        url: `${SERVICE_ENDPOINTS.AUTH}/change-password`,
        method: 'POST',
        body: passwordData,
      }),
      invalidatesTags: ['Auth'],
    }),
  }),
});

export const {
  useLoginMutation,
  useLogoutMutation,
  useRefreshTokenMutation,
  useValidateTokenQuery,
  useGetCurrentUserQuery,
  useChangePasswordMutation,
} = authApi;

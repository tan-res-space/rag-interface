/**
 * User API adapter
 * Implements Hexagonal Architecture adapter pattern for user management operations
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { SERVICE_ENDPOINTS } from './base-api';
import type {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  ChangePasswordRequest,
  UserAuditLogEntry,
  PaginatedResponse,
} from '@domain/types';

// Base query for user API
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

export const userApi = createApi({
  reducerPath: 'userApi',
  baseQuery,
  tagTypes: ['User', 'AuditLog'],
  endpoints: (builder) => ({
    // Get users
    getUsers: builder.query<PaginatedResponse<User>, any>({
      query: (params) => ({
        url: `${SERVICE_ENDPOINTS.USER_MANAGEMENT}`,
        method: 'GET',
        params,
      }),
      providesTags: ['User'],
    }),

    // Get user by ID
    getUser: builder.query<User, string>({
      query: (userId) => ({
        url: `${SERVICE_ENDPOINTS.USER_MANAGEMENT}/${userId}`,
        method: 'GET',
      }),
      providesTags: ['User'],
    }),

    // Create user
    createUser: builder.mutation<User, CreateUserRequest>({
      query: (userData) => ({
        url: `${SERVICE_ENDPOINTS.USER_MANAGEMENT}`,
        method: 'POST',
        body: userData,
      }),
      invalidatesTags: ['User'],
    }),

    // Update user
    updateUser: builder.mutation<User, UpdateUserRequest>({
      query: ({ userId, ...updateData }) => ({
        url: `${SERVICE_ENDPOINTS.USER_MANAGEMENT}/${userId}`,
        method: 'PATCH',
        body: updateData,
      }),
      invalidatesTags: ['User'],
    }),

    // Delete user
    deleteUser: builder.mutation<void, string>({
      query: (userId) => ({
        url: `${SERVICE_ENDPOINTS.USER_MANAGEMENT}/${userId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['User'],
    }),

    // Change user password
    changeUserPassword: builder.mutation<{ success: boolean }, ChangePasswordRequest>({
      query: ({ userId, ...passwordData }) => ({
        url: `${SERVICE_ENDPOINTS.USER_MANAGEMENT}/${userId}/change-password`,
        method: 'POST',
        body: passwordData,
      }),
      invalidatesTags: ['User'],
    }),

    // Get user audit log
    getUserAuditLog: builder.query<PaginatedResponse<UserAuditLogEntry>, { userId: string; params?: any }>({
      query: ({ userId, params }) => ({
        url: `${SERVICE_ENDPOINTS.USER_MANAGEMENT}/${userId}/audit-log`,
        method: 'GET',
        params,
      }),
      providesTags: ['AuditLog'],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useGetUserQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useChangeUserPasswordMutation,
  useGetUserAuditLogQuery,
} = userApi;

/**
 * Application routing configuration
 */

import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { ProtectedRoute } from '@features/auth/ProtectedRoute';
import { Layout } from '@shared/components/Layout';
import { UserRole } from '@domain/types';

// Lazy load components for code splitting
const LoginPage = React.lazy(() => import('@features/auth/pages/LoginPage'));
const DashboardPage = React.lazy(() => import('@features/dashboard/pages/DashboardPage'));
const ErrorReportingPage = React.lazy(() => import('@features/error-reporting/pages/ErrorReportingPage'));
const VerificationPage = React.lazy(() => import('@features/verification/pages/VerificationPage'));
const AdminPage = React.lazy(() => import('@features/admin/pages/AdminPage'));
const NotFoundPage = React.lazy(() => import('@shared/pages/NotFoundPage'));

// Loading component
const LoadingFallback = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="200px"
  >
    <CircularProgress />
  </Box>
);

export const AppRoutes: React.FC = () => {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected routes with layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          
          {/* Error Reporting */}
          <Route path="error-reporting" element={<ErrorReportingPage />} />
          
          {/* Verification */}
          <Route path="verification" element={<VerificationPage />} />
          
          {/* Admin (role-based access) */}
          <Route
            path="admin"
            element={
              <ProtectedRoute requiredRoles={[UserRole.ADMIN, UserRole.QA_SUPERVISOR]}>
                <AdminPage />
              </ProtectedRoute>
            }
          />
        </Route>
        
        {/* 404 page */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
};

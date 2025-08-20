/**
 * Protected route component with role-based access control
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useAppSelector } from '@/app/hooks';
import { selectCurrentUser, selectToken } from './auth-slice';
import { UserRole } from '@domain/types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: UserRole[];
  requiredPermissions?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
  requiredPermissions,
}) => {
  const location = useLocation();
  const token = useAppSelector(selectToken);
  const currentUser = useAppSelector(selectCurrentUser);

  // If no token, redirect to login
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If token exists but no user data yet, show loading
  if (token && !currentUser) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        gap={2}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Loading user data...
        </Typography>
      </Box>
    );
  }

  // Check role-based access
  if (requiredRoles && currentUser) {
    const hasRequiredRole = requiredRoles.some(role => 
      currentUser.roles.includes(role)
    );
    
    if (!hasRequiredRole) {
      return (
        <Box
          display="flex"
          flexDirection="column"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          gap={2}
        >
          <Typography variant="h5" color="error">
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" textAlign="center">
            You don't have the required permissions to access this page.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Required roles: {requiredRoles.join(', ')}
          </Typography>
        </Box>
      );
    }
  }

  // Check permission-based access
  if (requiredPermissions && currentUser) {
    const hasRequiredPermissions = requiredPermissions.every(permission =>
      currentUser.permissions.includes(permission)
    );
    
    if (!hasRequiredPermissions) {
      return (
        <Box
          display="flex"
          flexDirection="column"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          gap={2}
        >
          <Typography variant="h5" color="error">
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" textAlign="center">
            You don't have the required permissions to access this page.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Required permissions: {requiredPermissions.join(', ')}
          </Typography>
        </Box>
      );
    }
  }

  return <>{children}</>;
};

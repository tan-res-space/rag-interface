/**
 * Authentication provider component
 */

import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import { selectToken, setCredentials, logout } from './auth-slice';
import { useGetCurrentUserQuery } from '@infrastructure/api/auth-api';

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useAppDispatch();
  const token = useAppSelector(selectToken);

  // Get current user if token exists
  const {
    data: currentUser,
    error,
  } = useGetCurrentUserQuery(undefined, {
    skip: !token,
  });

  useEffect(() => {
    if (token && currentUser) {
      // Update auth state with current user data
      dispatch(setCredentials({
        accessToken: token,
        refreshToken: localStorage.getItem('refreshToken') || '',
        tokenType: 'bearer',
        expiresIn: 3600, // Default value
        user: currentUser,
      }));
    } else if (error) {
      // Token is invalid, logout user
      dispatch(logout());
    }
  }, [token, currentUser, error, dispatch]);

  return <>{children}</>;
};

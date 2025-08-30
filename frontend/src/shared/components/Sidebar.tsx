/**
 * Sidebar navigation component
 */

import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ReportProblem as ErrorIcon,
  VerifiedUser as VerificationIcon,
  AdminPanelSettings as AdminIcon,
  Analytics as AnalyticsIcon,
  MonitorHeart as SystemHealthIcon,
} from '@mui/icons-material';
import { useAppSelector } from '@/app/hooks';
import { selectCurrentUser } from '@features/auth/auth-slice';
import { UserRole } from '@domain/types';

interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: React.ReactNode;
  requiredRoles?: UserRole[];
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: <DashboardIcon />,
  },
  {
    id: 'error-reporting',
    label: 'Error Reporting',
    path: '/error-reporting',
    icon: <ErrorIcon />,
    requiredRoles: [UserRole.QA_PERSONNEL, UserRole.QA_SUPERVISOR, UserRole.ADMIN],
  },
  {
    id: 'verification',
    label: 'Verification',
    path: '/verification',
    icon: <VerificationIcon />,
    requiredRoles: [UserRole.QA_SUPERVISOR, UserRole.ADMIN],
  },
  {
    id: 'analytics',
    label: 'Analytics',
    path: '/analytics',
    icon: <AnalyticsIcon />,
    requiredRoles: [UserRole.QA_SUPERVISOR, UserRole.ADMIN],
  },
  {
    id: 'system-health',
    label: 'System Health',
    path: '/system-health',
    icon: <SystemHealthIcon />,
    requiredRoles: [UserRole.QA_SUPERVISOR, UserRole.ADMIN],
  },
  {
    id: 'admin',
    label: 'Administration',
    path: '/admin',
    icon: <AdminIcon />,
    requiredRoles: [UserRole.ADMIN],
  },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = useAppSelector(selectCurrentUser);

  const hasRequiredRole = (requiredRoles?: UserRole[]): boolean => {
    if (!requiredRoles || !currentUser) return true;
    return requiredRoles.some(role => currentUser.roles.includes(role));
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const visibleItems = navigationItems.filter(item => hasRequiredRole(item.requiredRoles));

  return (
    <Box sx={{ overflow: 'auto', height: '100%' }}>
      <List>
        {visibleItems.map((item, index) => (
          <React.Fragment key={item.id}>
            <ListItem disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: location.pathname === item.path ? 'inherit' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  primaryTypographyProps={{
                    fontWeight: location.pathname === item.path ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
            {/* Add divider after dashboard */}
            {index === 0 && <Divider sx={{ my: 1 }} />}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
};

/**
 * Dashboard Header Component
 * 
 * Header with title, connection status, refresh controls,
 * and quick action buttons.
 */

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Chip,
  CircularProgress,
  Badge,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  WifiOff as DisconnectedIcon,
  Wifi as ConnectedIcon,
  Schedule as TimeIcon,
} from '@mui/icons-material';

interface DashboardHeaderProps {
  title: string;
  subtitle?: string;
  lastUpdated: string;
  isConnected: boolean;
  onRefresh: () => void;
  onToggleFullscreen: () => void;
  loading?: boolean;
  isFullscreen?: boolean;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  title,
  subtitle,
  lastUpdated,
  isConnected,
  onRefresh,
  onToggleFullscreen,
  loading = false,
  isFullscreen = false,
}) => {
  return (
    <AppBar position="static" elevation={1} sx={{ backgroundColor: 'background.paper', color: 'text.primary' }}>
      <Toolbar>
        {/* Title Section */}
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h5" component="h1" fontWeight="bold">
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>

        {/* Status and Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Last Updated */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimeIcon fontSize="small" color="action" />
            <Typography variant="caption" color="text.secondary">
              Last updated: {lastUpdated}
            </Typography>
          </Box>

          {/* Connection Status */}
          <Tooltip title={isConnected ? 'Connected' : 'Disconnected'}>
            <Chip
              icon={isConnected ? <ConnectedIcon /> : <DisconnectedIcon />}
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
          </Tooltip>

          {/* Refresh Button */}
          <Tooltip title="Refresh Dashboard">
            <IconButton
              onClick={onRefresh}
              disabled={loading}
              color="primary"
            >
              {loading ? (
                <CircularProgress size={24} />
              ) : (
                <RefreshIcon />
              )}
            </IconButton>
          </Tooltip>

          {/* Fullscreen Toggle */}
          <Tooltip title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}>
            <IconButton
              onClick={onToggleFullscreen}
              color="primary"
            >
              {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default DashboardHeader;

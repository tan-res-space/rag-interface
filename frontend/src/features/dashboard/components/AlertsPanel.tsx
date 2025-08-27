/**
 * Alerts Panel Component
 * 
 * Side panel for displaying system alerts and notifications
 * with filtering, acknowledgment, and action capabilities.
 */

import React, { useState } from 'react';
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Button,
  Divider,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Check as CheckIcon,
  MarkEmailRead as MarkAllReadIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { DashboardAlert } from '@/domain/types/dashboard';

interface AlertsPanelProps {
  open: boolean;
  onClose: () => void;
  alerts: DashboardAlert[];
  onAcknowledgeAlert?: (alertId: string) => void;
  onMarkAllRead?: () => void;
}

type AlertFilter = 'all' | 'unread' | 'info' | 'warning' | 'error' | 'success';

export const AlertsPanel: React.FC<AlertsPanelProps> = ({
  open,
  onClose,
  alerts,
  onAcknowledgeAlert,
  onMarkAllRead,
}) => {
  const [filter, setFilter] = useState<AlertFilter>('all');

  // Filter alerts based on current filter
  const filteredAlerts = alerts.filter(alert => {
    switch (filter) {
      case 'unread':
        return !alert.acknowledged;
      case 'info':
      case 'warning':
      case 'error':
      case 'success':
        return alert.type === filter;
      default:
        return true;
    }
  });

  // Get alert icon
  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'info': return <InfoIcon color="info" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      case 'success': return <SuccessIcon color="success" />;
      default: return <InfoIcon />;
    }
  };

  // Get severity color
  const getSeverityColor = (severity: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now.getTime() - alertTime.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    return alertTime.toLocaleDateString();
  };

  // Handle acknowledge alert
  const handleAcknowledgeAlert = (alertId: string) => {
    onAcknowledgeAlert?.(alertId);
  };

  // Get filter counts
  const getFilterCounts = () => {
    return {
      all: alerts.length,
      unread: alerts.filter(a => !a.acknowledged).length,
      info: alerts.filter(a => a.type === 'info').length,
      warning: alerts.filter(a => a.type === 'warning').length,
      error: alerts.filter(a => a.type === 'error').length,
      success: alerts.filter(a => a.type === 'success').length,
    };
  };

  const filterCounts = getFilterCounts();

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { width: 400 }
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              System Alerts
            </Typography>
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Filter Buttons */}
          <ToggleButtonGroup
            value={filter}
            exclusive
            onChange={(_, newFilter) => newFilter && setFilter(newFilter)}
            size="small"
            sx={{ mb: 2, flexWrap: 'wrap' }}
          >
            <ToggleButton value="all">
              <Badge badgeContent={filterCounts.all} color="primary" max={99}>
                All
              </Badge>
            </ToggleButton>
            <ToggleButton value="unread">
              <Badge badgeContent={filterCounts.unread} color="error" max={99}>
                Unread
              </Badge>
            </ToggleButton>
            <ToggleButton value="error">
              <Badge badgeContent={filterCounts.error} color="error" max={99}>
                Error
              </Badge>
            </ToggleButton>
            <ToggleButton value="warning">
              <Badge badgeContent={filterCounts.warning} color="warning" max={99}>
                Warning
              </Badge>
            </ToggleButton>
          </ToggleButtonGroup>

          {/* Actions */}
          {filterCounts.unread > 0 && (
            <Button
              startIcon={<MarkAllReadIcon />}
              onClick={onMarkAllRead}
              size="small"
              variant="outlined"
              fullWidth
            >
              Mark All as Read
            </Button>
          )}
        </Box>

        {/* Alerts List */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {filteredAlerts.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                {filter === 'unread' ? 'No unread alerts' : 'No alerts found'}
              </Typography>
            </Box>
          ) : (
            <List>
              {filteredAlerts.map((alert, index) => (
                <React.Fragment key={alert.id}>
                  <ListItem
                    sx={{
                      backgroundColor: alert.acknowledged ? 'transparent' : 'action.hover',
                      opacity: alert.acknowledged ? 0.7 : 1,
                    }}
                  >
                    <ListItemIcon>
                      {getAlertIcon(alert.type)}
                    </ListItemIcon>
                    
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Typography variant="subtitle2" fontWeight="medium">
                            {alert.title}
                          </Typography>
                          <Chip
                            label={alert.severity.toUpperCase()}
                            size="small"
                            color={getSeverityColor(alert.severity)}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                            {alert.message}
                          </Typography>
                          <Typography variant="caption" color="text.disabled">
                            {alert.source} • {formatTimestamp(alert.timestamp)}
                          </Typography>
                        </Box>
                      }
                    />
                    
                    <ListItemSecondaryAction>
                      {!alert.acknowledged && (
                        <Tooltip title="Mark as read">
                          <IconButton
                            edge="end"
                            size="small"
                            onClick={() => handleAcknowledgeAlert(alert.id)}
                          >
                            <CheckIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </ListItemSecondaryAction>
                  </ListItem>
                  
                  {/* Alert Actions */}
                  {alert.actions && alert.actions.length > 0 && (
                    <Box sx={{ px: 2, pb: 1 }}>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {alert.actions.map((action, actionIndex) => (
                          <Button
                            key={actionIndex}
                            size="small"
                            variant={action.primary ? 'contained' : 'outlined'}
                            color="primary"
                            onClick={() => {
                              // Handle action click
                              console.log(`Action clicked: ${action.action}`);
                            }}
                          >
                            {action.label}
                          </Button>
                        ))}
                      </Box>
                    </Box>
                  )}
                  
                  {index < filteredAlerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary" textAlign="center" display="block">
            {filteredAlerts.length} of {alerts.length} alerts shown
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default AlertsPanel;

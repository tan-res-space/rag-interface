/**
 * Dashboard Settings Component
 * 
 * Settings dialog for dashboard preferences, themes,
 * refresh intervals, and notification settings.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,

  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  TextField,
  Divider,
  IconButton,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Close as CloseIcon,
  Settings as SettingsIcon,
  Palette as ThemeIcon,
  Notifications as NotificationsIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';
import { DashboardPreferences } from '@/domain/types/dashboard';

interface DashboardSettingsProps {
  open: boolean;
  onClose: () => void;
  preferences: DashboardPreferences;
  onSavePreferences?: (preferences: DashboardPreferences) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
};

export const DashboardSettings: React.FC<DashboardSettingsProps> = ({
  open,
  onClose,
  preferences,
  onSavePreferences,
}) => {
  const [localPreferences, setLocalPreferences] = useState<DashboardPreferences>(preferences);
  const [activeTab, setActiveTab] = useState(0);

  // Update local preferences when props change
  useEffect(() => {
    setLocalPreferences(preferences);
  }, [preferences]);

  // Handle preference changes
  const handlePreferenceChange = (key: keyof DashboardPreferences, value: any) => {
    setLocalPreferences(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // Handle nested preference changes
  const handleNestedPreferenceChange = (
    parentKey: keyof DashboardPreferences,
    childKey: string,
    value: any
  ) => {
    setLocalPreferences(prev => ({
      ...prev,
      [parentKey]: {
        ...(prev[parentKey] as any),
        [childKey]: value,
      },
    }));
  };

  // Handle save
  const handleSave = () => {
    onSavePreferences?.(localPreferences);
    onClose();
  };

  // Handle reset to defaults
  const handleReset = () => {
    const defaultPreferences: DashboardPreferences = {
      default_layout: 'default',
      refresh_interval: 30000,
      theme: 'light',
      timezone: 'UTC',
      number_format: 'US',
      chart_animations: true,
      auto_refresh: true,
      notification_settings: {
        alerts: true,
        email_reports: false,
        push_notifications: true,
      },
    };
    setLocalPreferences(defaultPreferences);
  };

  // Format refresh interval for display
  const formatRefreshInterval = (ms: number) => {
    const seconds = ms / 1000;
    if (seconds < 60) return `${seconds}s`;
    const minutes = seconds / 60;
    return `${minutes}m`;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ sx: { height: '80vh' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon color="primary" />
            <Typography variant="h6">Dashboard Settings</Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab icon={<SettingsIcon />} label="General" />
            <Tab icon={<ThemeIcon />} label="Appearance" />
            <Tab icon={<PerformanceIcon />} label="Performance" />
            <Tab icon={<NotificationsIcon />} label="Notifications" />
          </Tabs>
        </Box>

        {/* General Settings */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Default Layout</InputLabel>
                <Select
                  value={localPreferences.default_layout}
                  onChange={(e) => handlePreferenceChange('default_layout', e.target.value)}
                  label="Default Layout"
                >
                  <MenuItem value="default">Default</MenuItem>
                  <MenuItem value="compact">Compact</MenuItem>
                  <MenuItem value="detailed">Detailed</MenuItem>
                  <MenuItem value="custom">Custom</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Timezone</InputLabel>
                <Select
                  value={localPreferences.timezone}
                  onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
                  label="Timezone"
                >
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="America/New_York">Eastern Time</MenuItem>
                  <MenuItem value="America/Chicago">Central Time</MenuItem>
                  <MenuItem value="America/Denver">Mountain Time</MenuItem>
                  <MenuItem value="America/Los_Angeles">Pacific Time</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Number Format</InputLabel>
                <Select
                  value={localPreferences.number_format}
                  onChange={(e) => handlePreferenceChange('number_format', e.target.value)}
                  label="Number Format"
                >
                  <MenuItem value="US">US (1,234.56)</MenuItem>
                  <MenuItem value="EU">EU (1.234,56)</MenuItem>
                  <MenuItem value="custom">Custom</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={localPreferences.auto_refresh}
                    onChange={(e) => handlePreferenceChange('auto_refresh', e.target.checked)}
                  />
                }
                label="Auto-refresh dashboard data"
              />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Appearance Settings */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Theme</InputLabel>
                <Select
                  value={localPreferences.theme}
                  onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                  label="Theme"
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="auto">Auto (System)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={localPreferences.chart_animations}
                    onChange={(e) => handlePreferenceChange('chart_animations', e.target.checked)}
                  />
                }
                label="Enable chart animations"
              />
              <Typography variant="caption" color="text.secondary" display="block">
                Disable for better performance on slower devices
              </Typography>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Performance Settings */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Refresh Interval
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                How often to refresh dashboard data: {formatRefreshInterval(localPreferences.refresh_interval)}
              </Typography>
              <Slider
                value={localPreferences.refresh_interval}
                onChange={(_, value) => handlePreferenceChange('refresh_interval', value)}
                min={5000}
                max={300000}
                step={5000}
                marks={[
                  { value: 5000, label: '5s' },
                  { value: 30000, label: '30s' },
                  { value: 60000, label: '1m' },
                  { value: 300000, label: '5m' },
                ]}
                valueLabelDisplay="auto"
                valueLabelFormat={formatRefreshInterval}
              />
            </Grid>

            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="body2">
                  Shorter refresh intervals provide more up-to-date data but may impact performance.
                  Recommended: 30 seconds for most use cases.
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Notification Settings */}
        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Alert Notifications
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={localPreferences.notification_settings.alerts}
                    onChange={(e) => handleNestedPreferenceChange(
                      'notification_settings',
                      'alerts',
                      e.target.checked
                    )}
                  />
                }
                label="Show system alerts"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={localPreferences.notification_settings.push_notifications}
                    onChange={(e) => handleNestedPreferenceChange(
                      'notification_settings',
                      'push_notifications',
                      e.target.checked
                    )}
                  />
                }
                label="Browser push notifications"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={localPreferences.notification_settings.email_reports}
                    onChange={(e) => handleNestedPreferenceChange(
                      'notification_settings',
                      'email_reports',
                      e.target.checked
                    )}
                  />
                }
                label="Email reports"
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="caption" color="text.secondary">
                Note: Browser notifications require permission. You may need to enable them in your browser settings.
              </Typography>
            </Grid>
          </Grid>
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleReset} color="secondary">
          Reset to Defaults
        </Button>
        
        <Button onClick={onClose}>
          Cancel
        </Button>
        
        <Button onClick={handleSave} variant="contained" color="primary">
          Save Settings
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DashboardSettings;

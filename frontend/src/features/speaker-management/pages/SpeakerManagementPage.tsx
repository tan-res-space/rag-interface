/**
 * Speaker Management Page
 * 
 * Main page for speaker bucket management with search, selection,
 * statistics, and comprehensive speaker management functionality.
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  Badge,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Notifications as NotificationsIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  setViewMode,
  selectViewMode,
  selectSelectedSpeakerIds,
  selectPendingTransitions,
  getPendingTransitionRequests,
} from '../speaker-slice';
import { Speaker } from '@/domain/types/speaker';

// Components
import SpeakerSearchAndSelection from '../components/SpeakerSearchAndSelection';
import SpeakerTable from '../components/SpeakerTable';
import SpeakerStatistics from '../components/SpeakerStatistics';
import SpeakerDetailsDialog from '../components/SpeakerDetailsDialog';
import CreateSpeakerDialog from '../components/CreateSpeakerDialog';
import BulkActionsToolbar from '../components/BulkActionsToolbar';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`speaker-tabpanel-${index}`}
      aria-labelledby={`speaker-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const SpeakerManagementPage: React.FC = () => {
  const dispatch = useAppDispatch();
  
  // Redux state
  const viewMode = useAppSelector(selectViewMode);
  const selectedSpeakerIds = useAppSelector(selectSelectedSpeakerIds);
  const pendingTransitions = useAppSelector(selectPendingTransitions);
  
  // Local state
  const [currentTab, setCurrentTab] = useState(0);
  const [selectedSpeaker, setSelectedSpeaker] = useState<Speaker | null>(null);
  const [showSpeakerDetails, setShowSpeakerDetails] = useState(false);
  const [showCreateSpeaker, setShowCreateSpeaker] = useState(false);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  // Load pending transitions on mount
  React.useEffect(() => {
    dispatch(getPendingTransitionRequests());
  }, [dispatch]);

  // Tab change handler
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
    
    // Update view mode based on tab
    if (newValue === 0) {
      dispatch(setViewMode('table'));
    } else if (newValue === 1) {
      dispatch(setViewMode('analytics'));
    }
  };

  // Speaker action handlers
  const handleSpeakerView = useCallback((speaker: Speaker) => {
    setSelectedSpeaker(speaker);
    setShowSpeakerDetails(true);
  }, []);

  const handleSpeakerEdit = useCallback((speaker: Speaker) => {
    setSelectedSpeaker(speaker);
    setShowCreateSpeaker(true); // Reuse create dialog for editing
  }, []);

  const handleSpeakerAssess = useCallback((speaker: Speaker) => {
    // Navigate to assessment workflow
    setNotification({
      open: true,
      message: `Starting assessment workflow for ${speaker.speaker_name}`,
      severity: 'info',
    });
  }, []);

  const handleTransitionRequest = useCallback((speaker: Speaker) => {
    // Open transition request dialog
    setNotification({
      open: true,
      message: `Creating transition request for ${speaker.speaker_name}`,
      severity: 'info',
    });
  }, []);

  const handleViewHistory = useCallback((speaker: Speaker) => {
    // Navigate to speaker history view
    setNotification({
      open: true,
      message: `Viewing history for ${speaker.speaker_name}`,
      severity: 'info',
    });
  }, []);

  // Dialog handlers
  const handleCloseDetails = () => {
    setShowSpeakerDetails(false);
    setSelectedSpeaker(null);
  };

  const handleCloseCreate = () => {
    setShowCreateSpeaker(false);
    setSelectedSpeaker(null);
  };

  const handleSpeakerCreated = (speaker: Speaker) => {
    setNotification({
      open: true,
      message: `Speaker ${speaker.speaker_name} created successfully`,
      severity: 'success',
    });
    handleCloseCreate();
  };

  const handleNotificationClose = () => {
    setNotification({ ...notification, open: false });
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Speaker Bucket Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage speaker categorization, quality assessment, and bucket transitions
        </Typography>
      </Box>

      {/* Main Content */}
      <Box sx={{ width: '100%' }}>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={currentTab} onChange={handleTabChange} aria-label="speaker management tabs">
            <Tab 
              label="Speaker Directory" 
              id="speaker-tab-0"
              aria-controls="speaker-tabpanel-0"
            />
            <Tab 
              label="Analytics & Statistics" 
              id="speaker-tab-1"
              aria-controls="speaker-tabpanel-1"
            />
            <Tab 
              label={
                <Badge badgeContent={pendingTransitions.length} color="warning">
                  Transitions
                </Badge>
              }
              id="speaker-tab-2"
              aria-controls="speaker-tabpanel-2"
            />
          </Tabs>
        </Box>

        {/* Tab Panels */}
        
        {/* Speaker Directory Tab */}
        <TabPanel value={currentTab} index={0}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Search and Selection */}
            <SpeakerSearchAndSelection
              onSpeakerSelect={handleSpeakerView}
              multiSelect={true}
              showViewModeToggle={true}
              showQuickFilters={true}
            />

            {/* Bulk Actions Toolbar */}
            {selectedSpeakerIds.length > 0 && (
              <BulkActionsToolbar
                selectedCount={selectedSpeakerIds.length}
                onBulkAssess={() => {
                  setNotification({
                    open: true,
                    message: `Starting bulk assessment for ${selectedSpeakerIds.length} speakers`,
                    severity: 'info',
                  });
                }}
                onBulkTransition={() => {
                  setNotification({
                    open: true,
                    message: `Creating bulk transition requests for ${selectedSpeakerIds.length} speakers`,
                    severity: 'info',
                  });
                }}
                onBulkExport={() => {
                  setNotification({
                    open: true,
                    message: `Exporting ${selectedSpeakerIds.length} speakers`,
                    severity: 'info',
                  });
                }}
              />
            )}

            {/* Speaker Table */}
            <Paper elevation={1}>
              <SpeakerTable
                onSpeakerView={handleSpeakerView}
                onSpeakerEdit={handleSpeakerEdit}
                onSpeakerAssess={handleSpeakerAssess}
                onTransitionRequest={handleTransitionRequest}
                onViewHistory={handleViewHistory}
                selectable={true}
              />
            </Paper>
          </Box>
        </TabPanel>

        {/* Analytics Tab */}
        <TabPanel value={currentTab} index={1}>
          <SpeakerStatistics showRefresh={true} />
        </TabPanel>

        {/* Transitions Tab */}
        <TabPanel value={currentTab} index={2}>
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Pending Bucket Transitions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Review and manage pending speaker bucket transition requests.
            </Typography>
            
            {/* Transition requests would be displayed here */}
            <Box sx={{ mt: 3, textAlign: 'center', py: 4 }}>
              <NotificationsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                {pendingTransitions.length === 0 
                  ? 'No pending transition requests'
                  : `${pendingTransitions.length} pending transition requests`
                }
              </Typography>
            </Box>
          </Paper>
        </TabPanel>
      </Box>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add speaker"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setShowCreateSpeaker(true)}
      >
        <AddIcon />
      </Fab>

      {/* Dialogs */}
      
      {/* Speaker Details Dialog */}
      {showSpeakerDetails && selectedSpeaker && (
        <SpeakerDetailsDialog
          speaker={selectedSpeaker}
          open={showSpeakerDetails}
          onClose={handleCloseDetails}
          onEdit={() => {
            handleCloseDetails();
            handleSpeakerEdit(selectedSpeaker);
          }}
          onAssess={() => {
            handleCloseDetails();
            handleSpeakerAssess(selectedSpeaker);
          }}
        />
      )}

      {/* Create/Edit Speaker Dialog */}
      {showCreateSpeaker && (
        <CreateSpeakerDialog
          speaker={selectedSpeaker} // null for create, speaker object for edit
          open={showCreateSpeaker}
          onClose={handleCloseCreate}
          onSpeakerCreated={handleSpeakerCreated}
        />
      )}

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleNotificationClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Alert
          onClose={handleNotificationClose}
          severity={notification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default SpeakerManagementPage;

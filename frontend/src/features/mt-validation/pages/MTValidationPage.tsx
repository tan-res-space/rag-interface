/**
 * MT Validation Page
 * 
 * Main page for medical transcriptionist validation workflow
 * with session management, progress tracking, and comprehensive interface.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  Download as ExportIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  startValidationSession,
  getValidationSession,
  getValidationTestData,
  completeValidationSession,
  resetValidationState,
  selectCurrentSession,
  selectTestDataItems,
  selectSessionProgress,
  selectValidationLoading,
  selectValidationError,
  selectWorkflowState,
} from '../mt-validation-slice';
import {
  ValidationSession,
  StartValidationSessionRequest,
  SessionStatus,
} from '@/domain/types/mt-validation';

// Components
import MTValidationInterface from '../components/MTValidationInterface';
import ValidationProgress from '../components/ValidationProgress';
import SessionSetupDialog from '../components/SessionSetupDialog';
import SessionSummaryDialog from '../components/SessionSummaryDialog';

export const MTValidationPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  // Redux state
  const currentSession = useAppSelector(selectCurrentSession);
  const testDataItems = useAppSelector(selectTestDataItems);
  const sessionProgress = useAppSelector(selectSessionProgress);
  const loading = useAppSelector(selectValidationLoading);
  const error = useAppSelector(selectValidationError);
  const workflowState = useAppSelector(selectWorkflowState);
  
  // Local state
  const [showSetupDialog, setShowSetupDialog] = useState(false);
  const [showSummaryDialog, setShowSummaryDialog] = useState(false);
  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  // Initialize session
  useEffect(() => {
    if (sessionId) {
      // Load existing session
      dispatch(getValidationSession(sessionId));
      dispatch(getValidationTestData({ sessionId }));
    } else {
      // Show setup dialog for new session
      setShowSetupDialog(true);
    }

    // Cleanup on unmount
    return () => {
      dispatch(resetValidationState());
    };
  }, [dispatch, sessionId]);

  // Handle session creation
  const handleCreateSession = useCallback(async (sessionData: StartValidationSessionRequest) => {
    try {
      const session = await dispatch(startValidationSession(sessionData)).unwrap();
      await dispatch(getValidationTestData({ sessionId: session.session_id }));
      
      setShowSetupDialog(false);
      setNotification({
        open: true,
        message: `Validation session "${session.session_name}" started successfully`,
        severity: 'success',
      });
      
      // Navigate to the session URL
      navigate(`/mt-validation/${session.session_id}`);
    } catch (error: any) {
      setNotification({
        open: true,
        message: error.message || 'Failed to create validation session',
        severity: 'error',
      });
    }
  }, [dispatch, navigate]);

  // Handle session completion
  const handleCompleteSession = useCallback(async () => {
    if (!currentSession) return;

    try {
      await dispatch(completeValidationSession({
        sessionId: currentSession.session_id,
        request: {
          session_id: currentSession.session_id,
          completion_notes: 'Session completed successfully',
        },
      })).unwrap();

      setShowSummaryDialog(true);
      setNotification({
        open: true,
        message: 'Validation session completed successfully',
        severity: 'success',
      });
    } catch (error: any) {
      setNotification({
        open: true,
        message: error.message || 'Failed to complete session',
        severity: 'error',
      });
    }
  }, [dispatch, currentSession]);

  // Handle session pause
  const handlePauseSession = useCallback(() => {
    setNotification({
      open: true,
      message: 'Session paused. You can resume later.',
      severity: 'info',
    });
    navigate('/mt-validation');
  }, [navigate]);

  // Speed dial actions
  const speedDialActions = [
    {
      icon: <SettingsIcon />,
      name: 'Settings',
      onClick: () => {
        // Open settings dialog
      },
    },
    {
      icon: <AssessmentIcon />,
      name: 'Session Analytics',
      onClick: () => {
        // Open analytics dialog
      },
    },
    {
      icon: <HistoryIcon />,
      name: 'Session History',
      onClick: () => {
        navigate('/mt-validation/history');
      },
    },
    {
      icon: <ExportIcon />,
      name: 'Export Data',
      onClick: () => {
        // Export session data
      },
    },
  ];

  // Handle notification close
  const handleNotificationClose = () => {
    setNotification({ ...notification, open: false });
  };

  // Render session setup
  if (!sessionId && !currentSession) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h4" gutterBottom>
            MT Validation Workflow
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Start a new validation session to review RAG-corrected ASR drafts
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            startIcon={<StartIcon />}
            onClick={() => setShowSetupDialog(true)}
          >
            Start New Session
          </Button>
        </Box>

        {/* Session Setup Dialog */}
        <SessionSetupDialog
          open={showSetupDialog}
          onClose={() => setShowSetupDialog(false)}
          onCreateSession={handleCreateSession}
        />
      </Container>
    );
  }

  // Render loading state
  if (loading.session || loading.testData) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh',
        gap: 2
      }}>
        <LinearProgress sx={{ width: 300 }} />
        <Typography variant="body1" color="text.secondary">
          {loading.session ? 'Loading session...' : 'Loading validation data...'}
        </Typography>
      </Box>
    );
  }

  // Render error state
  if (error.session || error.testData) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error.session || error.testData}
        </Alert>
        <Button
          variant="outlined"
          onClick={() => navigate('/mt-validation')}
        >
          Back to Sessions
        </Button>
      </Container>
    );
  }

  // Render session completed state
  if (currentSession?.status === SessionStatus.COMPLETED) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Typography variant="h4" gutterBottom color="success.main">
              Session Completed!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              Validation session "{currentSession.session_name}" has been completed successfully.
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={4}>
                <Typography variant="h6" fontWeight="bold">
                  {testDataItems.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Items Reviewed
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="h6" fontWeight="bold">
                  {currentSession.duration_minutes || 0}min
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Duration
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="h6" fontWeight="bold">
                  100%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completion Rate
                </Typography>
              </Grid>
            </Grid>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="outlined"
                onClick={() => setShowSummaryDialog(true)}
              >
                View Summary
              </Button>
              <Button
                variant="contained"
                onClick={() => navigate('/mt-validation')}
              >
                Back to Sessions
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
    );
  }

  // Render main validation interface
  return (
    <Box sx={{ height: '100vh', overflow: 'hidden' }}>
      {/* Main Validation Interface */}
      {currentSession && testDataItems.length > 0 && (
        <MTValidationInterface
          sessionId={currentSession.session_id}
          onComplete={handleCompleteSession}
          onPause={handlePauseSession}
        />
      )}

      {/* Speed Dial */}
      <SpeedDial
        ariaLabel="Validation actions"
        sx={{ position: 'fixed', bottom: 16, left: 16 }}
        icon={<SpeedDialIcon />}
        onClose={() => setSpeedDialOpen(false)}
        onOpen={() => setSpeedDialOpen(true)}
        open={speedDialOpen}
        direction="up"
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={() => {
              action.onClick();
              setSpeedDialOpen(false);
            }}
          />
        ))}
      </SpeedDial>

      {/* Session Summary Dialog */}
      {showSummaryDialog && currentSession && (
        <SessionSummaryDialog
          session={currentSession}
          open={showSummaryDialog}
          onClose={() => setShowSummaryDialog(false)}
        />
      )}

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleNotificationClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
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
    </Box>
  );
};

export default MTValidationPage;

/**
 * MT Validation Interface Component
 * 
 * Main interface for medical transcriptionist validation workflow
 * with side-by-side text comparison, difference highlighting, and feedback controls.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  IconButton,
  Tooltip,
  Chip,
  LinearProgress,
  Alert,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
  Visibility as ViewIcon,
  VisibilityOff as HideIcon,
  CompareArrows as CompareIcon,
  Assessment as MetricsIcon,
  Save as SaveIcon,
  Settings as SettingsIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  KeyboardArrowUp as KeyboardArrowUpIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  selectCurrentSession,
  selectCurrentItem,
  selectCurrentItemIndex,
  selectTestDataItems,
  selectSessionProgress,
  selectComparisonMode,
  selectShowDifferences,
  selectShowSERMetrics,
  selectTextDifferences,
  selectValidationLoading,
  selectUserPreferences,
  nextItem,
  previousItem,
  setComparisonMode,
  toggleDifferences,
  toggleSERMetrics,
  calculateTextDifferences,
} from '../mt-validation-slice';

// Sub-components
import TextComparisonPanel from './TextComparisonPanel';
import SERMetricsPanel from './SERMetricsPanel';
import FeedbackPanel from './FeedbackPanel';
import ValidationProgress from './ValidationProgress';
import KeyboardShortcutsHelper from './KeyboardShortcutsHelper';

interface MTValidationInterfaceProps {
  sessionId: string;
  onComplete?: () => void;
  onPause?: () => void;
  compact?: boolean;
}

export const MTValidationInterface: React.FC<MTValidationInterfaceProps> = ({
  sessionId,
  onComplete,
  onPause,
  compact = false,
}) => {
  const dispatch = useAppDispatch();
  
  // Redux state
  const currentSession = useAppSelector(selectCurrentSession);
  const currentItem = useAppSelector(selectCurrentItem);
  const currentItemIndex = useAppSelector(selectCurrentItemIndex);
  const testDataItems = useAppSelector(selectTestDataItems);
  const sessionProgress = useAppSelector(selectSessionProgress);
  const comparisonMode = useAppSelector(selectComparisonMode);
  const showDifferences = useAppSelector(selectShowDifferences);
  const showSERMetrics = useAppSelector(selectShowSERMetrics);
  const textDifferences = useAppSelector(selectTextDifferences);
  const loading = useAppSelector(selectValidationLoading);
  const userPreferences = useAppSelector(selectUserPreferences);
  
  // Local state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);

  // Calculate text differences when current item changes
  useEffect(() => {
    if (currentItem) {
      dispatch(calculateTextDifferences({
        originalText: currentItem.original_asr_text,
        correctedText: currentItem.rag_corrected_text,
      }));
    }
  }, [dispatch, currentItem]);

  // Keyboard shortcuts
  useEffect(() => {
    if (!userPreferences.keyboard_shortcuts_enabled) return;

    const handleKeyPress = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in input fields
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (event.key) {
        case 'ArrowRight':
        case 'n':
          event.preventDefault();
          handleNextItem();
          break;
        case 'ArrowLeft':
        case 'p':
          event.preventDefault();
          handlePreviousItem();
          break;
        case 'd':
          event.preventDefault();
          dispatch(toggleDifferences());
          break;
        case 'm':
          event.preventDefault();
          dispatch(toggleSERMetrics());
          break;
        case 'f':
          event.preventDefault();
          toggleFullscreen();
          break;
        case '?':
          event.preventDefault();
          setShowKeyboardHelp(true);
          break;
        case 'Escape':
          setShowKeyboardHelp(false);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [dispatch, userPreferences.keyboard_shortcuts_enabled]);

  // Navigation handlers
  const handleNextItem = useCallback(() => {
    if (currentItemIndex < testDataItems.length - 1) {
      dispatch(nextItem());
    }
  }, [dispatch, currentItemIndex, testDataItems.length]);

  const handlePreviousItem = useCallback(() => {
    if (currentItemIndex > 0) {
      dispatch(previousItem());
    }
  }, [dispatch, currentItemIndex]);

  // UI handlers
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleComparisonModeChange = (mode: 'side-by-side' | 'unified' | 'overlay') => {
    dispatch(setComparisonMode(mode));
  };

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
      icon: showDifferences ? <HideIcon /> : <ViewIcon />,
      name: showDifferences ? 'Hide Differences' : 'Show Differences',
      onClick: () => dispatch(toggleDifferences()),
    },
    {
      icon: <MetricsIcon />,
      name: 'Toggle SER Metrics',
      onClick: () => dispatch(toggleSERMetrics()),
    },
    {
      icon: isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />,
      name: isFullscreen ? 'Exit Fullscreen' : 'Fullscreen',
      onClick: toggleFullscreen,
    },
  ];

  if (!currentSession || !currentItem) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Typography variant="h6" color="text.secondary">
          No validation session or item selected
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <Paper elevation={1} sx={{ p: 2, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Session Info */}
          <Box>
            <Typography variant="h6" component="h1">
              {currentSession.session_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Item {currentItemIndex + 1} of {testDataItems.length}
            </Typography>
          </Box>

          {/* Controls */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Comparison Mode Toggle */}
            <Tooltip title="Comparison Mode">
              <IconButton
                onClick={() => {
                  const modes: Array<'side-by-side' | 'unified' | 'overlay'> = ['side-by-side', 'unified', 'overlay'];
                  const currentIndex = modes.indexOf(comparisonMode);
                  const nextMode = modes[(currentIndex + 1) % modes.length];
                  handleComparisonModeChange(nextMode);
                }}
              >
                <CompareIcon />
              </IconButton>
            </Tooltip>

            {/* Differences Toggle */}
            <Tooltip title={showDifferences ? 'Hide Differences' : 'Show Differences'}>
              <IconButton onClick={() => dispatch(toggleDifferences())}>
                {showDifferences ? <HideIcon /> : <ViewIcon />}
              </IconButton>
            </Tooltip>

            {/* SER Metrics Toggle */}
            <Tooltip title="Toggle SER Metrics">
              <IconButton onClick={() => dispatch(toggleSERMetrics())}>
                <MetricsIcon color={showSERMetrics ? 'primary' : 'default'} />
              </IconButton>
            </Tooltip>

            {/* Navigation */}
            <Tooltip title="Previous Item (←)">
              <span>
                <IconButton
                  onClick={handlePreviousItem}
                  disabled={currentItemIndex === 0}
                >
                  <PrevIcon />
                </IconButton>
              </span>
            </Tooltip>

            <Chip
              label={`${currentItemIndex + 1} / ${testDataItems.length}`}
              size="small"
              variant="outlined"
            />

            <Tooltip title="Next Item (→)">
              <span>
                <IconButton
                  onClick={handleNextItem}
                  disabled={currentItemIndex === testDataItems.length - 1}
                >
                  <NextIcon />
                </IconButton>
              </span>
            </Tooltip>
          </Box>
        </Box>

        {/* Progress Bar */}
        <Box sx={{ mt: 1 }}>
          <ValidationProgress
            current={currentItemIndex + 1}
            total={testDataItems.length}
            progress={sessionProgress}
            compact={true}
          />
        </Box>
      </Paper>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Text Comparison Panel */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <TextComparisonPanel
            originalText={currentItem.original_asr_text}
            correctedText={currentItem.rag_corrected_text}
            referenceText={currentItem.final_reference_text}
            differences={textDifferences}
            comparisonMode={comparisonMode}
            showDifferences={showDifferences}
            loading={loading.differences}
          />
        </Box>

        {/* Side Panel */}
        <Box sx={{ width: 400, display: 'flex', flexDirection: 'column', borderLeft: 1, borderColor: 'divider' }}>
          {/* SER Metrics Panel */}
          {showSERMetrics && (
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <SERMetricsPanel
                originalMetrics={currentItem.original_ser_metrics}
                correctedMetrics={currentItem.corrected_ser_metrics}
                improvementMetrics={currentItem.improvement_metrics}
                compact={true}
              />
            </Box>
          )}

          {/* Feedback Panel */}
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            <FeedbackPanel
              sessionId={sessionId}
              currentItem={currentItem}
              onFeedbackSubmitted={handleNextItem}
              autoAdvance={userPreferences.auto_advance}
            />
          </Box>
        </Box>
      </Box>

      {/* Speed Dial */}
      <SpeedDial
        ariaLabel="Validation actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
        onClose={() => setSpeedDialOpen(false)}
        onOpen={() => setSpeedDialOpen(true)}
        open={speedDialOpen}
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

      {/* Keyboard Shortcuts Helper */}
      {showKeyboardHelp && (
        <KeyboardShortcutsHelper
          open={showKeyboardHelp}
          onClose={() => setShowKeyboardHelp(false)}
        />
      )}

      {/* Loading Overlay */}
      {loading.testData && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}
        >
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography variant="body1">Loading validation data...</Typography>
          </Paper>
        </Box>
      )}
    </Box>
  );
};

export default MTValidationInterface;

/**
 * Before/After Comparison Component
 * Side-by-side text comparison with diff highlighting and navigation
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Paper,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  NavigateBefore as PrevIcon,
  NavigateNext as NextIcon,
} from '@mui/icons-material';

// Type definitions
export interface TextChange {
  type: 'insertion' | 'deletion' | 'substitution';
  originalStart: number;
  originalEnd: number;
  correctedStart: number;
  correctedEnd: number;
  originalText: string;
  correctedText: string;
}

export interface BeforeAfterComparisonProps {
  originalText: string;
  correctedText: string;
  changes: TextChange[];
  onApprove?: () => void;
  onReject?: () => void;
  showActions?: boolean;
  highlightDifferences?: boolean;
  disabled?: boolean;
}

export const BeforeAfterComparison: React.FC<BeforeAfterComparisonProps> = ({
  originalText,
  correctedText,
  changes,
  onApprove,
  onReject,
  showActions = true,
  highlightDifferences = true,
  disabled = false,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [currentChangeIndex, setCurrentChangeIndex] = useState(0);

  // Calculate change statistics
  const changeStats = useMemo(() => {
    const stats = {
      total: changes.length,
      insertions: 0,
      deletions: 0,
      substitutions: 0,
    };

    changes.forEach(change => {
      stats[change.type + 's' as keyof typeof stats]++;
    });

    return stats;
  }, [changes]);

  // Navigate between changes
  const handlePreviousChange = useCallback(() => {
    setCurrentChangeIndex(prev => Math.max(0, prev - 1));
  }, []);

  const handleNextChange = useCallback(() => {
    setCurrentChangeIndex(prev => Math.min(changes.length - 1, prev + 1));
  }, [changes.length]);

  // Render text with highlighting
  const renderHighlightedText = useCallback((
    text: string,
    isOriginal: boolean
  ) => {
    if (!highlightDifferences || changes.length === 0) {
      return text;
    }

    const relevantChanges = changes.filter(change => {
      const start = isOriginal ? change.originalStart : change.correctedStart;
      const end = isOriginal ? change.originalEnd : change.correctedEnd;
      return start >= 0 && end <= text.length && start < end;
    });

    if (relevantChanges.length === 0) {
      return text;
    }

    // Sort changes by position
    const sortedChanges = [...relevantChanges].sort((a, b) => {
      const aStart = isOriginal ? a.originalStart : a.correctedStart;
      const bStart = isOriginal ? b.originalStart : b.correctedStart;
      return aStart - bStart;
    });

    const parts: React.ReactNode[] = [];
    let lastIndex = 0;

    sortedChanges.forEach((change, index) => {
      const start = isOriginal ? change.originalStart : change.correctedStart;
      const end = isOriginal ? change.originalEnd : change.correctedEnd;
      const changeText = isOriginal ? change.originalText : change.correctedText;

      // Validate positions
      const safeStart = Math.max(0, Math.min(start, text.length));
      const safeEnd = Math.max(safeStart, Math.min(end, text.length));

      // Add text before change
      if (safeStart > lastIndex) {
        parts.push(text.slice(lastIndex, safeStart));
      }

      // Add highlighted change
      if (changeText) {
        const isCurrent = index === currentChangeIndex;
        const changeTypeClass = `diff-${change.type}`;
        const currentClass = isCurrent ? 'diff-current' : '';
        
        parts.push(
          <Box
            key={`${isOriginal ? 'original' : 'corrected'}-${index}`}
            component="span"
            data-testid={`diff-${isOriginal ? 'original' : 'corrected'}-${index}`}
            className={`${changeTypeClass} ${currentClass}`}
            sx={{
              backgroundColor: 
                change.type === 'insertion' ? theme.palette.success.light :
                change.type === 'deletion' ? theme.palette.error.light :
                theme.palette.warning.light,
              color: 
                change.type === 'insertion' ? theme.palette.success.contrastText :
                change.type === 'deletion' ? theme.palette.error.contrastText :
                theme.palette.warning.contrastText,
              padding: '2px 4px',
              borderRadius: '4px',
              fontWeight: isCurrent ? 'bold' : 'normal',
              border: isCurrent ? `2px solid ${theme.palette.primary.main}` : 'none',
              margin: '0 1px',
            }}
          >
            {changeText}
          </Box>
        );
      }

      lastIndex = safeEnd;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts;
  }, [highlightDifferences, changes, currentChangeIndex, theme]);

  // Handle empty state
  if (!originalText && !correctedText) {
    return (
      <Box
        data-testid="comparison-container"
        sx={{ p: 3, textAlign: 'center' }}
      >
        <Typography variant="body1" color="text.secondary">
          No changes to display
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      data-testid="comparison-container"
      className={isMobile ? 'mobile-layout' : 'desktop-layout'}
      sx={{ width: '100%' }}
    >
      {/* Statistics Header */}
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
        <Typography variant="h6">
          Text Comparison
        </Typography>
        <Chip
          label={`${changeStats.total} changes`}
          size="small"
          color="primary"
        />
        {changeStats.substitutions > 0 && (
          <Chip
            label={`${changeStats.substitutions} substitutions`}
            size="small"
            variant="outlined"
          />
        )}
        {changeStats.insertions > 0 && (
          <Chip
            label={`${changeStats.insertions} insertions`}
            size="small"
            variant="outlined"
            color="success"
          />
        )}
        {changeStats.deletions > 0 && (
          <Chip
            label={`${changeStats.deletions} deletions`}
            size="small"
            variant="outlined"
            color="error"
          />
        )}
      </Box>

      {/* Change Navigation */}
      {changes.length > 1 && (
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton
            onClick={handlePreviousChange}
            disabled={currentChangeIndex === 0}
            aria-label="Previous change"
            size="small"
          >
            <PrevIcon />
          </IconButton>
          
          <Typography variant="body2">
            {currentChangeIndex + 1} of {changes.length}
          </Typography>
          
          <IconButton
            onClick={handleNextChange}
            disabled={currentChangeIndex === changes.length - 1}
            aria-label="Next change"
            size="small"
          >
            <NextIcon />
          </IconButton>
        </Box>
      )}

      {/* Comparison Content */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: isMobile ? 'column' : 'row',
          gap: 2,
          mb: showActions ? 2 : 0,
        }}
      >
        {/* Original Text */}
        <Paper
          sx={{ flex: 1, p: 2 }}
          role="region"
          aria-label="Original text"
        >
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Original Text
          </Typography>
          <Typography
            variant="body1"
            sx={{
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {renderHighlightedText(originalText, true)}
          </Typography>
        </Paper>

        {/* Corrected Text */}
        <Paper
          sx={{ flex: 1, p: 2 }}
          role="region"
          aria-label="Corrected text"
        >
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Corrected Text
          </Typography>
          <Typography
            variant="body1"
            sx={{
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {renderHighlightedText(correctedText, false)}
          </Typography>
        </Paper>
      </Box>

      {/* Action Buttons */}
      {showActions && (onApprove || onReject) && (
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          {onApprove && (
            <Button
              variant="contained"
              color="success"
              startIcon={<ApproveIcon />}
              onClick={onApprove}
              disabled={disabled}
            >
              Approve
            </Button>
          )}
          {onReject && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<RejectIcon />}
              onClick={onReject}
              disabled={disabled}
            >
              Reject
            </Button>
          )}
        </Box>
      )}

      {/* Screen Reader Announcements */}
      <Box
        role="status"
        aria-live="polite"
        sx={{ position: 'absolute', left: -10000, width: 1, height: 1, overflow: 'hidden' }}
      >
        {changes.length > 0 && `Showing change ${currentChangeIndex + 1} of ${changes.length}`}
      </Box>
    </Box>
  );
};

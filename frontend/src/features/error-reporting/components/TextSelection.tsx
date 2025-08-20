/**
 * Advanced Text Selection Component
 * Supports non-contiguous text selection with visual highlighting and touch optimization
 */

import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  IconButton,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Clear as ClearIcon,
  TouchApp as TouchIcon,
} from '@mui/icons-material';
import type { TextSelection as TextSelectionType } from '@domain/types';

export interface TextSelectionProps {
  text: string;
  onSelectionChange: (selections: TextSelectionType[]) => void;
  selections: TextSelectionType[];
  disabled?: boolean;
  maxSelections?: number;
  allowOverlapping?: boolean;
}

export const TextSelection: React.FC<TextSelectionProps> = ({
  text,
  onSelectionChange,
  selections,
  disabled = false,
  maxSelections = 10,
  allowOverlapping = false,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const containerRef = useRef<HTMLDivElement>(null);
  const [isSelecting, setIsSelecting] = useState(false);
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);

  // Generate unique selection ID
  const generateSelectionId = useCallback(() => {
    return `selection-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // Check if two selections overlap
  const selectionsOverlap = useCallback((sel1: TextSelectionType, sel2: TextSelectionType) => {
    return !(sel1.endPosition <= sel2.startPosition || sel2.endPosition <= sel1.startPosition);
  }, []);

  // Handle text selection
  const handleSelection = useCallback((event: React.MouseEvent | React.TouchEvent) => {
    if (disabled) return;

    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);
    const selectedText = selection.toString().trim();
    
    if (!selectedText) return;

    // Calculate positions relative to the text content
    const startOffset = range.startOffset;
    const endOffset = range.endOffset;
    
    // Validate selection range
    if (startOffset < 0 || endOffset > text.length || startOffset >= endOffset) {
      return;
    }

    const newSelection: TextSelectionType = {
      selectionId: generateSelectionId(),
      text: selectedText,
      startPosition: startOffset,
      endPosition: endOffset,
    };

    // Check for overlapping selections if not allowed
    if (!allowOverlapping) {
      const hasOverlap = selections.some(existing => 
        selectionsOverlap(existing, newSelection)
      );
      if (hasOverlap) {
        // Clear browser selection
        selection.removeAllRanges();
        return;
      }
    }

    // Check max selections limit
    if (selections.length >= maxSelections) {
      selection.removeAllRanges();
      return;
    }

    // Handle multiple selection (Ctrl/Cmd key)
    const isMultiSelect = (event as React.MouseEvent).ctrlKey || (event as React.MouseEvent).metaKey;
    
    let newSelections: TextSelectionType[];
    if (isMultiSelect) {
      newSelections = [...selections, newSelection];
    } else {
      newSelections = [newSelection];
    }

    onSelectionChange(newSelections);
    
    // Clear browser selection
    if (selection.removeAllRanges) {
      selection.removeAllRanges();
    }
  }, [disabled, text, selections, onSelectionChange, allowOverlapping, maxSelections, generateSelectionId, selectionsOverlap]);

  // Handle mouse events
  const handleMouseUp = useCallback((event: React.MouseEvent) => {
    if (!isSelecting) return;
    setIsSelecting(false);
    handleSelection(event);
  }, [isSelecting, handleSelection]);

  const handleMouseDown = useCallback(() => {
    if (!disabled) {
      setIsSelecting(true);
    }
  }, [disabled]);

  // Handle touch events for mobile
  const handleTouchStart = useCallback((event: React.TouchEvent) => {
    if (disabled) return;
    
    const touch = event.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY });
  }, [disabled]);

  const handleTouchEnd = useCallback((event: React.TouchEvent) => {
    if (disabled || !touchStart) return;
    
    const touch = event.changedTouches[0];
    const distance = Math.sqrt(
      Math.pow(touch.clientX - touchStart.x, 2) + 
      Math.pow(touch.clientY - touchStart.y, 2)
    );
    
    // If touch moved significantly, treat as selection
    if (distance > 10) {
      handleSelection(event);
    }
    
    setTouchStart(null);
  }, [disabled, touchStart, handleSelection]);

  // Clear all selections
  const handleClearSelections = useCallback(() => {
    onSelectionChange([]);
  }, [onSelectionChange]);

  // Remove specific selection
  const handleRemoveSelection = useCallback((selectionId: string) => {
    const newSelections = selections.filter(sel => sel.selectionId !== selectionId);
    onSelectionChange(newSelections);
  }, [selections, onSelectionChange]);

  // Render text with highlights
  const renderHighlightedText = useCallback(() => {
    if (!text || selections.length === 0) {
      return text;
    }

    // Sort selections by start position
    const sortedSelections = [...selections].sort((a, b) => a.startPosition - b.startPosition);
    
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;

    sortedSelections.forEach((selection) => {
      const { startPosition, endPosition, selectionId } = selection;
      
      // Validate positions
      const safeStart = Math.max(0, Math.min(startPosition, text.length));
      const safeEnd = Math.max(safeStart, Math.min(endPosition, text.length));
      
      // Add text before selection
      if (safeStart > lastIndex) {
        parts.push(text.slice(lastIndex, safeStart));
      }
      
      // Add highlighted selection
      parts.push(
        <Box
          key={selectionId}
          component="span"
          data-testid={`highlight-${selectionId}`}
          className="text-selection-highlight"
          sx={{
            backgroundColor: theme.palette.primary.light,
            color: theme.palette.primary.contrastText,
            padding: '2px 4px',
            borderRadius: '4px',
            cursor: 'pointer',
            position: 'relative',
            '&:hover': {
              backgroundColor: theme.palette.primary.main,
            },
          }}
          onClick={(e) => {
            e.stopPropagation();
            handleRemoveSelection(selectionId);
          }}
        >
          {text.slice(safeStart, safeEnd)}
          {isMobile && (
            <>
              <Box
                data-testid="selection-handle-start"
                sx={{
                  position: 'absolute',
                  left: -8,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: 16,
                  height: 16,
                  backgroundColor: theme.palette.primary.main,
                  borderRadius: '50%',
                  cursor: 'grab',
                }}
              />
              <Box
                data-testid="selection-handle-end"
                sx={{
                  position: 'absolute',
                  right: -8,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: 16,
                  height: 16,
                  backgroundColor: theme.palette.primary.main,
                  borderRadius: '50%',
                  cursor: 'grab',
                }}
              />
            </>
          )}
        </Box>
      );
      
      lastIndex = safeEnd;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts;
  }, [text, selections, theme, isMobile, handleRemoveSelection]);

  // Keyboard navigation support
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (disabled) return;
    
    // Handle Escape key to clear selections
    if (event.key === 'Escape') {
      handleClearSelections();
    }
  }, [disabled, handleClearSelections]);

  return (
    <Box
      data-testid="text-selection-container"
      ref={containerRef}
      className={`text-selection-container ${disabled ? 'text-selection-disabled' : ''}`}
      role="textbox"
      aria-label="Text selection area"
      tabIndex={disabled ? -1 : 0}
      onKeyDown={handleKeyDown}
      sx={{
        position: 'relative',
        padding: 2,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 1,
        backgroundColor: disabled ? theme.palette.action.disabled : theme.palette.background.paper,
        cursor: disabled ? 'not-allowed' : 'text',
        userSelect: disabled ? 'none' : 'text',
        '&:focus': {
          outline: `2px solid ${theme.palette.primary.main}`,
          outlineOffset: 2,
        },
      }}
    >
      {/* Selection Controls */}
      {selections.length > 0 && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 2,
            p: 1,
            backgroundColor: theme.palette.action.hover,
            borderRadius: 1,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            {selections.length} selection{selections.length !== 1 ? 's' : ''}
          </Typography>
          
          <IconButton
            size="small"
            onClick={handleClearSelections}
            aria-label="Clear selections"
            disabled={disabled}
          >
            <ClearIcon fontSize="small" />
          </IconButton>
        </Box>
      )}

      {/* Selectable Text */}
      <Box
        data-testid="selectable-text"
        className={isMobile ? 'touch-selectable' : ''}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        sx={{
          lineHeight: 1.6,
          fontSize: '1rem',
          fontFamily: 'inherit',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}
      >
        {renderHighlightedText()}
      </Box>

      {/* Mobile Touch Indicator */}
      {isMobile && !disabled && (
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            opacity: 0.5,
          }}
        >
          <TouchIcon fontSize="small" />
        </Box>
      )}
    </Box>
  );
};

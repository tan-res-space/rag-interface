/**
 * Text Comparison Panel Component
 * 
 * Advanced text comparison with difference highlighting,
 * multiple view modes, and interactive features.
 */

import React, { useMemo, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardHeader,
  CardContent,
  IconButton,
  Tooltip,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  Divider,
  Alert,
  Collapse,
  LinearProgress,
} from '@mui/material';
import {
  ViewColumn as SideBySideIcon,
  ViewStream as UnifiedIcon,
  Layers as OverlayIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  ContentCopy as CopyIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { TextDifference } from '@/domain/types/mt-validation';

interface TextComparisonPanelProps {
  originalText: string;
  correctedText: string;
  referenceText: string;
  differences: TextDifference[];
  comparisonMode: 'side-by-side' | 'unified' | 'overlay';
  showDifferences: boolean;
  loading?: boolean;
}

interface HighlightedTextProps {
  text: string;
  differences: TextDifference[];
  type: 'original' | 'corrected' | 'reference';
  showDifferences: boolean;
}

const HighlightedText: React.FC<HighlightedTextProps> = ({
  text,
  differences,
  type,
  showDifferences,
}) => {
  if (!showDifferences || differences.length === 0) {
    return <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>{text}</Typography>;
  }

  // Create highlighted segments
  const segments = useMemo(() => {
    const result: Array<{ text: string; type?: string; confidence?: number }> = [];
    let lastIndex = 0;

    differences.forEach((diff) => {
      // Add text before this difference
      if (diff.position.start > lastIndex) {
        result.push({
          text: text.slice(lastIndex, diff.position.start),
        });
      }

      // Add the difference
      const diffText = type === 'original' ? diff.originalText : diff.correctedText;
      if (diffText) {
        result.push({
          text: diffText,
          type: diff.type,
          confidence: diff.confidence,
        });
      }

      lastIndex = diff.position.end;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      result.push({
        text: text.slice(lastIndex),
      });
    }

    return result;
  }, [text, differences, type]);

  const getHighlightColor = (diffType: string, confidence?: number) => {
    const alpha = confidence ? Math.max(0.3, confidence) : 0.5;
    
    switch (diffType) {
      case 'insert':
        return `rgba(76, 175, 80, ${alpha})`; // Green
      case 'delete':
        return `rgba(244, 67, 54, ${alpha})`; // Red
      case 'replace':
        return `rgba(255, 152, 0, ${alpha})`; // Orange
      case 'move':
        return `rgba(156, 39, 176, ${alpha})`; // Purple
      default:
        return 'transparent';
    }
  };

  return (
    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
      {segments.map((segment, index) => (
        <span
          key={index}
          style={{
            backgroundColor: segment.type ? getHighlightColor(segment.type, segment.confidence) : 'transparent',
            padding: segment.type ? '2px 4px' : '0',
            borderRadius: segment.type ? '3px' : '0',
            border: segment.type ? '1px solid rgba(0, 0, 0, 0.1)' : 'none',
          }}
          title={segment.type ? `${segment.type} (confidence: ${(segment.confidence || 0).toFixed(2)})` : undefined}
        >
          {segment.text}
        </span>
      ))}
    </Typography>
  );
};

export const TextComparisonPanel: React.FC<TextComparisonPanelProps> = ({
  originalText,
  correctedText,
  referenceText,
  differences,
  comparisonMode,
  showDifferences,
  loading = false,
}) => {
  const [fontSize, setFontSize] = useState(14);
  const [showReference, setShowReference] = useState(true);
  const [expandedSections, setExpandedSections] = useState({
    original: true,
    corrected: true,
    reference: true,
  });

  // Statistics
  const diffStats = useMemo(() => {
    const stats = {
      insertions: 0,
      deletions: 0,
      substitutions: 0,
      moves: 0,
      total: differences.length,
    };

    differences.forEach((diff) => {
      switch (diff.type) {
        case 'insert':
          stats.insertions++;
          break;
        case 'delete':
          stats.deletions++;
          break;
        case 'replace':
          stats.substitutions++;
          break;
        case 'move':
          stats.moves++;
          break;
      }
    });

    return stats;
  }, [differences]);

  const handleCopyText = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    // Could show a snackbar notification here
  };

  const handleFontSizeChange = (delta: number) => {
    setFontSize(prev => Math.max(10, Math.min(24, prev + delta)));
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <LinearProgress sx={{ mb: 2 }} />
        <Typography variant="body2" color="text.secondary">
          Calculating text differences...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Controls */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Text Comparison</Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Font Size Controls */}
            <Tooltip title="Decrease font size">
              <IconButton size="small" onClick={() => handleFontSizeChange(-1)}>
                <ZoomOutIcon />
              </IconButton>
            </Tooltip>
            <Typography variant="caption" sx={{ minWidth: 30, textAlign: 'center' }}>
              {fontSize}px
            </Typography>
            <Tooltip title="Increase font size">
              <IconButton size="small" onClick={() => handleFontSizeChange(1)}>
                <ZoomInIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Difference Statistics */}
        {showDifferences && differences.length > 0 && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            <Chip
              label={`${diffStats.total} changes`}
              size="small"
              color="primary"
              variant="outlined"
            />
            {diffStats.insertions > 0 && (
              <Chip
                label={`${diffStats.insertions} insertions`}
                size="small"
                sx={{ backgroundColor: 'rgba(76, 175, 80, 0.1)', color: 'success.main' }}
              />
            )}
            {diffStats.deletions > 0 && (
              <Chip
                label={`${diffStats.deletions} deletions`}
                size="small"
                sx={{ backgroundColor: 'rgba(244, 67, 54, 0.1)', color: 'error.main' }}
              />
            )}
            {diffStats.substitutions > 0 && (
              <Chip
                label={`${diffStats.substitutions} substitutions`}
                size="small"
                sx={{ backgroundColor: 'rgba(255, 152, 0, 0.1)', color: 'warning.main' }}
              />
            )}
            {diffStats.moves > 0 && (
              <Chip
                label={`${diffStats.moves} moves`}
                size="small"
                sx={{ backgroundColor: 'rgba(156, 39, 176, 0.1)', color: 'secondary.main' }}
              />
            )}
          </Box>
        )}
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {comparisonMode === 'side-by-side' && (
          <Grid container spacing={2} sx={{ height: '100%' }}>
            {/* Original Text */}
            <Grid item xs={6}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardHeader
                  title="Original ASR"
                  action={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Tooltip title="Copy text">
                        <IconButton size="small" onClick={() => handleCopyText(originalText, 'Original')}>
                          <CopyIcon />
                        </IconButton>
                      </Tooltip>
                      <IconButton size="small" onClick={() => toggleSection('original')}>
                        {expandedSections.original ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                  sx={{ pb: 1 }}
                />
                <Collapse in={expandedSections.original}>
                  <CardContent sx={{ flex: 1, overflow: 'auto', fontSize }}>
                    <HighlightedText
                      text={originalText}
                      differences={differences}
                      type="original"
                      showDifferences={showDifferences}
                    />
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>

            {/* Corrected Text */}
            <Grid item xs={6}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardHeader
                  title="RAG Corrected"
                  action={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Tooltip title="Copy text">
                        <IconButton size="small" onClick={() => handleCopyText(correctedText, 'Corrected')}>
                          <CopyIcon />
                        </IconButton>
                      </Tooltip>
                      <IconButton size="small" onClick={() => toggleSection('corrected')}>
                        {expandedSections.corrected ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                  sx={{ pb: 1 }}
                />
                <Collapse in={expandedSections.corrected}>
                  <CardContent sx={{ flex: 1, overflow: 'auto', fontSize }}>
                    <HighlightedText
                      text={correctedText}
                      differences={differences}
                      type="corrected"
                      showDifferences={showDifferences}
                    />
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>

            {/* Reference Text */}
            {showReference && (
              <Grid item xs={12}>
                <Card>
                  <CardHeader
                    title="Final Reference"
                    action={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Tooltip title="Copy text">
                          <IconButton size="small" onClick={() => handleCopyText(referenceText, 'Reference')}>
                            <CopyIcon />
                          </IconButton>
                        </Tooltip>
                        <IconButton size="small" onClick={() => toggleSection('reference')}>
                          {expandedSections.reference ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </Box>
                    }
                    sx={{ pb: 1 }}
                  />
                  <Collapse in={expandedSections.reference}>
                    <CardContent sx={{ fontSize }}>
                      <HighlightedText
                        text={referenceText}
                        differences={differences}
                        type="reference"
                        showDifferences={showDifferences}
                      />
                    </CardContent>
                  </Collapse>
                </Card>
              </Grid>
            )}
          </Grid>
        )}

        {comparisonMode === 'unified' && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Unified view with all texts in sequence */}
            <Card>
              <CardHeader title="Original ASR" />
              <CardContent sx={{ fontSize }}>
                <HighlightedText
                  text={originalText}
                  differences={differences}
                  type="original"
                  showDifferences={showDifferences}
                />
              </CardContent>
            </Card>

            <Divider>
              <Chip label="RAG Correction" size="small" />
            </Divider>

            <Card>
              <CardHeader title="RAG Corrected" />
              <CardContent sx={{ fontSize }}>
                <HighlightedText
                  text={correctedText}
                  differences={differences}
                  type="corrected"
                  showDifferences={showDifferences}
                />
              </CardContent>
            </Card>

            <Divider>
              <Chip label="Final Reference" size="small" />
            </Divider>

            <Card>
              <CardHeader title="Final Reference" />
              <CardContent sx={{ fontSize }}>
                <HighlightedText
                  text={referenceText}
                  differences={differences}
                  type="reference"
                  showDifferences={showDifferences}
                />
              </CardContent>
            </Card>
          </Box>
        )}

        {comparisonMode === 'overlay' && (
          <Card sx={{ height: '100%' }}>
            <CardHeader title="Overlay Comparison" />
            <CardContent sx={{ height: '100%', overflow: 'auto', fontSize }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                Overlay mode shows corrections inline with the original text.
              </Alert>
              {/* This would implement an overlay view with inline corrections */}
              <HighlightedText
                text={correctedText}
                differences={differences}
                type="corrected"
                showDifferences={showDifferences}
              />
            </CardContent>
          </Card>
        )}
      </Box>
    </Box>
  );
};

export default TextComparisonPanel;

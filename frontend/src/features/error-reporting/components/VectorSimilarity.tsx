/**
 * Vector Similarity Analysis Component
 * Displays real-time similarity search results and pattern recognition
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Collapse,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ContentCopy as CopyIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
  AutoAwesome as AIIcon,
} from '@mui/icons-material';
import type { SimilarityResult, ErrorPattern } from '@domain/types';

export interface VectorSimilarityProps {
  similarityResults: SimilarityResult[];
  isLoading?: boolean;
  threshold?: number;
  onThresholdChange?: (threshold: number) => void;
  onPatternSelect?: (pattern: SimilarityResult) => void;
  disabled?: boolean;
  showPatternAnalysis?: boolean;
  maxResults?: number;
}

interface PatternGroup {
  category: string;
  patterns: SimilarityResult[];
  averageConfidence: number;
}

export const VectorSimilarity: React.FC<VectorSimilarityProps> = ({
  similarityResults,
  isLoading = false,
  threshold = 0.8,
  onThresholdChange,
  onPatternSelect,
  disabled = false,
  showPatternAnalysis = true,
  maxResults = 10,
}) => {
  const theme = useTheme();
  const [expandedGroups, setExpandedGroups] = useState<string[]>([]);
  const [copiedPatternId, setCopiedPatternId] = useState<string | null>(null);

  // Filter and sort results by confidence
  const filteredResults = useMemo(() => {
    return similarityResults
      .filter(result => result.confidence >= threshold)
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, maxResults);
  }, [similarityResults, threshold, maxResults]);

  // Group patterns by category
  const patternGroups = useMemo(() => {
    const groups: { [key: string]: SimilarityResult[] } = {};
    
    filteredResults.forEach(result => {
      const category = result.category || 'General';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(result);
    });

    return Object.entries(groups).map(([category, patterns]) => ({
      category,
      patterns,
      averageConfidence: patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length,
    })).sort((a, b) => b.averageConfidence - a.averageConfidence);
  }, [filteredResults]);

  // Handle group expansion
  const handleGroupToggle = useCallback((category: string) => {
    setExpandedGroups(prev => 
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  }, []);

  // Handle pattern copy
  const handleCopyPattern = useCallback(async (pattern: SimilarityResult) => {
    try {
      await navigator.clipboard.writeText(pattern.suggestedCorrection);
      setCopiedPatternId(pattern.patternId);
      setTimeout(() => setCopiedPatternId(null), 2000);
    } catch (error) {
      console.error('Failed to copy pattern:', error);
    }
  }, []);

  // Handle pattern selection
  const handlePatternSelect = useCallback((pattern: SimilarityResult) => {
    if (onPatternSelect && !disabled) {
      onPatternSelect(pattern);
    }
  }, [onPatternSelect, disabled]);

  // Get confidence color
  const getConfidenceColor = useCallback((confidence: number) => {
    if (confidence >= 0.9) return theme.palette.success.main;
    if (confidence >= 0.8) return theme.palette.warning.main;
    return theme.palette.error.main;
  }, [theme]);

  // Get confidence label
  const getConfidenceLabel = useCallback((confidence: number) => {
    if (confidence >= 0.95) return 'Very High';
    if (confidence >= 0.9) return 'High';
    if (confidence >= 0.8) return 'Medium';
    if (confidence >= 0.7) return 'Low';
    return 'Very Low';
  }, []);

  // Render pattern item
  const renderPatternItem = useCallback((pattern: SimilarityResult, index: number) => {
    const isCopied = copiedPatternId === pattern.patternId;
    
    return (
      <ListItem
        key={pattern.patternId}
        divider={index < filteredResults.length - 1}
        sx={{
          cursor: onPatternSelect ? 'pointer' : 'default',
          '&:hover': onPatternSelect ? {
            backgroundColor: theme.palette.action.hover,
          } : {},
        }}
        onClick={() => handlePatternSelect(pattern)}
      >
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                {pattern.suggestedCorrection}
              </Typography>
              <Chip
                label={`${Math.round(pattern.confidence * 100)}%`}
                size="small"
                sx={{
                  backgroundColor: getConfidenceColor(pattern.confidence),
                  color: 'white',
                  fontWeight: 'bold',
                }}
              />
            </Box>
          }
          secondary={
            <Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Original: {pattern.similarText}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Confidence: {getConfidenceLabel(pattern.confidence)}
                </Typography>
                {pattern.frequency > 1 && (
                  <Chip
                    label={`${pattern.frequency} occurrences`}
                    size="small"
                    variant="outlined"
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                )}
                {pattern.speakerIds && pattern.speakerIds.length > 0 && (
                  <Chip
                    label={`${pattern.speakerIds.length} speakers`}
                    size="small"
                    variant="outlined"
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                )}
              </Box>
            </Box>
          }
        />
        <ListItemSecondaryAction>
          <Tooltip title={isCopied ? "Copied!" : "Copy correction"}>
            <IconButton
              edge="end"
              onClick={(e) => {
                e.stopPropagation();
                handleCopyPattern(pattern);
              }}
              disabled={disabled}
              size="small"
            >
              {isCopied ? <CheckIcon color="success" /> : <CopyIcon />}
            </IconButton>
          </Tooltip>
        </ListItemSecondaryAction>
      </ListItem>
    );
  }, [
    filteredResults.length,
    copiedPatternId,
    onPatternSelect,
    theme,
    handlePatternSelect,
    getConfidenceColor,
    getConfidenceLabel,
    handleCopyPattern,
    disabled,
  ]);

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <AIIcon color="primary" />
            <Typography variant="h6">Analyzing Patterns...</Typography>
          </Box>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Searching for similar error patterns in the database...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (filteredResults.length === 0) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <InfoIcon color="info" />
            <Typography variant="h6">No Similar Patterns Found</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            No similar error patterns were found in the database with confidence above {Math.round(threshold * 100)}%.
            This might be a unique error pattern.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <TrendingUpIcon color="primary" />
          <Typography variant="h6">Similar Error Patterns</Typography>
          <Chip
            label={`${filteredResults.length} found`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>

        {/* Pattern Analysis Summary */}
        {showPatternAnalysis && patternGroups.length > 1 && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Found patterns across {patternGroups.length} categories. 
              Highest confidence category: <strong>{patternGroups[0].category}</strong> 
              ({Math.round(patternGroups[0].averageConfidence * 100)}% avg confidence)
            </Typography>
          </Alert>
        )}

        {/* Grouped Results */}
        {showPatternAnalysis && patternGroups.length > 1 ? (
          <Box>
            {patternGroups.map((group) => (
              <Box key={group.category} sx={{ mb: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    p: 1,
                    borderRadius: 1,
                    backgroundColor: theme.palette.action.hover,
                  }}
                  onClick={() => handleGroupToggle(group.category)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2">{group.category}</Typography>
                    <Chip
                      label={`${group.patterns.length} patterns`}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={`${Math.round(group.averageConfidence * 100)}% avg`}
                      size="small"
                      sx={{
                        backgroundColor: getConfidenceColor(group.averageConfidence),
                        color: 'white',
                      }}
                    />
                  </Box>
                  <IconButton size="small">
                    {expandedGroups.includes(group.category) ? (
                      <ExpandLessIcon />
                    ) : (
                      <ExpandMoreIcon />
                    )}
                  </IconButton>
                </Box>
                
                <Collapse in={expandedGroups.includes(group.category)}>
                  <List dense>
                    {group.patterns.map((pattern, index) => 
                      renderPatternItem(pattern, index)
                    )}
                  </List>
                </Collapse>
              </Box>
            ))}
          </Box>
        ) : (
          // Flat Results
          <List dense>
            {filteredResults.map((pattern, index) => 
              renderPatternItem(pattern, index)
            )}
          </List>
        )}

        {/* Footer Information */}
        <Divider sx={{ my: 2 }} />
        <Typography variant="caption" color="text.secondary">
          Showing top {filteredResults.length} patterns with confidence ≥ {Math.round(threshold * 100)}%.
          {onPatternSelect && ' Click a pattern to use its correction.'}
        </Typography>
      </CardContent>
    </Card>
  );
};

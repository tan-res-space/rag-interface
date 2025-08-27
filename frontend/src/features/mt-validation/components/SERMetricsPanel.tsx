/**
 * SER Metrics Panel Component
 * 
 * Displays SER metrics comparison with visual indicators
 * and improvement analysis for MT validation.
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Divider,
  Tooltip,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  TrendingUp as ImprovementIcon,
  TrendingDown as DegradationIcon,
  TrendingFlat as NoChangeIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { SERMetrics, SERComparison } from '@/domain/types/mt-validation';

interface SERMetricsPanelProps {
  originalMetrics: SERMetrics;
  correctedMetrics: SERMetrics;
  improvementMetrics: SERComparison;
  compact?: boolean;
}

interface MetricDisplayProps {
  label: string;
  value: number;
  unit?: string;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  showProgress?: boolean;
  maxValue?: number;
  tooltip?: string;
}

const MetricDisplay: React.FC<MetricDisplayProps> = ({
  label,
  value,
  unit = '',
  color = 'primary',
  showProgress = false,
  maxValue = 100,
  tooltip,
}) => {
  const displayValue = typeof value === 'number' ? value.toFixed(1) : value;
  
  return (
    <Box sx={{ mb: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
        <Typography variant="body2" color="text.secondary">
          {label}
          {tooltip && (
            <Tooltip title={tooltip}>
              <InfoIcon sx={{ fontSize: 14, ml: 0.5, color: 'text.disabled' }} />
            </Tooltip>
          )}
        </Typography>
        <Typography variant="body2" fontWeight="medium">
          {displayValue}{unit}
        </Typography>
      </Box>
      {showProgress && (
        <LinearProgress
          variant="determinate"
          value={Math.min((value / maxValue) * 100, 100)}
          color={color}
          sx={{ height: 6, borderRadius: 3 }}
        />
      )}
    </Box>
  );
};

export const SERMetricsPanel: React.FC<SERMetricsPanelProps> = ({
  originalMetrics,
  correctedMetrics,
  improvementMetrics,
  compact = false,
}) => {
  const [expanded, setExpanded] = React.useState(!compact);

  const getQualityColor = (qualityLevel: string): 'success' | 'warning' | 'error' => {
    switch (qualityLevel) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'error';
      default: return 'warning';
    }
  };

  const getImprovementIcon = (improvement: number) => {
    if (improvement > 5) return <ImprovementIcon color="success" />;
    if (improvement < -5) return <DegradationIcon color="error" />;
    return <NoChangeIcon color="info" />;
  };

  const getImprovementColor = (improvement: number): 'success' | 'error' | 'info' => {
    if (improvement > 5) return 'success';
    if (improvement < -5) return 'error';
    return 'info';
  };

  return (
    <Paper elevation={1} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">SER Metrics</Typography>
          {compact && (
            <IconButton size="small" onClick={() => setExpanded(!expanded)}>
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          )}
        </Box>
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ p: 2, flex: 1, overflow: 'auto' }}>
          {/* Improvement Summary */}
          <Card variant="outlined" sx={{ mb: 2, backgroundColor: 'background.default' }}>
            <CardContent sx={{ py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  Overall Improvement
                </Typography>
                {getImprovementIcon(improvementMetrics.improvement)}
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h4" fontWeight="bold" color={`${getImprovementColor(improvementMetrics.improvement)}.main`}>
                  {improvementMetrics.improvement > 0 ? '+' : ''}{improvementMetrics.improvement.toFixed(1)}%
                </Typography>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {improvementMetrics.improvement_percentage.toFixed(1)}% relative improvement
                  </Typography>
                  <Chip
                    label={improvementMetrics.is_significant_improvement ? 'Significant' : 'Minor'}
                    size="small"
                    color={improvementMetrics.is_significant_improvement ? 'success' : 'default'}
                    variant="outlined"
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Detailed Metrics Comparison */}
          <Grid container spacing={2}>
            {/* Original Metrics */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                    Original ASR
                  </Typography>
                  
                  <MetricDisplay
                    label="SER Score"
                    value={originalMetrics.ser_score}
                    unit="%"
                    color="error"
                    showProgress
                    tooltip="Sentence Error Rate - lower is better"
                  />
                  
                  <MetricDisplay
                    label="Edit Distance"
                    value={originalMetrics.edit_distance}
                    tooltip="Total number of edits required"
                  />
                  
                  <MetricDisplay
                    label="Insertions"
                    value={originalMetrics.insertions}
                    color="info"
                    tooltip="Number of words that need to be inserted"
                  />
                  
                  <MetricDisplay
                    label="Deletions"
                    value={originalMetrics.deletions}
                    color="warning"
                    tooltip="Number of words that need to be deleted"
                  />
                  
                  <MetricDisplay
                    label="Substitutions"
                    value={originalMetrics.substitutions}
                    color="secondary"
                    tooltip="Number of words that need to be replaced"
                  />
                  
                  <MetricDisplay
                    label="Moves"
                    value={originalMetrics.moves}
                    color="primary"
                    tooltip="Number of words that need to be moved"
                  />
                  
                  <Box sx={{ mt: 2 }}>
                    <Chip
                      label={`${originalMetrics.quality_level.toUpperCase()} Quality`}
                      color={getQualityColor(originalMetrics.quality_level)}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Corrected Metrics */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                    RAG Corrected
                  </Typography>
                  
                  <MetricDisplay
                    label="SER Score"
                    value={correctedMetrics.ser_score}
                    unit="%"
                    color={correctedMetrics.ser_score < originalMetrics.ser_score ? 'success' : 'error'}
                    showProgress
                    tooltip="Sentence Error Rate - lower is better"
                  />
                  
                  <MetricDisplay
                    label="Edit Distance"
                    value={correctedMetrics.edit_distance}
                    tooltip="Total number of edits required"
                  />
                  
                  <MetricDisplay
                    label="Insertions"
                    value={correctedMetrics.insertions}
                    color="info"
                    tooltip="Number of words that need to be inserted"
                  />
                  
                  <MetricDisplay
                    label="Deletions"
                    value={correctedMetrics.deletions}
                    color="warning"
                    tooltip="Number of words that need to be deleted"
                  />
                  
                  <MetricDisplay
                    label="Substitutions"
                    value={correctedMetrics.substitutions}
                    color="secondary"
                    tooltip="Number of words that need to be replaced"
                  />
                  
                  <MetricDisplay
                    label="Moves"
                    value={correctedMetrics.moves}
                    color="primary"
                    tooltip="Number of words that need to be moved"
                  />
                  
                  <Box sx={{ mt: 2 }}>
                    <Chip
                      label={`${correctedMetrics.quality_level.toUpperCase()} Quality`}
                      color={getQualityColor(correctedMetrics.quality_level)}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Quality Assessment */}
          <Card variant="outlined" sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                Quality Assessment
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Original Quality
                    </Typography>
                    <Chip
                      label={originalMetrics.is_acceptable_quality ? 'Acceptable' : 'Needs Work'}
                      color={originalMetrics.is_acceptable_quality ? 'success' : 'error'}
                      variant="outlined"
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Corrected Quality
                    </Typography>
                    <Chip
                      label={correctedMetrics.is_acceptable_quality ? 'Acceptable' : 'Needs Work'}
                      color={correctedMetrics.is_acceptable_quality ? 'success' : 'error'}
                      variant="outlined"
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Improvement Details */}
          {!compact && (
            <Card variant="outlined" sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  Improvement Analysis
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Absolute Improvement:</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {improvementMetrics.improvement > 0 ? '+' : ''}{improvementMetrics.improvement.toFixed(2)}%
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Relative Improvement:</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {improvementMetrics.improvement_percentage.toFixed(2)}%
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Significance:</Typography>
                    <Chip
                      label={improvementMetrics.is_significant_improvement ? 'Significant' : 'Not Significant'}
                      size="small"
                      color={improvementMetrics.is_significant_improvement ? 'success' : 'default'}
                      variant="outlined"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default SERMetricsPanel;

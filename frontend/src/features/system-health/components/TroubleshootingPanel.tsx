/**
 * Troubleshooting Panel Component
 * Displays troubleshooting suggestions and common solutions
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Alert,
  Link,
} from '@mui/material';
import {
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  Error as CriticalIcon,
  Warning as HighIcon,
  Info as MediumIcon,
  CheckCircle as LowIcon,
  BugReport as IssueIcon,
  Build as SolutionIcon,
  Help as CauseIcon,
  Description as DocsIcon,
} from '@mui/icons-material';
import type { TroubleshootingPanelProps, TroubleshootingSuggestion } from '../types/health-types';

const TroubleshootingPanel: React.FC<TroubleshootingPanelProps> = ({
  suggestions,
  service,
  onClose,
}) => {
  const [expandedSuggestion, setExpandedSuggestion] = useState<string | false>(false);

  const getSeverityIcon = (severity: TroubleshootingSuggestion['severity']) => {
    switch (severity) {
      case 'critical':
        return <CriticalIcon color="error" />;
      case 'high':
        return <HighIcon color="warning" />;
      case 'medium':
        return <MediumIcon color="info" />;
      case 'low':
        return <LowIcon color="success" />;
      default:
        return <IssueIcon color="disabled" />;
    }
  };

  const getSeverityColor = (severity: TroubleshootingSuggestion['severity']) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getSeverityText = (severity: TroubleshootingSuggestion['severity']) => {
    return severity.charAt(0).toUpperCase() + severity.slice(1);
  };

  const handleAccordionChange = (suggestionId: string) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpandedSuggestion(isExpanded ? suggestionId : false);
  };

  const sortedSuggestions = [...suggestions].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });

  return (
    <Dialog
      open={true}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh', maxHeight: '90vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Troubleshooting{service ? `: ${service}` : ''}
          </Typography>
          
          <Tooltip title="Close">
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </DialogTitle>

      <DialogContent>
        {suggestions.length === 0 ? (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              No Issues Detected
            </Typography>
            <Typography>
              All services are operating normally. No troubleshooting suggestions are available at this time.
            </Typography>
          </Alert>
        ) : (
          <>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Found {suggestions.length} issue{suggestions.length !== 1 ? 's' : ''} that may require attention. 
                Expand each item below for detailed troubleshooting steps.
              </Typography>
            </Alert>

            <Box>
              {sortedSuggestions.map((suggestion, index) => (
                <Accordion
                  key={`${suggestion.issue}-${index}`}
                  expanded={expandedSuggestion === `${suggestion.issue}-${index}`}
                  onChange={handleAccordionChange(`${suggestion.issue}-${index}`)}
                  sx={{ 
                    mb: 1,
                    border: suggestion.severity === 'critical' ? 2 : 1,
                    borderColor: suggestion.severity === 'critical' ? 'error.main' : 'divider',
                  }}
                >
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    sx={{
                      backgroundColor: suggestion.severity === 'critical' ? 'error.light' : 
                                     suggestion.severity === 'high' ? 'warning.light' : 'transparent',
                      '&.Mui-expanded': {
                        backgroundColor: suggestion.severity === 'critical' ? 'error.light' : 
                                       suggestion.severity === 'high' ? 'warning.light' : 'action.hover',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      {getSeverityIcon(suggestion.severity)}
                      
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {suggestion.issue}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {suggestion.description}
                        </Typography>
                      </Box>
                      
                      <Chip
                        label={getSeverityText(suggestion.severity)}
                        color={getSeverityColor(suggestion.severity) as any}
                        size="small"
                        variant="filled"
                      />
                    </Box>
                  </AccordionSummary>

                  <AccordionDetails>
                    <Box sx={{ space: 3 }}>
                      {/* Possible Causes */}
                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <CauseIcon color="primary" />
                          <Typography variant="h6">Possible Causes</Typography>
                        </Box>
                        
                        <List dense>
                          {suggestion.possible_causes.map((cause, causeIndex) => (
                            <ListItem key={causeIndex}>
                              <ListItemIcon>
                                <Box
                                  sx={{
                                    width: 8,
                                    height: 8,
                                    borderRadius: '50%',
                                    backgroundColor: 'text.secondary',
                                  }}
                                />
                              </ListItemIcon>
                              <ListItemText primary={cause} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>

                      {/* Suggested Actions */}
                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <SolutionIcon color="primary" />
                          <Typography variant="h6">Suggested Actions</Typography>
                        </Box>
                        
                        <List dense>
                          {suggestion.suggested_actions.map((action, actionIndex) => (
                            <ListItem key={actionIndex}>
                              <ListItemIcon>
                                <Typography variant="body2" color="primary" fontWeight="bold">
                                  {actionIndex + 1}.
                                </Typography>
                              </ListItemIcon>
                              <ListItemText primary={action} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>

                      {/* Documentation Links */}
                      {suggestion.documentation_links && suggestion.documentation_links.length > 0 && (
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <DocsIcon color="primary" />
                            <Typography variant="h6">Documentation</Typography>
                          </Box>
                          
                          <List dense>
                            {suggestion.documentation_links.map((link, linkIndex) => (
                              <ListItem key={linkIndex}>
                                <ListItemIcon>
                                  <DocsIcon fontSize="small" color="action" />
                                </ListItemIcon>
                                <ListItemText
                                  primary={
                                    <Link
                                      href={link}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      color="primary"
                                    >
                                      {link.split('/').pop() || link}
                                    </Link>
                                  }
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>

            {/* General Troubleshooting Tips */}
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                General Troubleshooting Tips
              </Typography>
              
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  <strong>Before making changes:</strong>
                </Typography>
                <List dense>
                  <ListItem sx={{ py: 0 }}>
                    <ListItemText primary="• Check service logs for detailed error messages" />
                  </ListItem>
                  <ListItem sx={{ py: 0 }}>
                    <ListItemText primary="• Verify system resources (CPU, memory, disk space)" />
                  </ListItem>
                  <ListItem sx={{ py: 0 }}>
                    <ListItemText primary="• Test connectivity from different locations" />
                  </ListItem>
                  <ListItem sx={{ py: 0 }}>
                    <ListItemText primary="• Document any changes made for rollback purposes" />
                  </ListItem>
                </List>
              </Alert>

              <Alert severity="warning">
                <Typography variant="body2">
                  <strong>Need additional help?</strong> Contact your system administrator or 
                  check the comprehensive troubleshooting guide in the documentation.
                </Typography>
              </Alert>
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TroubleshootingPanel;

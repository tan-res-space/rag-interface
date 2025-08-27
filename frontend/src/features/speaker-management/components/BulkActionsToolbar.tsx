/**
 * Bulk Actions Toolbar Component
 * 
 * Toolbar for performing bulk operations on selected speakers
 * including assessment, transition requests, and export.
 */

import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  Button,
  IconButton,
  Tooltip,
  Divider,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Alert,
  Collapse,
} from '@mui/material';
import {
  Close as CloseIcon,
  Assessment as AssessmentIcon,
  SwapHoriz as TransitionIcon,
  FileDownload as ExportIcon,
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import { clearSelection, selectSelectedSpeakerIds } from '../speaker-slice';

interface BulkActionsToolbarProps {
  selectedCount: number;
  onBulkAssess?: () => void;
  onBulkTransition?: () => void;
  onBulkExport?: () => void;
  onBulkEdit?: () => void;
  onBulkDelete?: () => void;
  onBulkRefresh?: () => void;
  showAdvancedActions?: boolean;
}

export const BulkActionsToolbar: React.FC<BulkActionsToolbarProps> = ({
  selectedCount,
  onBulkAssess,
  onBulkTransition,
  onBulkExport,
  onBulkEdit,
  onBulkDelete,
  onBulkRefresh,
  showAdvancedActions = false,
}) => {
  const dispatch = useAppDispatch();
  const selectedSpeakerIds = useAppSelector(selectSelectedSpeakerIds);
  
  // Local state
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [showDetails, setShowDetails] = useState(false);
  
  const menuOpen = Boolean(anchorEl);

  // Handle menu open/close
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle clear selection
  const handleClearSelection = () => {
    dispatch(clearSelection());
  };

  // Handle menu item clicks
  const handleMenuItemClick = (action: () => void) => {
    action();
    handleMenuClose();
  };

  if (selectedCount === 0) {
    return null;
  }

  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 2, 
        backgroundColor: 'primary.50',
        border: '1px solid',
        borderColor: 'primary.200',
      }}
    >
      {/* Main Toolbar */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Selection Info */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            label={`${selectedCount} selected`}
            color="primary"
            variant="filled"
            size="small"
          />
          
          <Typography variant="body2" color="text.secondary">
            Bulk actions available for selected speakers
          </Typography>
          
          {selectedCount > 10 && (
            <Button
              size="small"
              startIcon={showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              onClick={() => setShowDetails(!showDetails)}
              variant="text"
            >
              {showDetails ? 'Hide' : 'Show'} Details
            </Button>
          )}
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Primary Actions */}
          {onBulkAssess && (
            <Button
              startIcon={<AssessmentIcon />}
              onClick={onBulkAssess}
              variant="contained"
              size="small"
              color="primary"
            >
              Assess All
            </Button>
          )}

          {onBulkTransition && (
            <Button
              startIcon={<TransitionIcon />}
              onClick={onBulkTransition}
              variant="outlined"
              size="small"
            >
              Request Transitions
            </Button>
          )}

          {onBulkExport && (
            <Button
              startIcon={<ExportIcon />}
              onClick={onBulkExport}
              variant="outlined"
              size="small"
            >
              Export
            </Button>
          )}

          {/* More Actions Menu */}
          {showAdvancedActions && (
            <>
              <Tooltip title="More Actions">
                <IconButton
                  size="small"
                  onClick={handleMenuOpen}
                  aria-label="more actions"
                  aria-controls={menuOpen ? 'bulk-actions-menu' : undefined}
                  aria-haspopup="true"
                  aria-expanded={menuOpen ? 'true' : undefined}
                >
                  <MoreVertIcon />
                </IconButton>
              </Tooltip>

              <Menu
                id="bulk-actions-menu"
                anchorEl={anchorEl}
                open={menuOpen}
                onClose={handleMenuClose}
                MenuListProps={{
                  'aria-labelledby': 'bulk-actions-button',
                }}
              >
                {onBulkEdit && (
                  <MenuItem onClick={() => handleMenuItemClick(onBulkEdit)}>
                    <ListItemIcon>
                      <EditIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Bulk Edit</ListItemText>
                  </MenuItem>
                )}

                {onBulkRefresh && (
                  <MenuItem onClick={() => handleMenuItemClick(onBulkRefresh)}>
                    <ListItemIcon>
                      <RefreshIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Refresh Statistics</ListItemText>
                  </MenuItem>
                )}

                <Divider />

                {onBulkDelete && (
                  <MenuItem 
                    onClick={() => handleMenuItemClick(onBulkDelete)}
                    sx={{ color: 'error.main' }}
                  >
                    <ListItemIcon>
                      <DeleteIcon fontSize="small" color="error" />
                    </ListItemIcon>
                    <ListItemText>Delete Selected</ListItemText>
                  </MenuItem>
                )}
              </Menu>
            </>
          )}

          {/* Clear Selection */}
          <Tooltip title="Clear Selection">
            <IconButton
              size="small"
              onClick={handleClearSelection}
              aria-label="clear selection"
            >
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Detailed Selection Info */}
      <Collapse in={showDetails}>
        <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Selected Speaker IDs:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, maxHeight: 100, overflow: 'auto' }}>
            {selectedSpeakerIds.slice(0, 20).map((id) => (
              <Chip
                key={id}
                label={id.slice(-8)} // Show last 8 characters of ID
                size="small"
                variant="outlined"
              />
            ))}
            {selectedSpeakerIds.length > 20 && (
              <Chip
                label={`+${selectedSpeakerIds.length - 20} more`}
                size="small"
                variant="outlined"
                color="secondary"
              />
            )}
          </Box>
        </Box>
      </Collapse>

      {/* Warning for Large Selections */}
      {selectedCount > 50 && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          <Typography variant="body2">
            You have selected {selectedCount} speakers. Bulk operations on large selections may take some time to complete.
          </Typography>
        </Alert>
      )}

      {/* Info for Assessment */}
      {selectedCount > 0 && onBulkAssess && (
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            Bulk assessment will start quality evaluation workflows for all selected speakers. 
            This process may take several minutes depending on the number of speakers and available data.
          </Typography>
        </Alert>
      )}
    </Paper>
  );
};

export default BulkActionsToolbar;

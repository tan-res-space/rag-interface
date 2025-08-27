/**
 * Keyboard Shortcuts Helper Component
 * 
 * Modal dialog displaying available keyboard shortcuts
 * for efficient MT validation workflow.
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Chip,
  Divider,
  IconButton,
  Card,
  CardContent,
} from '@mui/material';
import {
  Close as CloseIcon,
  Keyboard as KeyboardIcon,
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
  Visibility as ViewIcon,
  Assessment as MetricsIcon,
  Fullscreen as FullscreenIcon,
  Save as SaveIcon,
  Help as HelpIcon,
} from '@mui/icons-material';

interface KeyboardShortcutsHelperProps {
  open: boolean;
  onClose: () => void;
}

interface ShortcutItem {
  keys: string[];
  description: string;
  icon?: React.ReactNode;
  category: string;
}

const shortcuts: ShortcutItem[] = [
  // Navigation
  {
    keys: ['→', 'N'],
    description: 'Next item',
    icon: <NextIcon />,
    category: 'Navigation',
  },
  {
    keys: ['←', 'P'],
    description: 'Previous item',
    icon: <PrevIcon />,
    category: 'Navigation',
  },
  
  // View Controls
  {
    keys: ['D'],
    description: 'Toggle differences highlighting',
    icon: <ViewIcon />,
    category: 'View',
  },
  {
    keys: ['M'],
    description: 'Toggle SER metrics panel',
    icon: <MetricsIcon />,
    category: 'View',
  },
  {
    keys: ['F'],
    description: 'Toggle fullscreen mode',
    icon: <FullscreenIcon />,
    category: 'View',
  },
  
  // Feedback
  {
    keys: ['1', '2', '3', '4', '5'],
    description: 'Set rating (1-5 stars)',
    category: 'Feedback',
  },
  {
    keys: ['Ctrl', 'Enter'],
    description: 'Submit feedback and advance',
    icon: <SaveIcon />,
    category: 'Feedback',
  },
  {
    keys: ['Ctrl', 'S'],
    description: 'Save current feedback',
    icon: <SaveIcon />,
    category: 'Feedback',
  },
  
  // General
  {
    keys: ['?'],
    description: 'Show this help dialog',
    icon: <HelpIcon />,
    category: 'General',
  },
  {
    keys: ['Esc'],
    description: 'Close dialogs/cancel actions',
    category: 'General',
  },
];

const KeyShortcut: React.FC<{ keys: string[] }> = ({ keys }) => (
  <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
    {keys.map((key, index) => (
      <React.Fragment key={key}>
        {index > 0 && (
          <Typography variant="caption" color="text.secondary" sx={{ mx: 0.5 }}>
            +
          </Typography>
        )}
        <Chip
          label={key}
          size="small"
          variant="outlined"
          sx={{
            fontFamily: 'monospace',
            fontSize: '0.75rem',
            height: 24,
            minWidth: 24,
            '& .MuiChip-label': {
              px: 1,
            },
          }}
        />
      </React.Fragment>
    ))}
  </Box>
);

export const KeyboardShortcutsHelper: React.FC<KeyboardShortcutsHelperProps> = ({
  open,
  onClose,
}) => {
  const categories = Array.from(new Set(shortcuts.map(s => s.category)));

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { maxHeight: '80vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <KeyboardIcon color="primary" />
            <Typography variant="h6">Keyboard Shortcuts</Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Use these keyboard shortcuts to navigate and interact with the MT validation interface more efficiently.
        </Typography>

        {categories.map((category, categoryIndex) => (
          <Box key={category} sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom color="primary">
              {category}
            </Typography>
            
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Grid container spacing={2}>
                  {shortcuts
                    .filter(shortcut => shortcut.category === category)
                    .map((shortcut, index) => (
                      <Grid item xs={12} key={index}>
                        <Box sx={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'space-between',
                          py: 1,
                          borderBottom: index < shortcuts.filter(s => s.category === category).length - 1 
                            ? '1px solid' 
                            : 'none',
                          borderColor: 'divider',
                        }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            {shortcut.icon && (
                              <Box sx={{ color: 'text.secondary' }}>
                                {shortcut.icon}
                              </Box>
                            )}
                            <Typography variant="body2">
                              {shortcut.description}
                            </Typography>
                          </Box>
                          <KeyShortcut keys={shortcut.keys} />
                        </Box>
                      </Grid>
                    ))}
                </Grid>
              </CardContent>
            </Card>
          </Box>
        ))}

        <Divider sx={{ my: 3 }} />

        {/* Tips */}
        <Box>
          <Typography variant="h6" gutterBottom color="primary">
            Tips
          </Typography>
          <Card variant="outlined" sx={{ backgroundColor: 'background.default' }}>
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="body2">
                  • Keyboard shortcuts work when not typing in text fields
                </Typography>
                <Typography variant="body2">
                  • Use Tab to navigate between form fields
                </Typography>
                <Typography variant="body2">
                  • Press Escape to cancel any ongoing action
                </Typography>
                <Typography variant="body2">
                  • Shortcuts are case-insensitive (N and n both work)
                </Typography>
                <Typography variant="body2">
                  • Hold Shift with navigation keys for bulk selection
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Browser Compatibility */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="caption" color="text.secondary">
            <strong>Note:</strong> Some shortcuts may conflict with browser shortcuts. 
            Use F11 for browser fullscreen if F key doesn't work for application fullscreen.
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} variant="contained">
          Got it
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KeyboardShortcutsHelper;

/**
 * Bucket Progression Notification Component
 * Displays notifications when a speaker's bucket level changes
 */

import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Chip,
  Typography,
  Slide,
  IconButton,
  useTheme
} from '@mui/material';
import {
  TrendingUp as PromotionIcon,
  TrendingDown as DemotionIcon,
  Close as CloseIcon,
  EmojiEvents as TrophyIcon
} from '@mui/icons-material';
import type { BucketType, BucketProgressionNotification } from '@domain/types';
import { bucketProgressionHelpers } from '@infrastructure/services/speakerProfileService';

interface BucketProgressionNotificationProps {
  notification: BucketProgressionNotification;
  open: boolean;
  onClose: () => void;
  autoHideDuration?: number;
}

export const BucketProgressionNotificationComponent: React.FC<BucketProgressionNotificationProps> = ({
  notification,
  open,
  onClose,
  autoHideDuration = 8000
}) => {
  const theme = useTheme();
  const isPromotion = notification.type === 'promotion';
  
  // Auto-hide notification
  React.useEffect(() => {
    if (open && autoHideDuration > 0) {
      const timer = setTimeout(onClose, autoHideDuration);
      return () => clearTimeout(timer);
    }
  }, [open, autoHideDuration, onClose]);

  const getNotificationIcon = () => {
    if (isPromotion) {
      return notification.new_bucket === 'expert' ? <TrophyIcon /> : <PromotionIcon />;
    }
    return <DemotionIcon />;
  };

  const getNotificationColor = () => {
    return isPromotion ? 'success' : 'warning';
  };

  const getNotificationTitle = () => {
    if (isPromotion) {
      return notification.new_bucket === 'expert' 
        ? '🎉 Congratulations! Expert Level Achieved!' 
        : '🎉 Bucket Level Promotion!';
    }
    return '📊 Bucket Level Update';
  };

  const formatMessage = () => {
    return bucketProgressionHelpers.formatProgressionMessage(
      notification.old_bucket,
      notification.new_bucket,
      notification.reason
    );
  };

  return (
    <Slide direction="down" in={open} mountOnEnter unmountOnExit>
      <Alert
        severity={getNotificationColor()}
        icon={getNotificationIcon()}
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={onClose}
          >
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }
        sx={{
          position: 'fixed',
          top: 24,
          right: 24,
          zIndex: theme.zIndex.snackbar,
          minWidth: 400,
          maxWidth: 600,
          boxShadow: theme.shadows[8],
          '& .MuiAlert-message': {
            width: '100%'
          }
        }}
      >
        <AlertTitle sx={{ fontWeight: 'bold', mb: 1 }}>
          {getNotificationTitle()}
        </AlertTitle>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            {formatMessage()}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
              From:
            </Typography>
            <Chip
              label={`${bucketProgressionHelpers.getBucketIcon(notification.old_bucket)} ${bucketProgressionHelpers.getBucketDisplayName(notification.old_bucket)}`}
              size="small"
              variant="outlined"
              sx={{ 
                borderColor: bucketProgressionHelpers.getBucketColor(notification.old_bucket),
                color: bucketProgressionHelpers.getBucketColor(notification.old_bucket)
              }}
            />
          </Box>
          
          <Typography variant="caption" color="text.secondary">
            →
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
              To:
            </Typography>
            <Chip
              label={`${bucketProgressionHelpers.getBucketIcon(notification.new_bucket)} ${bucketProgressionHelpers.getBucketDisplayName(notification.new_bucket)}`}
              size="small"
              variant="filled"
              sx={{ 
                backgroundColor: bucketProgressionHelpers.getBucketColor(notification.new_bucket),
                color: 'white',
                fontWeight: 'bold'
              }}
            />
          </Box>
        </Box>

        {isPromotion && (
          <Box sx={{ mt: 2, p: 1, backgroundColor: 'success.light', borderRadius: 1, opacity: 0.1 }}>
            <Typography variant="caption" color="success.dark" sx={{ fontStyle: 'italic' }}>
              Keep up the excellent work! Your consistent improvement has been recognized.
            </Typography>
          </Box>
        )}
      </Alert>
    </Slide>
  );
};

// Hook for managing bucket progression notifications
export const useBucketProgressionNotifications = () => {
  const [notifications, setNotifications] = React.useState<Array<BucketProgressionNotification & { id: string; open: boolean }>>([]);

  const addNotification = React.useCallback((notification: BucketProgressionNotification) => {
    const id = `${notification.timestamp}-${Math.random()}`;
    setNotifications(prev => [...prev, { ...notification, id, open: true }]);
  }, []);

  const removeNotification = React.useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const closeNotification = React.useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, open: false } : n)
    );
    // Remove after animation completes
    setTimeout(() => removeNotification(id), 300);
  }, [removeNotification]);

  const clearAllNotifications = React.useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    addNotification,
    removeNotification,
    closeNotification,
    clearAllNotifications
  };
};

// Notification container component
export const BucketProgressionNotifications: React.FC = () => {
  const { notifications, closeNotification } = useBucketProgressionNotifications();

  return (
    <>
      {notifications.map((notification) => (
        <BucketProgressionNotificationComponent
          key={notification.id}
          notification={notification}
          open={notification.open}
          onClose={() => closeNotification(notification.id)}
        />
      ))}
    </>
  );
};

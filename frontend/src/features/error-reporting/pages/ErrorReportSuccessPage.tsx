/**
 * Error Report Success Page
 * Displays confirmation after successful error report submission
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Grid,
  Chip,
  Divider,
  Alert,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Dashboard as DashboardIcon,
  Assignment as ReportsIcon,
  Add as NewReportIcon,
  Email as EmailIcon,
  Schedule as ScheduleIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface SuccessPageState {
  reportId: string;
  submissionTime: string;
  speakerId: string;
  clientId: string;
  jobId: string;
}

const ErrorReportSuccessPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Get data from navigation state
  const state = location.state as SuccessPageState | null;
  
  // Fallback data if state is not available
  const reportData = state || {
    reportId: 'ER-' + Date.now(),
    submissionTime: new Date().toLocaleString(),
    speakerId: 'Unknown',
    clientId: 'Unknown',
    jobId: 'Unknown',
  };

  const handleViewReports = () => {
    navigate('/reports');
  };

  const handleNewReport = () => {
    navigate('/error-reporting');
  };

  const handleDashboard = () => {
    navigate('/dashboard');
  };

  const handleUpdateEmailPreferences = () => {
    navigate('/profile/notifications');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Success Header */}
      <Paper
        elevation={0}
        sx={{
          p: 4,
          mb: 4,
          textAlign: 'center',
          background: `linear-gradient(135deg, ${theme.palette.success.light}20, ${theme.palette.success.main}10)`,
          border: `2px solid ${theme.palette.success.main}`,
          borderRadius: 2,
        }}
      >
        <SuccessIcon
          sx={{
            fontSize: 64,
            color: 'success.main',
            mb: 2,
          }}
        />
        <Typography variant="h3" component="h1" gutterBottom color="success.main">
          Error Report Submitted Successfully!
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Thank you for helping improve our ASR system accuracy!
        </Typography>
      </Paper>

      <Grid container spacing={4}>
        {/* Report Details */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <InfoIcon color="primary" />
              Report Details
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Report ID
              </Typography>
              <Typography variant="h6" sx={{ fontFamily: 'monospace' }}>
                {reportData.reportId}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Submission Time
              </Typography>
              <Typography variant="body1">
                {reportData.submissionTime}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Status
              </Typography>
              <Chip
                label="Submitted for Review"
                color="warning"
                variant="outlined"
                size="small"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Estimated Processing Time
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ScheduleIcon fontSize="small" color="action" />
                <Typography variant="body1">
                  2-3 business days
                </Typography>
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Associated IDs
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip label={`Job: ${reportData.jobId}`} size="small" variant="outlined" />
              <Chip label={`Speaker: ${reportData.speakerId}`} size="small" variant="outlined" />
              <Chip label={`Client: ${reportData.clientId}`} size="small" variant="outlined" />
            </Box>
          </Paper>
        </Grid>

        {/* What Happens Next */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ScheduleIcon color="primary" />
              What Happens Next
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box component="ol" sx={{ pl: 2, '& li': { mb: 1.5 } }}>
              <li>
                <Typography variant="body1">
                  <strong>Quality Review:</strong> Our QA team will review your report for accuracy and completeness
                </Typography>
              </li>
              <li>
                <Typography variant="body1">
                  <strong>Validation:</strong> The correction will be validated against our language models
                </Typography>
              </li>
              <li>
                <Typography variant="body1">
                  <strong>Integration:</strong> Approved corrections will be integrated into our ASR system
                </Typography>
              </li>
              <li>
                <Typography variant="body1">
                  <strong>Notification:</strong> You'll receive an email when processing is complete
                </Typography>
              </li>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Your contribution helps improve accuracy for all users of our transcription system.
              </Typography>
            </Alert>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Next Actions
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<ReportsIcon />}
                  onClick={handleViewReports}
                  sx={{ py: 1.5 }}
                >
                  View My Reports
                </Button>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<NewReportIcon />}
                  onClick={handleNewReport}
                  sx={{ py: 1.5 }}
                >
                  Submit Another Report
                </Button>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<DashboardIcon />}
                  onClick={handleDashboard}
                  sx={{ py: 1.5 }}
                >
                  Return to Dashboard
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Additional Information */}
        <Grid item xs={12}>
          <Paper elevation={1} sx={{ p: 3, bgcolor: 'grey.50' }}>
            <Typography variant="h6" gutterBottom>
              💡 Helpful Tips
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" paragraph>
                  <strong>Track Your Reports:</strong> You can monitor the status of all your submissions 
                  in the "My Reports" section of your dashboard.
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <EmailIcon fontSize="small" color="action" />
                  <Typography variant="body2">
                    <strong>Email Notifications:</strong> admin@example.com
                  </Typography>
                </Box>
                <Button
                  size="small"
                  variant="text"
                  onClick={handleUpdateEmailPreferences}
                  sx={{ textTransform: 'none' }}
                >
                  Update Email Preferences
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ErrorReportSuccessPage;

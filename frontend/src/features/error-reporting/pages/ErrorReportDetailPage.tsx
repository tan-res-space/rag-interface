/**
 * Error Report Detail Page
 * Displays detailed view of a specific error report
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  Divider,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Skeleton,
  Alert,
  Breadcrumbs,
  Link,
  useTheme,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Person as PersonIcon,
  Business as ClientIcon,
  Schedule as TimeIcon,
  Category as CategoryIcon,
  Priority as PriorityIcon,
  Description as TextIcon,
  Edit as EditIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useGetErrorReportQuery } from '@infrastructure/api/error-report-api';

// Status color mapping (same as list page)
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'warning';
    case 'processed':
      return 'success';
    case 'archived':
      return 'default';
    case 'rejected':
      return 'error';
    default:
      return 'default';
  }
};

const getStatusDisplay = (status: string) => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'Under Review';
    case 'processed':
      return 'Completed';
    case 'archived':
      return 'Archived';
    case 'rejected':
      return 'Rejected';
    default:
      return status;
  }
};

const ErrorReportDetailPage: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const navigate = useNavigate();
  const theme = useTheme();

  // API query
  const {
    data: report,
    isLoading,
    isError,
    error,
  } = useGetErrorReportQuery(reportId!);

  const handleBack = () => {
    navigate('/reports');
  };

  const handleEdit = () => {
    // TODO: Implement edit functionality
    console.log('Edit report:', reportId);
  };

  const handleDownload = () => {
    // TODO: Implement download functionality
    console.log('Download report:', reportId);
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Skeleton variant="text" width={300} height={40} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={200} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={300} />
      </Container>
    );
  }

  if (isError || !report) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error && 'message' in error 
            ? error.message 
            : 'Failed to load error report. The report may not exist or you may not have permission to view it.'
          }
        </Alert>
        <Button startIcon={<BackIcon />} onClick={handleBack}>
          Back to Reports
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component="button"
          variant="body1"
          onClick={handleBack}
          sx={{ textDecoration: 'none' }}
        >
          My Reports
        </Link>
        <Typography color="text.primary">Report Details</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h3" component="h1" gutterBottom>
            Error Report Details
          </Typography>
          <Typography variant="h6" sx={{ fontFamily: 'monospace', color: 'text.secondary' }}>
            {report.id}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            startIcon={<BackIcon />}
            onClick={handleBack}
            variant="outlined"
          >
            Back
          </Button>
          <Button
            startIcon={<EditIcon />}
            onClick={handleEdit}
            variant="outlined"
            disabled={report.status === 'processed' || report.status === 'archived'}
          >
            Edit
          </Button>
          <Button
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
            variant="outlined"
          >
            Download
          </Button>
        </Box>
      </Box>

      <Grid container spacing={4}>
        {/* Status and Basic Info */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Report Status
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Chip
                  label={getStatusDisplay(report.status)}
                  color={getStatusColor(report.status) as any}
                  size="large"
                  sx={{ fontSize: '1rem', py: 2 }}
                />
              </Box>

              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <TimeIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Submitted"
                    secondary={new Date(report.created_at).toLocaleString()}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <TimeIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Last Updated"
                    secondary={new Date(report.updated_at).toLocaleString()}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <PersonIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Speaker ID"
                    secondary={report.speaker_id}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <ClientIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Client ID"
                    secondary={report.client_id}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <PriorityIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Severity"
                    secondary={report.severity_level}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Text Content */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TextIcon />
              Text Comparison
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom color="error">
                  Original Text (Error)
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    backgroundColor: theme.palette.error.light + '10',
                    border: `1px solid ${theme.palette.error.light}`,
                    minHeight: 120,
                  }}
                >
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {report.original_text}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom color="success.main">
                  Corrected Text
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    backgroundColor: theme.palette.success.light + '10',
                    border: `1px solid ${theme.palette.success.light}`,
                    minHeight: 120,
                  }}
                >
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {report.corrected_text}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle1" gutterBottom>
              Error Position
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Characters {report.start_position} to {report.end_position} (Length: {report.end_position - report.start_position})
            </Typography>
          </Paper>

          {/* Categories and Metadata */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CategoryIcon />
              Categories & Metadata
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Error Categories
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {report.error_categories.map((category, index) => (
                  <Chip
                    key={index}
                    label={category}
                    variant="outlined"
                    color="primary"
                  />
                ))}
              </Box>
            </Box>

            {report.context_notes && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Context Notes
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {report.context_notes}
                </Typography>
              </Box>
            )}

            {report.metadata && Object.keys(report.metadata).length > 0 && (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Additional Metadata
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'grey.50' }}>
                  <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                    {JSON.stringify(report.metadata, null, 2)}
                  </pre>
                </Paper>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ErrorReportDetailPage;

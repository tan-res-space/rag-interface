/**
 * Verification Workflow Interface Component
 * 
 * Provides interface for managing verification jobs, applying RAG corrections,
 * and verifying correction results.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';

interface VerificationJob {
  verificationId: string;
  jobId: string;
  speakerId: string;
  verificationStatus: 'pending' | 'verified' | 'not_rectified' | 'partially_rectified';
  verificationResult?: 'rectified' | 'not_rectified' | 'partially_rectified' | 'not_applicable';
  correctionsCount: number;
  averageConfidence: number;
  needsManualReview: boolean;
  verifiedBy?: string;
  verifiedAt?: string;
  hasQaComments: boolean;
}

interface CorrectionApplied {
  correctionType: string;
  originalText: string;
  correctedText: string;
  confidence: number;
  positionStart?: number;
  positionEnd?: number;
}

interface VerificationJobDetails extends VerificationJob {
  originalDraft: string;
  ragCorrectedDraft?: string;
  correctionsApplied: CorrectionApplied[];
  qaComments?: string;
}

interface VerificationWorkflowInterfaceProps {
  jobs: VerificationJob[];
  onPullJobs: (speakerId: string, dateRange: { startDate: string; endDate: string }) => void;
  onApplyCorrections: (verificationId: string) => void;
  onVerifyResult: (verificationId: string, result: string, comments?: string) => void;
  onGetJobDetails: (verificationId: string) => Promise<VerificationJobDetails>;
  loading?: boolean;
}

export const VerificationWorkflowInterface: React.FC<VerificationWorkflowInterfaceProps> = ({
  jobs,
  onPullJobs,
  onApplyCorrections,
  onVerifyResult,
  onGetJobDetails,
  loading = false,
}) => {
  const [pullDialogOpen, setPullDialogOpen] = useState(false);
  const [verifyDialogOpen, setVerifyDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<VerificationJob | null>(null);
  const [jobDetails, setJobDetails] = useState<VerificationJobDetails | null>(null);
  const [speakerId, setSpeakerId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [verificationResult, setVerificationResult] = useState('');
  const [qaComments, setQaComments] = useState('');
  const [processingJobs, setProcessingJobs] = useState<Set<string>>(new Set());

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'success';
      case 'pending':
        return 'warning';
      case 'not_rectified':
        return 'error';
      case 'partially_rectified':
        return 'info';
      default:
        return 'default';
    }
  };

  const getResultColor = (result?: string) => {
    switch (result) {
      case 'rectified':
        return 'success';
      case 'not_rectified':
        return 'error';
      case 'partially_rectified':
        return 'warning';
      case 'not_applicable':
        return 'info';
      default:
        return 'default';
    }
  };

  const handlePullJobs = () => {
    if (speakerId && startDate && endDate) {
      onPullJobs(speakerId, { startDate, endDate });
      setPullDialogOpen(false);
      setSpeakerId('');
      setStartDate('');
      setEndDate('');
    }
  };

  const handleApplyCorrections = async (verificationId: string) => {
    setProcessingJobs(prev => new Set(prev).add(verificationId));
    try {
      await onApplyCorrections(verificationId);
    } finally {
      setProcessingJobs(prev => {
        const newSet = new Set(prev);
        newSet.delete(verificationId);
        return newSet;
      });
    }
  };

  const handleVerifyResult = () => {
    if (selectedJob && verificationResult) {
      onVerifyResult(selectedJob.verificationId, verificationResult, qaComments);
      setVerifyDialogOpen(false);
      setSelectedJob(null);
      setVerificationResult('');
      setQaComments('');
    }
  };

  const handleViewDetails = async (job: VerificationJob) => {
    setSelectedJob(job);
    try {
      const details = await onGetJobDetails(job.verificationId);
      setJobDetails(details);
      setDetailsDialogOpen(true);
    } catch (error) {
      console.error('Failed to load job details:', error);
    }
  };

  const openVerifyDialog = (job: VerificationJob) => {
    setSelectedJob(job);
    setVerifyDialogOpen(true);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const pendingJobs = jobs.filter(job => job.verificationStatus === 'pending');
  const reviewJobs = jobs.filter(job => job.needsManualReview);
  const completedJobs = jobs.filter(job => job.verificationStatus === 'verified');

  return (
    <Box>
      {/* Header Actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Verification Workflow</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => window.location.reload()}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => setPullDialogOpen(true)}
          >
            Pull Jobs
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="warning.main">
                Pending Jobs
              </Typography>
              <Typography variant="h3">
                {pendingJobs.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="error.main">
                Need Review
              </Typography>
              <Typography variant="h3">
                {reviewJobs.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                Completed
              </Typography>
              <Typography variant="h3">
                {completedJobs.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Total Jobs
              </Typography>
              <Typography variant="h3">
                {jobs.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Jobs Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Verification Jobs
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Job ID</TableCell>
                  <TableCell>Speaker</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Result</TableCell>
                  <TableCell>Corrections</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Review</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {jobs.map((job) => (
                  <TableRow key={job.verificationId}>
                    <TableCell>{job.jobId}</TableCell>
                    <TableCell>{job.speakerId}</TableCell>
                    <TableCell>
                      <Chip
                        label={job.verificationStatus}
                        color={getStatusColor(job.verificationStatus) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {job.verificationResult ? (
                        <Chip
                          label={job.verificationResult}
                          color={getResultColor(job.verificationResult) as any}
                          size="small"
                        />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>{job.correctionsCount}</TableCell>
                    <TableCell>
                      {job.averageConfidence > 0 ? 
                        `${(job.averageConfidence * 100).toFixed(0)}%` : 
                        '-'
                      }
                    </TableCell>
                    <TableCell>
                      {job.needsManualReview && (
                        <Chip
                          label="Review Required"
                          color="warning"
                          size="small"
                          icon={<WarningIcon />}
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        {job.verificationStatus === 'pending' && (
                          <Tooltip title="Apply RAG Corrections">
                            <IconButton
                              size="small"
                              onClick={() => handleApplyCorrections(job.verificationId)}
                              disabled={processingJobs.has(job.verificationId)}
                            >
                              <PlayArrowIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        {job.correctionsCount > 0 && job.verificationStatus !== 'verified' && (
                          <Tooltip title="Verify Result">
                            <IconButton
                              size="small"
                              onClick={() => openVerifyDialog(job)}
                            >
                              <CheckCircleIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(job)}
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Pull Jobs Dialog */}
      <Dialog open={pullDialogOpen} onClose={() => setPullDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Pull Verification Jobs</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Speaker ID"
              value={speakerId}
              onChange={(e) => setSpeakerId(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPullDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handlePullJobs}
            variant="contained"
            disabled={!speakerId || !startDate || !endDate}
          >
            Pull Jobs
          </Button>
        </DialogActions>
      </Dialog>

      {/* Verify Result Dialog */}
      <Dialog open={verifyDialogOpen} onClose={() => setVerifyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Verify Correction Result</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Verification Result</InputLabel>
              <Select
                value={verificationResult}
                onChange={(e) => setVerificationResult(e.target.value)}
                label="Verification Result"
              >
                <MenuItem value="rectified">Rectified</MenuItem>
                <MenuItem value="not_rectified">Not Rectified</MenuItem>
                <MenuItem value="partially_rectified">Partially Rectified</MenuItem>
                <MenuItem value="not_applicable">Not Applicable</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              multiline
              rows={3}
              label="QA Comments"
              value={qaComments}
              onChange={(e) => setQaComments(e.target.value)}
              placeholder="Add any comments about the verification..."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerifyDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleVerifyResult}
            variant="contained"
            disabled={!verificationResult}
          >
            Verify
          </Button>
        </DialogActions>
      </Dialog>

      {/* Job Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Verification Job Details</DialogTitle>
        <DialogContent>
          {jobDetails && (
            <Box sx={{ pt: 1 }}>
              <Grid container spacing={2} mb={3}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Job ID:</Typography>
                  <Typography variant="body2">{jobDetails.jobId}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Speaker ID:</Typography>
                  <Typography variant="body2">{jobDetails.speakerId}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Status:</Typography>
                  <Chip
                    label={jobDetails.verificationStatus}
                    color={getStatusColor(jobDetails.verificationStatus) as any}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Corrections Applied:</Typography>
                  <Typography variant="body2">{jobDetails.correctionsCount}</Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Original Draft</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                    <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                      {jobDetails.originalDraft}
                    </Typography>
                  </Paper>
                </AccordionDetails>
              </Accordion>

              {jobDetails.ragCorrectedDraft && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">RAG Corrected Draft</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Paper sx={{ p: 2, backgroundColor: 'success.50' }}>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                        {jobDetails.ragCorrectedDraft}
                      </Typography>
                    </Paper>
                  </AccordionDetails>
                </Accordion>
              )}

              {jobDetails.correctionsApplied.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">Corrections Applied ({jobDetails.correctionsApplied.length})</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Type</TableCell>
                            <TableCell>Original</TableCell>
                            <TableCell>Corrected</TableCell>
                            <TableCell>Confidence</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {jobDetails.correctionsApplied.map((correction, index) => (
                            <TableRow key={index}>
                              <TableCell>{correction.correctionType}</TableCell>
                              <TableCell>{correction.originalText}</TableCell>
                              <TableCell>{correction.correctedText}</TableCell>
                              <TableCell>{(correction.confidence * 100).toFixed(0)}%</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </AccordionDetails>
                </Accordion>
              )}

              {jobDetails.qaComments && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>QA Comments:</Typography>
                  <Paper sx={{ p: 2, backgroundColor: 'info.50' }}>
                    <Typography variant="body2">{jobDetails.qaComments}</Typography>
                  </Paper>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

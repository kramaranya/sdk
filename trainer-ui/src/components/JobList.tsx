import React, { useEffect, useState } from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableRow,
  Button,
  Chip,
  IconButton,
  Typography,
  Paper,
  CircularProgress
} from '@material-ui/core';
import { Refresh, Delete, Visibility } from '@material-ui/icons';
import { ToolbarProps } from './Toolbar';

interface Job {
  name: string;
  status: string;
  runtime: string;
  created_at: string | null;
  containers: Array<{
    name: string;
    status: string;
  }>;
}

interface JobListResponse {
  jobs: Job[];
  total: number;
  timestamp: string;
}

interface JobListProps {
  updateToolbar: (props: Partial<ToolbarProps>) => void;
}

const API_BASE_URL = 'http://localhost:8000/api';

const JobList: React.FC<JobListProps> = ({ updateToolbar }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: JobListResponse = await response.json();
      setJobs(data.jobs);
      setLastUpdate(new Date(data.timestamp).toLocaleTimeString());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };

  const deleteJob = async (jobName: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobName}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // Refresh the job list after deletion
      fetchJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete job');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
        return 'primary';
      case 'succeeded':
        return 'default';
      case 'failed':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Invalid Date';
    }
  };

  useEffect(() => {
    updateToolbar({
      actions: {
        refresh: {
          title: 'Refresh Jobs',
          tooltip: 'Refresh job list',
          icon: Refresh,
          action: fetchJobs,
        },
      },
      breadcrumbs: [],
      pageTitle: 'Training Jobs',
    });

    // Initial fetch
    fetchJobs();

    // Set up polling for real-time updates every 5 seconds
    const interval = setInterval(fetchJobs, 5000);

    return () => clearInterval(interval);
  }, [updateToolbar]);

  if (loading && jobs.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
        <CircularProgress />
        <Typography variant="body2" style={{ marginLeft: 16 }}>
          Loading training jobs...
        </Typography>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography variant="h4">Training Jobs</Typography>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {lastUpdate && (
            <Typography variant="body2" color="textSecondary">
              Last updated: {lastUpdate}
            </Typography>
          )}
          <IconButton onClick={fetchJobs} disabled={loading}>
            <Refresh />
          </IconButton>
        </div>
      </div>

      {error && (
        <Paper style={{ padding: 16, marginBottom: 16, backgroundColor: '#ffebee' }}>
          <Typography color="error">
            Error: {error}
          </Typography>
        </Paper>
      )}

      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Job Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Runtime</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Containers</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="textSecondary">
                    No training jobs found. Create a job using the Trainer SDK to see it here.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              jobs.map((job) => (
                <TableRow key={job.name}>
                  <TableCell>
                    <Typography variant="body2" component="div">
                      {job.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={job.status}
                      color={getStatusColor(job.status) as any}
                    />
                  </TableCell>
                  <TableCell>{job.runtime || 'Unknown'}</TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(job.created_at)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {job.containers?.length || 0} containers
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <IconButton
                        onClick={() => {
                          // TODO: Navigate to job details
                          console.log('View job:', job.name);
                        }}
                        title="View Details"
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton
                        onClick={() => deleteJob(job.name)}
                        title="Delete Job"
                        style={{ color: '#f44336' }}
                      >
                        <Delete />
                      </IconButton>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Paper>

      <div style={{ marginTop: 16 }}>
        <Typography variant="body2" color="textSecondary">
          Total: {jobs.length} jobs • Updates automatically every 5 seconds
        </Typography>
      </div>
    </div>
  );
};

export default JobList; 